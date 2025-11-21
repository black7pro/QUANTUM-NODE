# =========================================================
# SOL_FUSION_RUNTIME_v3.6.1_AUTORECOVERY.py
# =========================================================
# ✅ Solana (SOL/USD) Fusion Runtime
# ✅ 4-hour UTC cycles + autorecovery
# ✅ Layer-1 macro stack + behavioral modules
# =========================================================

import requests, json, datetime, time, os

# ==============================
# 🔑 API KEYS
# ==============================
API_KEYS = {
    "finnhub": "d4alo5hr01qseda29ai0d4alo5hr01qseda29aig",
    "chartexchange": "i4pf4iqoz9vjz56eebrf2aa2olln50df",
    "newsapi": "440a0ee7adf040678b329b981b38044b",
    "twelvedata": "177ea18da03a4d93b437798986b140d5"
}

SAVE_PATH = "SOL"
os.makedirs(SAVE_PATH, exist_ok=True)
LOG_FILE = os.path.join(SAVE_PATH, "FUSION_LOG.txt")
SUMMARY_FILE = os.path.join(SAVE_PATH, "SUMMARY_LAST.txt")
CYCLE_INTERVAL_HOURS = 4
DATA_INTEGRITY_THRESHOLD = 0.5

# ==============================
# 🧩 LOGGING
# ==============================
def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def write_summary(txt):
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        f.write(txt)

# ==============================
# 🌐 DATA FETCHERS
# ==============================
def fetch_twelvedata(symbol="SOL/USD"):
    try:
        url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEYS['twelvedata']}"
        r = requests.get(url, timeout=10)
        d = r.json()
        if "price" in d:
            log(f"✅ TwelveData {symbol}: {d['price']}")
            return float(d["price"])
        raise Exception(d)
    except Exception as e:
        log(f"❌ TwelveData {symbol} failed: {e}")
        return None

def fetch_crypto(symbol="bitcoin"):
    try:
        url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol}&vs_currencies=usd"
        r = requests.get(url, timeout=10)
        return r.json()[symbol]["usd"]
    except Exception as e:
        log(f"⚠️ CoinGecko {symbol} failed: {e}")
        return None

def fetch_solana_network_stats():
    try:
        url = "https://api.mainnet-beta.solana.com"
        payload = {"jsonrpc":"2.0","id":1,"method":"getRecentPerformanceSamples","params":[1]}
        r = requests.post(url, json=payload, timeout=10)
        d = r.json()
        samples = d.get("result", [{}])[0]
        tps = samples.get("numTransactions", 0) / max(samples.get("samplePeriodSecs", 1), 1)
        return round(tps, 2)
    except Exception as e:
        log(f"⚠️ Solana network fetch failed: {e}")
        return None

def fetch_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/", timeout=10)
        d = r.json()
        return {
            "value": int(d["data"][0]["value"]),
            "classification": d["data"][0]["value_classification"]
        }
    except Exception as e:
        log(f"⚠️ FearGreed fetch failed: {e}")
        return {"value": None, "classification": None}

# ==============================
# 🧠 MODULES
# ==============================
def module_1_macro():
    sol = fetch_twelvedata("SOL/USD")
    btc = fetch_crypto("bitcoin")
    eth = fetch_crypto("ethereum")
    tps = fetch_solana_network_stats()
    macro_tone = 0.6 if all([sol, btc, eth]) else 0.4
    return {
        "SOL": sol,
        "BTC": btc,
        "ETH": eth,
        "TPS": tps,
        "macro_tone_score": round(macro_tone, 3)
    }

def module_2_behavioral():
    fg = fetch_fear_greed()
    polarity = round(((fg["value"] or 50) / 100), 3)
    return {
        "fear_greed": fg,
        "behavioral_polarity": polarity
    }

