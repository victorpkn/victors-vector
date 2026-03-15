import pandas as pd


def evaluate_signals(raw_indicators: dict, close_series: pd.Series,
                     params: dict = None) -> dict:
    if params is None:
        params = {}

    sma_short = raw_indicators["sma_short"]
    sma_long = raw_indicators["sma_long"]
    macd_line = raw_indicators["macd_line"]
    macd_signal = raw_indicators["macd_signal"]
    macd_hist = raw_indicators["macd_hist"]
    stoch_k = raw_indicators["stoch_k"]
    stoch_d = raw_indicators["stoch_d"]

    stoch_ob = params.get("stoch_ob", 80)
    stoch_os = params.get("stoch_os", 20)
    sma_short_w = params.get("sma_short", 20)
    sma_long_w = params.get("sma_long", 50)

    reasons = []

    sma_signal = _evaluate_sma(sma_short, sma_long, sma_short_w, sma_long_w)
    reasons.append(sma_signal)

    macd_sig = _evaluate_macd(macd_line, macd_signal, macd_hist)
    reasons.append(macd_sig)

    stoch_sig = _evaluate_stochastic(stoch_k, stoch_d, stoch_ob, stoch_os)
    reasons.append(stoch_sig)

    signal_map = {"BUY": 1, "HOLD": 0, "SELL": -1}
    score = sum(signal_map.get(r["signal"], 0) for r in reasons)

    if score >= 2:
        action = "BUY"
    elif score <= -2:
        action = "SELL"
    else:
        action = "HOLD"

    dates = close_series.index if hasattr(close_series.index, 'strftime') else None
    crossovers = _find_crossovers(sma_short, sma_long, macd_hist,
                                  stoch_k, stoch_d, stoch_ob, stoch_os,
                                  dates)

    return {
        "action": action,
        "score": score,
        "reasons": reasons,
        "crossovers": crossovers,
    }


def _evaluate_sma(sma_short: pd.Series, sma_long: pd.Series,
                  short_w: int = 20, long_w: int = 50) -> dict:
    latest_s = _last_valid(sma_short)
    latest_l = _last_valid(sma_long)
    prev_s = _nth_last_valid(sma_short, 2)
    prev_l = _nth_last_valid(sma_long, 2)

    vals = {}
    if latest_s is not None:
        vals["shortSma"] = round(float(latest_s), 2)
    if latest_l is not None:
        vals["longSma"] = round(float(latest_l), 2)
    if latest_s is not None and latest_l is not None and latest_l != 0:
        vals["spread"] = round((latest_s - latest_l) / latest_l * 100, 2)

    base = {"indicator": "SMA Crossover", "values": vals}

    if latest_s is None or latest_l is None:
        return {**base, "signal": "HOLD",
                "reason": f"Not enough data for SMA crossover",
                "brief": "Insufficient data"}

    if latest_s > latest_l and prev_s is not None and prev_l is not None and prev_s <= prev_l:
        return {**base, "signal": "BUY",
                "reason": f"SMA {short_w} just crossed above SMA {long_w} (Golden Cross) — bullish trend reversal",
                "brief": "Golden Cross"}
    elif latest_s < latest_l and prev_s is not None and prev_l is not None and prev_s >= prev_l:
        return {**base, "signal": "SELL",
                "reason": f"SMA {short_w} just crossed below SMA {long_w} (Death Cross) — bearish trend reversal",
                "brief": "Death Cross"}
    elif latest_s > latest_l:
        return {**base, "signal": "BUY",
                "reason": f"SMA {short_w} ({latest_s:.2f}) above SMA {long_w} ({latest_l:.2f}) — uptrend intact",
                "brief": "Uptrend intact"}
    elif latest_s < latest_l:
        return {**base, "signal": "SELL",
                "reason": f"SMA {short_w} ({latest_s:.2f}) below SMA {long_w} ({latest_l:.2f}) — downtrend",
                "brief": "Downtrend"}
    else:
        return {**base, "signal": "HOLD",
                "reason": f"SMA {short_w} and SMA {long_w} are converging",
                "brief": "Converging"}


def _evaluate_macd(macd_line: pd.Series, macd_signal: pd.Series,
                   macd_hist: pd.Series) -> dict:
    m = _last_valid(macd_line)
    s = _last_valid(macd_signal)
    h = _last_valid(macd_hist)
    prev_h = _nth_last_valid(macd_hist, 2)

    vals = {}
    if m is not None:
        vals["macd"] = round(float(m), 4)
    if s is not None:
        vals["signal"] = round(float(s), 4)
    if h is not None:
        vals["histogram"] = round(float(h), 4)

    base = {"indicator": "MACD", "values": vals}

    if m is None or s is None or h is None:
        return {**base, "signal": "HOLD",
                "reason": "Not enough data for MACD",
                "brief": "Insufficient data"}

    if m > s and h > 0:
        if prev_h is not None and prev_h <= 0:
            return {**base, "signal": "BUY",
                    "reason": "MACD crossed above signal — fresh bullish momentum",
                    "brief": "Bullish crossover"}
        return {**base, "signal": "BUY",
                "reason": f"MACD above signal with positive histogram — bullish",
                "brief": "Bullish momentum"}
    elif m < s and h < 0:
        if prev_h is not None and prev_h >= 0:
            return {**base, "signal": "SELL",
                    "reason": "MACD crossed below signal — fresh bearish momentum",
                    "brief": "Bearish crossover"}
        return {**base, "signal": "SELL",
                "reason": f"MACD below signal with negative histogram — bearish",
                "brief": "Bearish momentum"}
    else:
        return {**base, "signal": "HOLD",
                "reason": "MACD and signal are close — momentum neutral",
                "brief": "Neutral"}


