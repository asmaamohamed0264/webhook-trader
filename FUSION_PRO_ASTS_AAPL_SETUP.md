# Fusion Pro Strategy - ASTS & AAPL Testing Setup

## 🎯 **CONFIGURARE PENTRU TESTARE PE ASTS ȘI AAPL**

### 📋 **VARIABILELE DE MEDIU PENTRU DOKPLOY**

Adaugă aceste variabile în **Environment** tab-ul din Dokploy:

```bash
# ===== VARIABILE EXISTENTE (PĂSTREAZĂ-LE) =====
ALPACA_API_KEYS=PKGU5Z2MR2QF6CZN3KSHLW3T6Z
ALPACA_API_SECRETS=9XS54h71XE74Tny73Wqg5PgNZ6rn9YVi
ALPACA_NAMES=alpaca-paper-bot
ALPACA_PAPER=1
IP_WHITELIST=127.0.0.1,localhost,188.27.117.56
DB_URI=postgresql://webhook_user:webhook_secure_pass_2024@webhook-trader-db-ng6qts:5432/webhook_trader
DB_ECHO=True
TEST_MODE=True

# ===== NOILE VARIABILE FUSION PRO =====
# Simboluri pentru testare
FUSION_SYMBOLS=ASTS,AAPL
FUSION_TIMEFRAME=1D
FUSION_RISK_PCT=0.5
FUSION_ATR_MULT_SL=1.5
FUSION_ATR_MULT_TP=1.0
FUSION_ACCOUNT_SIZE=10000

# Parametrii indicatorilor tehnici
FUSION_EMA_FAST=50
FUSION_EMA_SLOW=200
FUSION_MACD_FAST=12
FUSION_MACD_SLOW=26
FUSION_MACD_SIGNAL=9
FUSION_RSI_LEN=14
FUSION_RSI_LONG_MIN=50
FUSION_RSI_LONG_MAX=80
FUSION_RSI_SHORT_MAX=50
FUSION_RSI_SHORT_MIN=20
FUSION_ADX_LEN=14
FUSION_ADX_MIN=16
FUSION_ATR_LEN=14

# Management de risc
FUSION_TRAIL_START_RR=0.5
FUSION_TRAIL_ATR_MULT=1.2
FUSION_MIN_ATR_PCT=0.20

# Filtre de execuție
FUSION_VOL_FILTER_ON=true
FUSION_VOL_SMA_LEN=50
FUSION_VOL_MIN_MULT=1.0
FUSION_MIN_BARS_GAP=3
FUSION_MAX_TRADES_DAY=10

# Setări cooldown
FUSION_USE_COOLDOWN=true
FUSION_COOLDOWN_BARS=10
```

## 🚀 **PAȘII PENTRU ACTIVARE**

### 1. **Adaugă variabilele în Dokploy**
- Mergi la aplicația `webhook-trader` în Dokploy
- Click pe **Environment** tab
- Adaugă toate variabilele de mai sus
- Click **Save**

### 2. **Redeploy aplicația**
- Click pe **Deploy** sau **Redeploy**
- Așteaptă ca aplicația să se pornească

### 3. **Verifică log-urile**
- Mergi la **Logs** tab
- Caută mesajele:
  ```
  🚀 Fusion Pro strategy started in background
  📊 Fusion Pro strategy cycle for symbols: ASTS, AAPL
  Processing ASTS...
  Processing AAPL...
  ```

## 📊 **ENDPOINT-URI PENTRU TESTARE**

### 1. **Status strategie**
```bash
GET https://abot.qub3.uk/status/fusion_pro
```

**Răspuns așteptat:**
```json
{
  "symbols": ["ASTS", "AAPL"],
  "primary_symbol": "ASTS",
  "timeframe": "1D",
  "risk_pct": 0.5,
  "account_size": 10000,
  "config": { ... }
}
```

### 2. **Trigger manual**
```bash
POST https://abot.qub3.uk/fusion_pro/trigger
```

**Răspuns așteptat:**
```json
{
  "status": "completed",
  "results": [
    {
      "symbol": "ASTS",
      "status": "completed",
      "signal_data": {
        "signal": "HOLD",
        "reason": "No clear trend",
        "price": 12.45,
        "indicators": { ... }
      }
    },
    {
      "symbol": "AAPL",
      "status": "completed", 
      "signal_data": {
        "signal": "BUY",
        "reason": "Trend up, Momentum long, Filters OK",
        "price": 175.23,
        "execution": { ... }
      }
    }
  ],
  "summary": {
    "total_symbols": 2,
    "completed": 2,
    "errors": 0
  }
}
```

## 🎯 **CE VA FACE STRATEGIA**

### **Pentru fiecare simbol (ASTS și AAPL):**

1. **Fetch date** - Ia date OHLCV de la Alpaca API
2. **Calculează indicatori** - EMA, MACD, RSI, ADX, ATR
3. **Analizează semnale** - Determină BUY/SELL/HOLD
4. **Execută ordere** - Dacă semnalul nu este HOLD
5. **Log rezultate** - Înregistrează toate deciziile

### **Log-uri așteptate:**
```
📊 Fusion Pro strategy cycle for symbols: ASTS, AAPL
Processing ASTS...
Processing AAPL...
ASTS: HOLD signal - No clear trend
AAPL: BUY signal executed
Strategy cycle completed: 2 symbols processed, 0 errors
```

## ⚠️ **IMPORTANT**

- **Paper Trading**: Toate orderele sunt pe contul de test Alpaca
- **Ore de piață**: Strategia rulează doar între 9:00-16:00
- **Interval**: Verifică la fiecare 5 minute
- **Risk Management**: 0.5% risc per tranzacție
- **Webhook-uri**: Funcționalitatea existentă rămâne neschimbată

## 🔧 **PERSONALIZARE**

Pentru a schimba simbolurile, modifică doar:
```bash
FUSION_SYMBOLS=ASTS,AAPL,TSLA,MSFT
```

Pentru a schimba timeframe-ul:
```bash
FUSION_TIMEFRAME=1h  # sau 4h, 1D, etc.
```

---

**🎉 După ce adaugi variabilele și faci redeploy, strategia va începe să testeze automat pe ASTS și AAPL!**
