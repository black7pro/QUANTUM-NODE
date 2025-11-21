# =========================================================
# US10Y_FUSION_RUNTIME_v3.6.1_AUTORECOVERY.py
# =========================================================
# ✅ U.S. 10-Year Treasury Macro Fusion Runtime
# ✅ 4-hour UTC cycles + autorecovery
# ✅ Aligned with M1–M7 architecture
# =========================================================

import requests, json, datetime, time, os

API_KEYS = {
    "fred": "dd34406206c77eae198f6512d3dea8a3",
    "finnhub": "d4alo5hr01qseda29ai0d4alo5hr01qseda29aig",
    "chartexchange": "i4pf4iqoz9vjz56eebrf2aa2olln50df",
    "newsapi": "440a0ee7adf040678b329b981b38044b",
    "twelvedata": "177ea18da03a4d93b437798986b140d5"
}

SAVE_PATH = "US10Y"
os.makedirs(SAVE_PATH, exist_ok=True)
LOG_FILE = os.path.join(SAVE_PATH, "FUSION_LOG.txt")
SUMMARY_FILE = os.path.join(SAVE_PATH, "SUMMARY_LAST.txt")
CYCLE_INTERVAL_HOURS = 4
DATA_INTEGRITY_THRESHOLD = 0.5


def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def write_summary(text):
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write(text)

# ---------- DATA FETCHERS ----------
def fetch_fred(series_id):
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={API_KEYS['fred']}&file_type=json"
        r = requests.get(url, timeout=10)
        data = r.json()
        return float(data["observations"][-1]["value"])
    except Exception as e:
        log(f"⚠️ FRED {series_id} fetch failed: {e}")
        return None

def fetch_twelvedata(symbol):
    try:
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEYS['twelvedata']}"
        r = requests.get(url, timeout=10)
        d = r.json()
        if "price" in d:
            return float(d["price"])
        raise Exception(d)
    except Exception as e:
        log(f"⚠️ TwelveData {symbol} failed: {e}")
        return None

def fetch_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/", timeout=10)
        d = r.json()
        return {"value": int(d["data"][0]["value"]), "classification": d["data"][0]["value_classification"]}
    except Exception as e:
        log(f"⚠️ FearGreed failed: {e}")
        return {"value": None, "classification": None}

def fetch_crypto(symbol):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        r = requests.get(url, timeout=10)
        return r.json()[symbol]["usd"]
    except Exception:
        return None

# ---------- MODULES ----------
def module_1_macro():
    y10 = fetch_fred("DGS10")
    spx = fetch_twelvedata("SPX")
    vix = fetch_twelvedata("VIX")
    dxy = fetch_twelvedata("DXY")
    macro_tone = round(sum(v is not None for v in [y10, spx, vix, dxy]) / 4, 3)
    return {"US10Y": y10, "SPX": spx, "VIX": vix, "DXY": dxy, "macro_tone_score": macro_tone}

def module_2_behavioral():
    fg = fetch_fear_greed()
    btc = fetch_crypto("bitcoin")
    polarity = round(((fg["value"] or 50) / 100), 3)
    return {"fear_greed": fg, "BTC": btc, "behavioral_polarity": polarity}

def module_3_scenario(m1, m2):
    tone = m1["macro_tone_score"]; polarity = m2["behavioral_polarity"]
    if tone > 0.7 and polarity < 0.45: bias = "yield_pressure"
    elif tone < 0.5 and polarity > 0.55: bias = "easing"
    else: bias = "neutral"
    conf = round(0.6 + abs(0.5 - polarity) * 0.5, 3)
    return {"short_term_bias": bias, "confidence": conf}

def module_4_mtf(): return {"alignment_score": 0.33, "phase": "rotation"}

def module_5_cross(m1, m2):
    try: corr = round(((m1["US10Y"] or 0) / (m1["SPX"] or 1)) * 10, 3)
    except: corr = 0.0
    return {"US10Y_SPX_corr": corr}

def module_6_risk(m1, m2):
    risk = round((m1["macro_tone_score"] + (1 - m2["behavioral_polarity"])) / 7, 3)
    return {"risk_chain_score": risk}

def module_7_forecast(m1, m2, m3, m6):
    return {"directional_bias": m3["short_term_bias"],
            "expected_volatility_pct": round(m6["risk_chain_score"] * 2.5, 2),
            "confidence_score": m3["confidence"]}

# ---------- INTEGRITY + AUTORECOVERY ----------
def compute_data_integrity(m1, m2):
    vals = [m1["US10Y"], m1["SPX"], m1["VIX"], m2["BTC"]]
    return sum(v is not None for v in vals) / len(vals)

def auto_recover_if_needed(score):
    if score < DATA_INTEGRITY_THRESHOLD:
        log(f"⚠️ Low data integrity ({score:.2f}) — retry in 10 min...")
        time.sleep(600)
        fusion_cycle()

# ---------- MAIN CYCLE ----------
def fusion_cycle():
    now = datetime.datetime.utcnow().isoformat() + "Z"
    log(f"\n===========================================================\nUS10Y Fusion Cycle - {now}\n===========================================================\n")

    m1 = module_1_macro(); m2 = module_2_behavioral(); m3 = module_3_scenario(m1, m2)
    m4 = module_4_mtf(); m5 = module_5_cross(m1, m2); m6 = module_6_risk(m1, m2)
    m7 = module_7_forecast(m1, m2, m3, m6)
    integrity = compute_data_integrity(m1, m2)

    output = {"timestamp_utc": now,
              "modules": {"M1": m1, "M2": m2, "M3": m3, "M4": m4, "M5": m5, "M6": m6, "M7": m7}}
    filename = f"{SAVE_PATH}/TOTAL_RECALL_RUNTIME_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f: json.dump(output, f, indent=2, ensure_ascii=False)

    summary = (
        f"US10Y FUSION SUMMARY ({now})\n"
        f"[M1] 10Y: {m1['US10Y']} | SPX: {m1['SPX']} | VIX: {m1['VIX']} | Macro: {m1['macro_tone_score']}\n"
        f"[M2] BTC: {m2['BTC']} | Polarity: {m2['behavioral_polarity']}\n"
        f"[M3] Bias: {m3['short_term_bias']} | Conf: {m3['confidence']}\n"
        f"[M5] Corr: {m5['US10Y_SPX_corr']}\n"
        f"[M6] Risk: {m6['risk_chain_score']}\n"
        f"[M7] Forecast: {m7['directional_bias']} | Vol: {m7['expected_volatility_pct']}% | Conf: {m7['confidence_score']}\n"
        f"Integrity: {integrity:.2f}\n")
    write_summary(summary); log(summary)
    log(f"✅ Data saved: {filename}")
    auto_recover_if_needed(integrity)
    log(f"Sleeping for {CYCLE_INTERVAL_HOURS} hours...\n")

def continuous_runtime():
    while True:
        fusion_cycle()
        time.sleep(CYCLE_INTERVAL_HOURS * 3600)

if __name__ == "__main__":
    continuous_runtime()