def _evaluate_stochastic(stoch_k: pd.Series, stoch_d: pd.Series,
                         ob: int = 80, os_level: int = 20) -> dict:
    k = _last_valid(stoch_k)
    d = _last_valid(stoch_d)
    prev_k = _nth_last_valid(stoch_k, 2)
    prev_d = _nth_last_valid(stoch_d, 2)

    vals = {}
    if k is not None:
        vals["k"] = round(float(k), 1)
    if d is not None:
        vals["d"] = round(float(d), 1)
    vals["ob"] = ob
    vals["os"] = os_level

    base = {"indicator": "Stochastic", "values": vals}

    if k is None or d is None:
        return {**base, "signal": "HOLD",
                "reason": "Not enough data for Stochastic",
                "brief": "Insufficient data"}

    if k < os_level:
        if prev_k is not None and prev_d is not None and prev_k < prev_d and k > d:
            return {**base, "signal": "BUY",
                    "reason": f"%K crossed above %D in oversold zone (<{os_level}) — strong buy",
                    "brief": f"Oversold crossover"}
        return {**base, "signal": "BUY",
                "reason": f"%K at {k:.1f} — oversold (<{os_level}), potential bounce",
                "brief": "Oversold"}
    elif k > ob:
        if prev_k is not None and prev_d is not None and prev_k > prev_d and k < d:
            return {**base, "signal": "SELL",
                    "reason": f"%K crossed below %D in overbought zone (>{ob}) — strong sell",
                    "brief": f"Overbought crossover"}
        return {**base, "signal": "SELL",
                "reason": f"%K at {k:.1f} — overbought (>{ob}), potential pullback",
                "brief": "Overbought"}
    else:
        return {**base, "signal": "HOLD",
                "reason": f"%K at {k:.1f} — neutral zone",
                "brief": "Neutral zone"}


def _find_crossovers(sma_short, sma_long, macd_hist,
                     stoch_k, stoch_d, stoch_ob, stoch_os, dates):
    """Find historical crossover points for chart markers."""
    markers = []

    ss = sma_short.dropna()
    sl = sma_long.dropna()
    common_idx = ss.index.intersection(sl.index)
    if len(common_idx) >= 2:
        ss_c = ss.loc[common_idx]
        sl_c = sl.loc[common_idx]
        for i in range(1, len(common_idx)):
            prev_diff = ss_c.iloc[i - 1] - sl_c.iloc[i - 1]
            curr_diff = ss_c.iloc[i] - sl_c.iloc[i]
            idx = common_idx[i]
            date_str = idx.strftime("%Y-%m-%d") if hasattr(idx, 'strftime') else str(idx)
            if prev_diff <= 0 < curr_diff:
                markers.append({"time": date_str, "type": "buy",
                                "source": "sma", "label": "Golden Cross"})
            elif prev_diff >= 0 > curr_diff:
                markers.append({"time": date_str, "type": "sell",
                                "source": "sma", "label": "Death Cross"})

    mh = macd_hist.dropna()
    if len(mh) >= 2:
        for i in range(1, len(mh)):
            idx = mh.index[i]
            date_str = idx.strftime("%Y-%m-%d") if hasattr(idx, 'strftime') else str(idx)
            if mh.iloc[i - 1] <= 0 < mh.iloc[i]:
                markers.append({"time": date_str, "type": "buy",
                                "source": "macd", "label": "MACD Cross Up"})
            elif mh.iloc[i - 1] >= 0 > mh.iloc[i]:
                markers.append({"time": date_str, "type": "sell",
                                "source": "macd", "label": "MACD Cross Down"})

    sk = stoch_k.dropna()
    sd = stoch_d.dropna()
    sk_sd_idx = sk.index.intersection(sd.index)
    if len(sk_sd_idx) >= 2:
        sk_c = sk.loc[sk_sd_idx]
        sd_c = sd.loc[sk_sd_idx]
        for i in range(1, len(sk_sd_idx)):
            kv = sk_c.iloc[i]
            idx = sk_sd_idx[i]
            date_str = idx.strftime("%Y-%m-%d") if hasattr(idx, 'strftime') else str(idx)
            prev_diff = sk_c.iloc[i - 1] - sd_c.iloc[i - 1]
            curr_diff = sk_c.iloc[i] - sd_c.iloc[i]
            if prev_diff <= 0 < curr_diff and kv < stoch_os:
                markers.append({"time": date_str, "type": "buy",
                                "source": "stoch", "label": "Stoch Oversold Cross"})
            elif prev_diff >= 0 > curr_diff and kv > stoch_ob:
                markers.append({"time": date_str, "type": "sell",
                                "source": "stoch", "label": "Stoch Overbought Cross"})

    markers.sort(key=lambda m: m["time"])
    return markers


def _last_valid(series: pd.Series):
    valid = series.dropna()
    return valid.iloc[-1] if len(valid) > 0 else None


def _nth_last_valid(series: pd.Series, n: int):
    valid = series.dropna()
    return valid.iloc[-n] if len(valid) >= n else None
