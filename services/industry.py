import time
import logging
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

import yfinance as yf
from services.yf_session import get_cached_info, yf_fetch_with_retry

logger = logging.getLogger(__name__)

RATIO_KEYS = [
    "trailingPE", "forwardPE", "priceToBook", "priceToSalesTrailing12Months",
    "enterpriseToEbitda", "profitMargins", "operatingMargins", "returnOnEquity",
    "returnOnAssets", "currentRatio", "debtToEquity", "quickRatio",
    "dividendYield", "payoutRatio", "revenueGrowth", "earningsGrowth",
]

_cache = {}
CACHE_TTL = 7200  # 2 hours
NEGATIVE_CACHE_TTL = 300  # 5 minutes for failed industry lookups

MAX_PEERS = 8
PEER_TIMEOUT = 15  # seconds per peer future


def _fetch_peer_ratios(symbol: str) -> dict | None:
    try:
        info = get_cached_info(symbol)
        if not info:
            return None
        out = {}
        for k in RATIO_KEYS:
            v = info.get(k)
            if v is not None and isinstance(v, (int, float)):
                out[k] = v
        return out if out else None
    except Exception as e:
        logger.debug(f"_fetch_peer_ratios({symbol}) failed: {e}")
        return None


def fetch_industry_medians(industry_key: str, exclude_symbol: str = "") -> dict:
    """Return {ratio_key: median_value} for an industry, cached for 2 hours."""
    if not industry_key:
        return {}

    cached = _cache.get(industry_key)
    if cached:
        ttl = CACHE_TTL if cached.get("ok") else NEGATIVE_CACHE_TTL
        if (time.time() - cached["ts"]) < ttl:
            return cached["data"]

    try:
        ind = yf_fetch_with_retry(lambda: yf.Industry(industry_key))
        top = yf_fetch_with_retry(lambda: ind.top_companies)
        if top is None or top.empty:
            _cache[industry_key] = {"ts": time.time(), "data": {}, "ok": False}
            return {}
        peer_symbols = [s for s in list(top.index)[:MAX_PEERS]
                        if s.upper() != exclude_symbol.upper()]
    except Exception as e:
        logger.warning(f"Failed to fetch industry peers for {industry_key}: {e}")
        _cache[industry_key] = {"ts": time.time(), "data": {}, "ok": False}
        return {}

    all_ratios = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(_fetch_peer_ratios, sym): sym for sym in peer_symbols}
        for future in as_completed(futures, timeout=PEER_TIMEOUT * 2):
            try:
                r = future.result(timeout=PEER_TIMEOUT)
                if r:
                    all_ratios.append(r)
            except Exception as e:
                logger.debug(f"Peer future failed: {e}")

    if len(all_ratios) < 2:
        _cache[industry_key] = {"ts": time.time(), "data": {}, "ok": False}
        return {}

    medians = {}
    for key in RATIO_KEYS:
        vals = [r[key] for r in all_ratios if key in r]
        if len(vals) >= 2:
            medians[key] = round(statistics.median(vals), 4)

    result = {"medians": medians, "peerCount": len(all_ratios)}
    _cache[industry_key] = {"ts": time.time(), "data": result, "ok": True}
    return result
