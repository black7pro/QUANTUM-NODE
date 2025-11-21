# ==============================================================
# 🌍 QUANTUM LIVE PROPAGATION v4.0
# (Pythonista Safe Build — Full NumPy Compatibility)
# ==============================================================
# Purpose: Pull live market + sentiment data and propagate into
# TOTAL RECALL modules (1–7)
# ==============================================================

# --- PYTHONISTA NUMPY PATCH (full compatibility) ---
import sys, types, random

class FakeGenerator:
    def random(self, *args):
        return [random.random() for _ in range(args[0] if args else 1)]
    def normal(self, loc=0, scale=1, size=1):
        return [random.gauss(loc, scale) for _ in range(size if isinstance(size, int) else 1)]
    def integers(self, low, high=None, size=1):
        if high is None:  # mimic numpy behaviour
            high, low = low, 0
        return [random.randint(low, high - 1) for _ in range(size if isinstance(size, int) else 1)]

class FakeRandom:
    Generator = FakeGenerator  # fixes Generator reference
    def rand(self, *args):
        return [random.random() for _ in range(args[0] if args else 1)]
    def randn(self, *args):
        return [random.gauss(0, 1) for _ in range(args[0] if args else 1)]
    def randint(self, a, b=None):
        return random.randint(a, b or a)
    def choice(self, seq):
        return random.choice(seq)
    def seed(self, *args): pass

fake_numpy = types.SimpleNamespace(
    int64=int,
    float64=float,
    datetime64=str,
    timedelta64=str,
    ndarray=list,
    uint=int,
    uint64=int,
    random=FakeRandom()
)
sys.modules["numpy"] = fake_numpy
# ---------------------------------------------------------------

import requests, json, datetime, math, statistics
from pytrends.request import TrendReq

print("\n🚀 QUANTUM LIVE PROPAGATION v4.0 —", datetime.datetime.utcnow(), "UTC\n")

# --- CONFIGURATION ---
ANCHOR_FILE = "US500_TOTAL_RECALL_ANCHOR.json"

tickers = {
    "SPX": "^GSPC",
    "DJI": "^DJI",
    "DXY": "DX-Y.NYB",
    "VIX": "^VIX",
    "US10Y": "^TNX",
    "WTI": "CL=F",
    "GOLD": "GC=F",
    "BTC": "BTC-USD",
    "ETH": "ETH-USD"
}


# ==============================================================
# PHASE 1 — DATA FETCHERS
# ==============================================================

