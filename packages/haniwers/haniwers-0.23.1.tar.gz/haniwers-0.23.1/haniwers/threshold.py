"""スレッショルド測定

スレッショルド値を変化させて測定し、
スレッショルド値に対するイベント数のSカーブを取得します。
このSカーブを誤差補正関数でフィットし、最適なスレッショルド値を推定します。

- チャンネルを選択
- スレッショルドを設定
- DAQを実行

"""

import csv
from pathlib import Path

import numpy as np
import pandas as pd
import pendulum
from datetime import datetime

from loguru import logger
from scipy.optimize import curve_fit
from scipy.special import erfc
from pydantic import BaseModel

from .config import Daq
from .daq import (
    events_to_dataframe,
    get_savef_with_timestamp,
    mkdir_saved,
    scan_daq,
    set_vth_retry,
)


class Count(BaseModel):
    """スレッショルドごとのカウント数"""

    timestamp: datetime = pendulum.now()
    duration: int = 0
    ch: int = 0
    vth: int = 0
    counts: int = 0
    hit_top: int = 0
    hit_mid: int = 0
    hit_btm: int = 0
    tmp: float = 0
    atm: float = 0
    hmd: float = 0

    def to_list_string(self) -> list[str]:
        """List

        メンバー変数を文字列にしたリストに変換します。

        ```python
        >>> count = Count()
        >>> count.to_list_string()
        ['2024-06-02 08:44:20.389786+09:00', '0', '0', '0', '0', '0', '0', '0', '0', '0', '0']
        ```
        """
        data = self.model_dump()
        values = [str(v) for v in data.values()]
        return values


def get_count(data: pd.DataFrame):
    """スレッショルド測定の結果を処理して保存する"""
    count = Count()

    if data.empty:
        return count

    count.counts = len(data)
    count.hit_top = int(data["hit_top"].sum())
    count.hit_mid = int(data["hit_mid"].sum())
    count.hit_btm = int(data["hit_btm"].sum())
    count.tmp = float(data["tmp"].mean())
    count.atm = float(data["atm"].mean())
    count.hmd = float(data["hmd"].mean())

    logger.debug(count)
    logger.debug(f"{count.counts=}")
    logger.debug(f"{count.hit_top=}")
    logger.debug(f"{count.hit_mid=}")
    logger.debug(f"{count.hit_btm=}")
    logger.debug(f"{count.tmp=}")
    logger.debug(f"{count.atm=}")
    logger.debug(f"{count.hmd=}")

    return count


