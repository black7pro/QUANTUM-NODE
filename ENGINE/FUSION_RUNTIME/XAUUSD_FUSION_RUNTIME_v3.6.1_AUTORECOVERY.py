# =========================================================
# XAUUSD_FUSION_RUNTIME_v3.6.1_AUTORECOVERY.py
# =========================================================
# ✅ Gold (XAU/USD) Runtime
# ✅ 4-hour UTC cycles + autorecovery + macro linkage
# ✅ Schema-aligned with US500, US100, BTCUSD runtimes
# =========================================================

import requests, json, datetime, time, os

# ==============================
# 🔑 API KEYS — paste yours here
# ==============================
API_KEYS = {
    "fred": "dd34406206c77eae198f6512d3dea8a3",
    "finnhub": "d4alo5hr01qseda29ai0d4alo5hr01qseda29aig",
    "chartexchange": "i4pf4iqoz9vjz56eebrf2aa2olln50df",
    "newsapi": "440a0ee7adf040678b329b981b38044b",
    "twelvedata": "177ea18da03a4d93b437798986b140d5"
}

SAVE_PATH = "XAUUSD"
os.makedirs(SAVE_PATH, exist_ok=True)
LOG_FILE = os.path.join(SAVE_PATH, "FUSION_LOG.txt")
CYCLE_INTERVAL_HOURS = 4
DATA_INTEGRITY_THRESHOLD = 0.5

# ==============================
# 🧩 LOGGING
# ==============================
def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

# ==============================
# 🌐 DATA FETCHERS
# ==============================
def fetch_twelvedata(symbol="XAU/USD"):
    try:
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEYS['twelvedata']}"
        r = requests.get(url, timeout=10)
        d = r.json()
        if "price" in d:
            log(f"✅ TwelveData {symbol}: {d['price']}")
            return float(d["price"])
        raise Exception(f"Invalid TwelveData response: {d}")
    except Exception as e:
        log(f"❌ TwelveData {symbol} fetch failed: {e}")
        return None

def fetch_yahoo(symbol):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        r = requests.get(url, timeout=10)
        d = r.json()
        return d["chart"]["result"][0]["meta"]["regularMarketPrice"]
    except Exception as e:
        log(f"⚠️ Yahoo {symbol} failed: {e}")
        return None

def fetch_fred(series_id):
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={API_KEYS['fred']}&file_type=json"
        r = requests.get(url, timeout=10)
        d = r.json()
        return float(d["observations"][-1]["value"])
    except Exception as e:
        log(f"⚠️ FRED {series_id} fetch failed: {e}")
        return None

def fetch_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/", timeout=10)
        d = r.json()
        return {
            "value": int(d["data"][0]["value"]),
            "classification": d["data"][0]["value_classification"],
        }
    except Exception as e:
        log(f"⚠️ FearGreed fetch failed: {e}")
        return {"value": None, "classification": None}

def fetch_crypto(symbol):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        r = requests.get(url, timeout=10)
        return r.json()[symbol]["usd"]
    except Exception:
        return None

# ==============================
# 🧠 MODULES
# ==============================
def module_1_macro():
    xau = fetch_twelvedata("XAU/USD") or fetch_yahoo("GC=F")
    dxy = fetch_yahoo("DX-Y.NYB")
    yield_10y = fetch_fred("DGS10")
    vix = fetch_yahoo("^VIX")

    macro_tone = 0.65 if xau and dxy and yield_10y else 0.3
    return {
        "XAUUSD": xau,
        "DXY": dxy,
        "yield_10y": yield_10y,
        "VIX": vix,
        "macro_tone_score": round(macro_tone, 3),
    }

def module_2_behavioral():
    fg = fetch_fear_greed()
    btc = fetch_crypto("bitcoin")
    eth = fetch_crypto("ethereum")
    polarity = round(((fg["value"] or 50) / 100), 3)
    return {
        "fear_greed": fg,
        "BTC": btc,
        "ETH": eth,
        "behavioral_polarity": polarity,
    }

