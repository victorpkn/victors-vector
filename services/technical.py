import pandas as pd
from ta.trend import SMAIndicator, MACD
from ta.momentum import StochasticOscillator


def compute_indicators(df: pd.DataFrame, params: dict = None) -> dict:
    if params is None:
        params = {}

    close = df["Close"]
    high = df["High"]
    low = df["Low"]

    sma_short_w = params.get("sma_short", 20)
    sma_long_w = params.get("sma_long", 50)
    sma_short = SMAIndicator(close=close, window=sma_short_w).sma_indicator()
    sma_long = SMAIndicator(close=close, window=sma_long_w).sma_indicator()

    macd_fast = params.get("macd_fast", 12)
    macd_slow = params.get("macd_slow", 26)
    macd_sign = params.get("macd_signal", 9)
    macd_obj = MACD(close=close, window_slow=macd_slow, window_fast=macd_fast, window_sign=macd_sign)
    macd_line = macd_obj.macd()
    macd_signal = macd_obj.macd_signal()
    macd_hist = macd_obj.macd_diff()

    stoch_k_w = params.get("stoch_k", 14)
    stoch_smooth = params.get("stoch_smooth", 3)
    stoch_obj = StochasticOscillator(
        high=high, low=low, close=close,
        window=stoch_k_w, smooth_window=stoch_smooth
    )
    stoch_k = stoch_obj.stoch()
    stoch_d = stoch_obj.stoch_signal()

    dates = df["date"].dt.strftime("%Y-%m-%d")

    def to_series(series, date_series):
        result = []
        for d, v in zip(date_series, series):
            if pd.notna(v):
                result.append({"time": d, "value": round(v, 4)})
        return result

    def to_macd_series(macd_s, signal_s, hist_s, date_series):
        result = []
        for d, m, s, h in zip(date_series, macd_s, signal_s, hist_s):
            if pd.notna(m) and pd.notna(s) and pd.notna(h):
                result.append({
                    "time": d,
                    "macd": round(m, 4),
                    "signal": round(s, 4),
                    "histogram": round(h, 4),
                })
        return result

    def to_stoch_series(k_s, d_s, date_series):
        result = []
        for d, k, dv in zip(date_series, k_s, d_s):
            if pd.notna(k) and pd.notna(dv):
                result.append({
                    "time": d,
                    "k": round(k, 2),
                    "d": round(dv, 2),
                })
        return result

    return {
        "sma_short": to_series(sma_short, dates),
        "sma_long": to_series(sma_long, dates),
        "macd": to_macd_series(macd_line, macd_signal, macd_hist, dates),
        "stochastic": to_stoch_series(stoch_k, stoch_d, dates),
        "raw": {
            "sma_short": sma_short,
            "sma_long": sma_long,
            "macd_line": macd_line,
            "macd_signal": macd_signal,
            "macd_hist": macd_hist,
            "stoch_k": stoch_k,
            "stoch_d": stoch_d,
        },
    }