def write_count(count: Count, fname: Path):
    row = count
    with fname.open("a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row.to_list_string())
        msg = f"Added data to: {fname}"
        logger.success(msg)


def get_data(daq: Daq, duration: int, ch: int, vth: int) -> Count:
    """スレッショルド測定"""
    try:
        # fidは7ケタまで使える
        fid = f"{ch:02}_{vth:04}"
        fname = get_savef_with_timestamp(daq, fid)
        events = scan_daq(daq, str(fname), duration)
        data = events_to_dataframe(events)
    except Exception as e:
        data = pd.DataFrame()
        msg = f"Failed to collect data due to: {str(e)}"
        logger.error(msg)

    # Save Summary
    row = get_count(data)
    now = pendulum.now()
    row.timestamp = now
    row.duration = duration
    row.ch = ch
    row.vth = vth

    return row


def scan_threshold_by_channel(daq: Daq, duration: int, ch: int, vth: int) -> Count:
    """スレッショルド測定（チャンネル指定）

    チャンネルを指定してスレッショルド測定します。

    :Args:
    - `daq (Daq)`: Daqオブジェクトを指定する
    - `duration (int)`: 測定時間（秒）を指定する
    - `ch (int)`: 測定するチャンネル番号を指定する
    - `vth (int)`: スレッショルド値を指定する

    :Returns:
    - `data (list)`: [測定時刻, チャンネル番号, スレッショルド値, イベント数, 気温など]のリスト
    """

    # Try to set the threshold
    if not set_vth_retry(daq, ch, vth, 3):
        msg = f"Failed to set threshold: ch{ch} - {vth}"
        logger.error(msg)
        return []

    # スレッショルド測定を実行
    row = get_data(daq, duration, ch, vth)
    fname = Path(daq.saved) / daq.fname_scan
    write_count(row, fname)
    return row


def scan_thresholds_in_serial(
    daq: Daq, duration: int, ch: int, thresholds: list[int]
) -> list[list]:
    """
    Run threshold scan for all channels by default.

    :Args:
    - daq (Daq): Daqオブジェクト
    - duration (int): 測定時間（秒）
    - ch (int): チャンネル番号（1 - 3)
    - thresholds (list[int])： 測定するスレッショルド値のリスト

    :Returns:
    - rows (list[list]):  [測定時刻、チャンネル番号、スレッショルド値、イベント数]のリスト
    """

    # Estimated time for scan
    msg = f"Number of points: {len(thresholds)}"
    logger.info(msg)
    estimated_time = len(thresholds) * duration
    msg = f"Estimated time: {estimated_time} sec."
    logger.info(msg)

    # すべてのチャンネルの閾値を高くする
    set_vth_retry(daq, 1, 500, 5)
    set_vth_retry(daq, 2, 500, 5)
    set_vth_retry(daq, 3, 500, 5)

    rows = []
    n = len(thresholds)
    for i, vth in enumerate(thresholds):
        msg = "-" * 40 + f"[{i + 1:2d}/{n:2d}: {vth}]"
        logger.info(msg)
        row = scan_threshold_by_channel(daq, duration, ch, vth)
        if row:
            rows.append(row)

    return rows


def scan_thresholds_in_parallel(daq: Daq, duration: int, thresholds: list[int]):
    mkdir_saved(daq)

    # Estimated time for scan
    msg = f"Number of points: {len(thresholds)}"
    logger.info(msg)
    estimated_time = len(thresholds) * duration
    msg = f"Estimated time: {estimated_time} sec."
    logger.info(msg)

    # チャンネルは0にする
    ch = 0

    n = len(thresholds)
    for i, vth in enumerate(thresholds):
        msg = "-" * 40 + f"[{i + 1:2d}/{n:2d}: {vth}]"
        logger.info(msg)

        # すべてのチャンネルの閾値を設定
        set_vth_retry(daq, 1, vth, 5)
        set_vth_retry(daq, 2, vth, 5)
        set_vth_retry(daq, 3, vth, 5)

        # スレッショルド測定を実行
        row = get_data(daq, duration, ch, vth)
        fname = Path(daq.saved) / daq.fname_scan
        write_count(row, fname)

    return row


def erfc_function(x, a, b, c, d):
    """
    誤差補正関数（Error function complement）。

    スレショルドを計算するためのフィット関数です。

    erfc(x) = 1 - erf(x)

    Parameters
    ----------
    x : input value
    a : height
    b : mean
    c : sigma
    d : intercept
    """
    return a * erfc((x - b) / c) + d


def fit_threshold_by_channel(data: pd.DataFrame, ch: int, func, params: list[float]):
    """誤差補正関数を使ってスレッショルド値を決める

    Args:
        data (pd.DataFrame): スレッショルド測定のデータフレーム
        ch (int): スレッショルドを求めるチャンネル番号
        func (_type_): フィット関数

    Returns:
        pd.DataFrame: 閾値の提案値のデータフレーム
        pd.DataFrame: フィットしたデータフレーム
        pd.DataFrame: フィット曲線のデータフレーム
    """

    # 実行した時刻を取得する
    now = pendulum.now()

    # データフレームのカラム名を確認する
    expected_names = ["time", "duration", "ch", "vth", "events", "tmp", "atm", "hmd"]
    names = list(data.columns)
    # assert names == expected_names

    # フィットの準備
    # 1. 該当するチャンネル番号のデータを抽出
    # 2. イベントレートの計算
    # 3. numpy配列に変換
    q = f"ch == {ch}"
    # print(f"----- Query: {q} -----")
    data_q = data.query(q).copy()
    data_q["event_rate"] = data_q["events"] / data_q["duration"]
    x_data = data_q["vth"]
    y_data = data_q["event_rate"]

    # フィットの初期パラメータ
    # TODO: 初期パラメータを外から調整できるようにする
    # params = [10.0, 300.0, 1.0, 1.0]

    # フィット：1回目
    popt, pcov = curve_fit(func, x_data, y_data, p0=params)
    # std = np.sqrt(np.diag(pcov))

    # logger.debug("フィット（1回目）")
    # logger.debug(f"Parameter Optimized  (popt) = {popt}")
    # logger.debug(f"Parameter Covariance (pcov) = {pcov}")
    # logger.debug(f"Parameter Std. Dev.  (std) = {std}")

    # フィット：2回目
    popt, pcov = curve_fit(func, x_data, y_data, p0=popt)
    # std = np.sqrt(np.diag(pcov))
    # logger.debug("フィット（2回目）")
    # logger.debug(f"Parameter Optimized  (popt) = {popt}")
    # logger.debug(f"Parameter Covariance (pcov) = {pcov}")
    # logger.debug(f"Parameter Std. Dev.  (std) = {std}")

    # フィット曲線
    # 1. フィットで得られた値を使って関数（numpy.array）を作成する
    # 2. データフレームに変換して返り値にする
    xmin = x_data.min()
    xmax = x_data.max()

    # logger.debug(xmin)
    # logger.debug(xmax)
    x_fit = np.arange(xmin, xmax, 0.1)
    a, b, c, d = popt
    y_fit = func(x_fit, a, b, c, d)
    data_f = pd.DataFrame(
        {
            "vth": x_fit,
            "event_rate": y_fit,
            "ch": f"fit{ch}",
        }
    )

    # フィット結果を使って閾値を計算する
    # 例：1sigma, 3sigma, 5sigma
    # pd.DataFrameに変換する
    mean, sigma = popt[1], popt[2]
    _thresholds = {
        "timestamp": now,
        "ch": ch,
        "0sigma": [round(mean)],
        "1sigma": [round(mean + 1 * sigma)],
        "3sigma": [round(mean + 3 * sigma)],
        "5sigma": [round(mean + 5 * sigma)],
    }
    thresholds = pd.DataFrame(_thresholds)

    return thresholds, data_q, data_f


def fit_thresholds(data: pd.DataFrame, channels: list[int], params: list[float]) -> pd.DataFrame:
    """スレッショルド

    Args:
        data (pd.DataFrame): スレッショルド測定のデータフレーム
        channels (list[int]): スレッショルドを計算するチャンネル番号

    Returns:
        pd.DataFrame: 計算したスレッショルド値のデータフレーム
    """
    threshold = []
    erfc = erfc_function
    for c in channels:
        _threshold, _, _ = fit_threshold_by_channel(data, ch=c, func=erfc, params=params)
        threshold.append(_threshold)

    thresholds = pd.concat(threshold, ignore_index=True)
    return thresholds
