import logging
import pandas as pd
from services.yf_session import Ticker, yf_fetch_with_retry

logger = logging.getLogger(__name__)

VALID_PERIODS = {"1mo", "3mo", "6mo", "1y", "2y", "5y"}
VALID_MARKETS = {"set", "us"}
REQUIRED_COLUMNS = {"Open", "High", "Low", "Close", "Volume"}


def normalize_ticker(ticker: str, market: str = "set") -> str:
    ticker = ticker.strip().upper()
    if market == "set" and not ticker.endswith(".BK"):
        ticker += ".BK"
    return ticker


def fetch_stock_data(ticker: str, period: str = "6mo", market: str = "set") -> dict:
    if period not in VALID_PERIODS:
        period = "6mo"
    if market not in VALID_MARKETS:
        market = "set"

    symbol = normalize_ticker(ticker, market)
    stock = Ticker(symbol)
    df = yf_fetch_with_retry(lambda: stock.history(period=period, interval="1d"))

    if df is None or df.empty:
        return {"error": f"No data found for {symbol}"}

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        logger.warning(f"fetch_stock_data({symbol}): missing columns {missing}")
        return {"error": f"Incomplete data for {symbol}"}

    df = df.dropna(subset=["Open", "High", "Low", "Close"])
    if df.empty:
        return {"error": f"No valid price data for {symbol}"}

    df["Volume"] = df["Volume"].fillna(0)

    df.index = pd.to_datetime(df.index)
    df = df.reset_index()
    df.rename(columns={"Date": "date"}, inplace=True)

    if df["date"].dt.tz is not None:
        df["date"] = df["date"].dt.tz_localize(None)

    df = df.set_index("date", drop=False)

    try:
        info = yf_fetch_with_retry(lambda: stock.info)
        name = info.get("longName") or info.get("shortName") or symbol if info else symbol
    except Exception as e:
        logger.warning(f"fetch_stock_data({symbol}): info lookup failed: {e}")
        name = symbol

    candles = []
    for _, row in df.iterrows():
        candles.append({
            "time": row["date"].strftime("%Y-%m-%d"),
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]),
        })

    return {
        "ticker": symbol,
        "name": name,
        "candles": candles,
        "df": df,
    }
