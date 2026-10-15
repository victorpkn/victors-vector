# Victor's Vector

Stock analysis for **Thai SET** and **US** equities. One app, two markets, and a UI you can switch between English and Thai.

Search a ticker, flip between 🇹🇭 SET and 🇺🇸 US, and get charts, buy/hold/sell signals, fundamentals, a discounted-cash-flow valuation, and a short analyst-style brief. Built for research and education — not financial advice.

## What it covers

| Market | How tickers work | Examples |
| --- | --- | --- |
| Thailand (SET) | Symbol is looked up on Yahoo Finance with a `.BK` suffix | `PTT`, `AOT`, `CPALL`, `KBANK` |
| United States | Standard US symbols, equities and ETFs | `AAPL`, `NVDA`, `TSLA`, `MSFT` |

The interface has an **EN / TH** toggle. Copy lives in `static/i18n/en.json` and `static/i18n/th.json`.

## Features

- **Brief** — a 10-section note: technical setup, trend, momentum, support and resistance, entry view, long-term view, bear/base/bull scenarios, catalysts, risks, and portfolio fit. Sentences are generated from the numbers, not from an LLM.
- **Signals** — Buy, Hold, or Sell from SMA crossovers, MACD, and Stochastic, with adjustable sensitivity.
- **Charts** — price history plus studies you can turn on (EMAs, Bollinger Bands, RSI, VWAP, and more).
- **Summary** — market cap, ratios, financial health, dividends, growth, and analyst targets.
- **Research** — company and industry context for the ticker.
- **Valuation** — discounted cash flow with editable growth, discount rate, and terminal assumptions.
- **Backtest** — replay the signal rules on historical prices.
- **Watchlist, compare, and portfolio** — track names, put two tickers side by side, and see live P&L.
- **Alerts** — price alerts, with optional email when SMTP is configured.
- **Paper trading** — practice buys and sells against a simulated balance.
- **Themes** — curated groups (AI infrastructure, semis, space, defense, energy, and others) for quick jumps from the home screen.

Prices and fundamentals come from Yahoo Finance through `yfinance`.

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open [http://localhost:5000](http://localhost:5000).

Optional email alerts (Gmail SMTP):

```bash
export SMTP_EMAIL="you@gmail.com"
export SMTP_PASSWORD="your-app-password"
export ALERT_RECIPIENT="you@gmail.com"   # defaults to SMTP_EMAIL
```

## Deploy

The repo includes a `Dockerfile` (Python 3.11, Gunicorn) and `render.yaml` for [Render](https://render.com). Set `PORT` in the environment; the container binds to `0.0.0.0:$PORT`.

## Disclaimer

Victor's Vector is for educational purposes only. It is not financial, investment, or trading advice. Market data can be delayed or incomplete.

---

# Victor's Vector (ภาษาไทย)

แอปวิเคราะห์หุ้นสำหรับตลาด **ไทย (SET)** และ **สหรัฐฯ (US)** สลับตลาดได้ในคลิกเดียว และสลับภาษาอินเทอร์เฟซระหว่างอังกฤษกับไทยได้

ค้นหาหุ้น แล้วดูกราฟ สัญญาณซื้อ / ถือ / ขาย งบการเงิน การประเมินมูลค่าแบบ DCF และบทสรุปสไตล์นักวิเคราะห์ ใช้เพื่อการศึกษาและการค้นคว้าเท่านั้น ไม่ใช่คำแนะนำการลงทุน

## ตลาดที่รองรับ

| ตลาด | วิธีค้นหา | ตัวอย่าง |
| --- | --- | --- |
| ไทย (SET) | ระบบเติม `.BK` ให้เองตอนดึงข้อมูลจาก Yahoo Finance | `PTT`, `AOT`, `CPALL`, `KBANK` |
| สหรัฐฯ | ใช้สัญลักษณ์หุ้นสหรัฐตามปกติ รวม ETF | `AAPL`, `NVDA`, `TSLA`, `MSFT` |

กดปุ่ม **EN / TH** ที่มุมขวาบนเพื่อเปลี่ยนภาษา

## สิ่งที่ทำได้

- **Brief** — บทสรุป 10 ส่วน: ภาพเทคนิค แนวโน้ม โมเมนตัม แนวรับแนวต้าน มุมมองเข้าซื้อ มุมมองระยะยาว สถานการณ์หมี / ฐาน / กระทิง ตัวเร่ง ความเสี่ยง และความเข้ากันกับพอร์ต
- **Signals** — สัญญาณ Buy, Hold, Sell จาก SMA, MACD และ Stochastic ปรับความเข้มงวดได้
- **กราฟ** — ราคาพร้อมอินดิเคเตอร์ (EMA, Bollinger Bands, RSI, VWAP และอื่น ๆ)
- **Summary** — มูลค่าตลาด อัตราส่วนสำคัญ สุขภาพการเงิน เงินปันผล การเติบโต และเป้าหมายนักวิเคราะห์
- **Valuation** — โมเดล DCF ปรับสมมติฐานได้
- **Backtest** — ทดสอบกฎสัญญาณกับราคาในอดีต
- **Watchlist, เปรียบเทียบ, พอร์ต** — ติดตามหุ้น เทียบสองตัว และดูกำไรขาดทุน
- **Alerts** — แจ้งเตือนราคา และส่งอีเมลได้ถ้าตั้งค่า SMTP
- **Paper trading** — ซ้อมซื้อขายด้วยเงินจำลอง
- **Themes** — กลุ่มธีม เช่น AI, เซมิคอนดักเตอร์, อวกาศ, พลังงาน สำหรับเลือกหุ้นจากหน้าแรก

ข้อมูลราคาและปัจจัยพื้นฐานมาจาก Yahoo Finance

## รันบนเครื่องตัวเอง

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

เปิด [http://localhost:5000](http://localhost:5000)

## ข้อจำกัดความรับผิด

Victor's Vector มีไว้เพื่อการศึกษาเท่านั้น ไม่ใช่คำแนะนำด้านการลงทุนหรือการซื้อขาย ข้อมูลตลาดอาจล่าช้าหรือไม่ครบถ้วน
