import logging
import yfinance as yf

logger = logging.getLogger(__name__)

_session = None

try:
    from curl_cffi import requests as cffi_requests
    _session = cffi_requests.Session(impersonate="chrome")
    logger.info("yf_session: using curl_cffi (chrome impersonation)")
except Exception:
    import requests as _req
    _session = _req.Session()
    _session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        )
    })
    logger.warning("yf_session: curl_cffi unavailable, falling back to requests")


def Ticker(symbol: str) -> yf.Ticker:
    return yf.Ticker(symbol, session=_session)


def get_session():
    return _session