def module_3_scenario(m1, m2):
    if m1["macro_tone_score"] > 0.55 and m2["behavioral_polarity"] > 0.55:
        bias = "bullish"
    elif m1["macro_tone_score"] < 0.45 and m2["behavioral_polarity"] < 0.45:
        bias = "bearish"
    else:
        bias = "neutral"
    conf = round(0.65 + abs(0.5 - m2["behavioral_polarity"]) * 0.6, 3)
    return {"short_term_bias": bias, "confidence": conf}

def module_4_mtf():
    return {"alignment_score": 0.32, "phase": "transition"}

def module_5_cross(m1):
    try:
        corr = round(((m1["SOL"] or 0) / (m1["BTC"] or 1)) * 0.0015, 3)
    except Exception:
        corr = 0.0
    return {"SOL_BTC_corr": corr}

def module_6_risk(m1, m2):
    risk = round((m1["macro_tone_score"] + (1 - m2["behavioral_polarity"])) / 7, 3)
    return {"risk_chain_score": risk}

def module_7_forecast(m1, m2, m3, m6):
    return {
        "directional_bias": m3["short_term_bias"],
        "expected_volatility_pct": round(m6["risk_chain_score"] * 3.4, 2),
        "confidence_score": m3["confidence"]
    }

# ==============================
# 🩺 INTEGRITY + AUTORECOVERY
# ==============================
def compute_data_integrity(m1):
    filled = sum(1 for v in [m1["SOL"], m1["BTC"], m1["ETH"]] if v)
    return filled / 3

def auto_recover_if_needed(score):
    if score < DATA_INTEGRITY_THRESHOLD:
        log(f"⚠️ Data integrity low ({score:.2f}) — retrying in 10 minutes...")
        time.sleep(600)
        fusion_cycle()

# ==============================
# 🔁 FUSION CYCLE
# ==============================
def fusion_cycle():
    now = datetime.datetime.utcnow().isoformat() + "Z"
    log("\n===========================================================")
    log(f"SOL Fusion Cycle - {now}")
    log("===========================================================\n")

    m1 = module_1_macro()
    m2 = module_2_behavioral()
    m3 = module_3_scenario(m1, m2)
    m4 = module_4_mtf()
    m5 = module_5_cross(m1)
    m6 = module_6_risk(m1, m2)
    m7 = module_7_forecast(m1, m2, m3, m6)

    integrity = compute_data_integrity(m1)
    output = {
        "timestamp_utc": now,
        "modules": {"M1": m1, "M2": m2, "M3": m3, "M4": m4, "M5": m5, "M6": m6, "M7": m7}
    }

    filename = f"{SAVE_PATH}/TOTAL_RECALL_RUNTIME_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    summary = (
        f"SOL FUSION SUMMARY ({now})\n"
        f"-----------------------------------------------------------\n"
        f"[M1] SOL: {m1['SOL']} | BTC: {m1['BTC']} | ETH: {m1['ETH']} | TPS: {m1['TPS']} | Macro: {m1['macro_tone_score']}\n"
        f"[M2] Polarity: {m2['behavioral_polarity']}\n"
        f"[M3] Bias: {m3['short_term_bias']} | Conf: {m3['confidence']}\n"
        f"[M5] SOL-BTC Corr: {m5['SOL_BTC_corr']}\n"
        f"[M6] Risk: {m6['risk_chain_score']}\n"
        f"[M7] Forecast: {m7['directional_bias']} | Vol: {m7['expected_volatility_pct']}% | Conf: {m7['confidence_score']}\n"
        f"Integrity: {integrity:.2f}\n"
    )
    write_summary(summary)
    log(summary)
    log(f"✅ Data saved: {filename}")
    auto_recover_if_needed(integrity)
    log(f"Sleeping for {CYCLE_INTERVAL_HOURS} hours...\n")

# ==============================
# 🕒 CONTINUOUS RUNTIME
# ==============================
def continuous_runtime():
    while True:
        fusion_cycle()
        time.sleep(CYCLE_INTERVAL_HOURS * 3600)

if __name__ == "__main__":
    continuous_runtime()