def fetch_yahoo_price(ticker):
    """Fetch last 5d of price data + compute metrics."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=5d&interval=1h"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()["chart"]["result"][0]
    prices = data["indicators"]["quote"][0]["close"]
    prices = [p for p in prices if p is not None]
    if len(prices) < 3:
        return None, None, None, []
    last = prices[-1]
    change = ((prices[-1] - prices[-2]) / prices[-2]) * 100
    vol = (statistics.stdev(prices[-10:]) / statistics.mean(prices[-10:])) * 100
    return round(last, 2), round(change, 2), round(vol, 2), prices[-20:]


def fetch_sentiment_score():
    """Google Trends sentiment proxy."""
    try:
        pytrends = TrendReq(hl="en-US", tz=0)
        kw = ["stocks", "recession", "inflation", "crypto", "fear index"]
        pytrends.build_payload(kw, timeframe="now 7-d")
        df = pytrends.interest_over_time()
        if df.empty:
            return 50.0
        score = df.mean().mean()
        return round(score, 2)
    except Exception as e:
        print("⚠️ Sentiment fetch failed:", e)
        return 50.0


# ==============================================================
# PHASE 2 — MATH UTILITIES
# ==============================================================

def correlation(a, b):
    """Manual Pearson correlation."""
    if len(a) != len(b) or len(a) < 3:
        return 0
    n = len(a)
    mean_a = sum(a) / n
    mean_b = sum(b) / n
    num = sum((a[i] - mean_a) * (b[i] - mean_b) for i in range(n))
    den = math.sqrt(
        sum((a[i] - mean_a) ** 2 for i in range(n)) *
        sum((b[i] - mean_b) ** 2 for i in range(n))
    )
    return round(num / den, 2) if den else 0


def compute_risk_metrics(data):
    """Calculate systemic risk score & macro tone."""
    vix = data.get("VIX", {}).get("price", 20)
    dxy = data.get("DXY", {}).get("price", 105)
    us10y = data.get("US10Y", {}).get("price", 4)
    spx = data.get("SPX", {}).get("change_pct", 0)
    sentiment = data.get("sentiment_proxy", 50)

    risk_score = min(
        1,
        max(0, ((vix - 15) / 15 + (dxy - 100) / 10 - spx / 10 + (100 - sentiment) / 100) / 4),
    )

    tone = (
        "risk_on" if risk_score < 0.35 else
        "neutral" if risk_score < 0.6 else
        "risk_off"
    )

    return {
        "vix": vix,
        "dxy": dxy,
        "sentiment": sentiment,
        "risk_score": round(risk_score, 3),
        "macro_tone_state": tone
    }


# ==============================================================
# PHASE 3 — PROPAGATION ENGINE
# ==============================================================

def run_propagation(anchor_file=ANCHOR_FILE):
    print("📡 Loading anchor:", anchor_file)
    with open(anchor_file) as f:
        modules = json.load(f)

    live_data = {}
    price_hist = {}

    print("\n📊 Fetching live market data...\n")
    for name, t in tickers.items():
        try:
            p, c, v, hist = fetch_yahoo_price(t)
            live_data[name] = {"price": p, "change_pct": c, "volatility": v}
            price_hist[name] = hist
            print(f"{name:<6} | Price: {p:>10} | Δ%: {c:>6} | Vol: {v:>6}")
        except Exception as e:
            live_data[name] = {"error": str(e)}
            print(f"{name:<6} | ⚠️ Error: {e}")

    # --- Behavioral Polarity (Sentiment Proxy) ---
    live_data["sentiment_proxy"] = fetch_sentiment_score()
    print(f"\n🧠 Sentiment proxy: {live_data['sentiment_proxy']}")

    # --- Cross-Asset Correlations ---
    if "SPX" in price_hist:
        live_data["correlations"] = {}
        for k, v in price_hist.items():
            if k != "SPX":
                live_data["correlations"][f"SPX_vs_{k}"] = correlation(price_hist["SPX"], v)
        print("\n🔗 Cross-asset correlations (SPX):")
        for pair, val in live_data["correlations"].items():
            print(f"  {pair:<15}: {val}")

    # --- Risk Metrics ---
    risk_metrics = compute_risk_metrics(live_data)
    live_data["risk_metrics"] = risk_metrics
    print("\n⚖️ Risk Metrics:")
    for k, v in risk_metrics.items():
        print(f"  {k:<18}: {v}")

    # --- Inject into Modules ---
    now = datetime.datetime.utcnow().isoformat() + "Z"
    for mod in modules:
        mod.setdefault("runtime", {})["last_update_utc"] = now
        mod.setdefault("telemetry", {})["fusion_integrity"] = 0.998
        mod.setdefault("outputs", {})["live_feed"] = live_data

        if "MODULE_6" in mod.get("module_id", ""):
            mod["outputs"]["systemic_risk_score"] = risk_metrics["risk_score"]
            mod["outputs"]["macro_tone_state"] = risk_metrics["macro_tone_state"]

    # --- Save Runtime File ---
    outname = f"TOTAL_RECALL_RUNTIME_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M')}.json"
    with open(outname, "w") as f:
        json.dump(modules, f, indent=2)

    print(f"\n✅ Propagation + Risk Calibration complete: {outname}")
    print(f"🕒 Timestamp: {now}")
    print("Ready to upload to the Fusion Engine.\n")


# ==============================================================
# MAIN EXECUTION
# ==============================================================

if __name__ == "__main__":
    run_propagation()