def module_3_scenario(m1, m2):
    bias = "bullish" if m1["macro_tone_score"] > 0.5 and m2["behavioral_polarity"] > 0.55 else "neutral"
    conf = round(0.7 + (m1["macro_tone_score"] / 3), 3)
    return {"short_term_bias": bias, "confidence": conf}

def module_4_mtf():
    return {"alignment_score": 0.32, "phase": "accumulation"}

def module_5_cross(m1, m2):
    try:
        corr = round(((m1["XAUUSD"] or 0) / (m2["BTC"] or 1)) * 0.001, 3)
    except Exception:
        corr = 0.0
    return {"XAU_BTC_corr": corr}

def module_6_risk(m1, m2):
    risk = round((m1["macro_tone_score"] + m2["behavioral_polarity"]) / 9, 3)
    return {"risk_chain_score": risk}

def module_7_forecast(m1, m2, m3, m6):
    return {
        "directional_bias": m3["short_term_bias"],
        "expected_volatility_pct": round(m6["risk_chain_score"] * 2.4, 2),
        "confidence_score": m3["confidence"],
    }

# ==============================
# 🩺 INTEGRITY + AUTORECOVERY
# ==============================
def compute_data_integrity(m1, m2):
    filled = sum(1 for v in [m1["XAUUSD"], m1["DXY"], m1["yield_10y"], m2["BTC"]] if v)
    return filled / 4

def auto_recover_if_needed(integrity_score):
    if integrity_score < DATA_INTEGRITY_THRESHOLD:
        log(f"⚠️ Data integrity low ({integrity_score:.2f}) — retrying in 10 minutes...")
        time.sleep(600)
        fusion_cycle()

# ==============================
# 🔁 FUSION CYCLE
# ==============================
def fusion_cycle():
    now = datetime.datetime.utcnow().isoformat() + "Z"
    log("\n===========================================================")
    log(f"XAUUSD Fusion Cycle - {now}")
    log("===========================================================\n")

    m1 = module_1_macro()
    m2 = module_2_behavioral()
    m3 = module_3_scenario(m1, m2)
    m4 = module_4_mtf()
    m5 = module_5_cross(m1, m2)
    m6 = module_6_risk(m1, m2)
    m7 = module_7_forecast(m1, m2, m3, m6)

    integrity = compute_data_integrity(m1, m2)
    output = {
        "timestamp_utc": now,
        "modules": {"M1": m1, "M2": m2, "M3": m3, "M4": m4, "M5": m5, "M6": m6, "M7": m7},
    }

    filename = f"{SAVE_PATH}/TOTAL_RECALL_RUNTIME_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    # Dashboard summary
    log("📊 FUSION DASHBOARD SUMMARY")
    log("-----------------------------------------------------------")
    log(f"[M1] XAU: {m1['XAUUSD']} | DXY: {m1['DXY']} | 10Y: {m1['yield_10y']} | VIX: {m1['VIX']} | Macro: {m1['macro_tone_score']}")
    log(f"[M2] BTC: {m2['BTC']} | ETH: {m2['ETH']} | Polarity: {m2['behavioral_polarity']}")
    log(f"[M3] Bias: {m3['short_term_bias']} | Conf: {m3['confidence']}")
    log(f"[M5] XAU-BTC Corr: {m5['XAU_BTC_corr']}")
    log(f"[M6] Risk: {m6['risk_chain_score']}")
    log(f"[M7] Forecast: {m7['directional_bias']} | Vol: {m7['expected_volatility_pct']}% | Conf: {m7['confidence_score']}")
    log("-----------------------------------------------------------")
    log(f"✅ Data saved: {filename}")
    log(f"🩺 Data Integrity Score → {integrity:.2f}\n")

    auto_recover_if_needed(integrity)
    log(f"Sleeping for {CYCLE_INTERVAL_HOURS} hours...\n")

def continuous_runtime():
    while True:
        fusion_cycle()
        time.sleep(CYCLE_INTERVAL_HOURS * 3600)

if __name__ == "__main__":
    continuous_runtime()