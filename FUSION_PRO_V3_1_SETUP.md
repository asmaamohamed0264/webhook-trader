# Fusion Pro Strategy v3.1 - Advanced Setup Guide

## 🚀 **STRATEGIA FUSION PRO V3.1 - VERSIUNEA AVANSATĂ**

Strategia a fost actualizată cu toate funcționalitățile din PineScript v3.1:

### ✨ **FUNCȚIONALITĂȚI NOI ADĂUGATE:**

1. **🕐 Filtru Sesiune RTH** - Trading doar în orele 09:30-16:00
2. **📊 HTF Trend Filter** - Filtru trend pe timeframe superior (EMA200)
3. **🔄 Cooldown Avansat** - Pauză după stop loss cu tracking
4. **📈 Trailing Stops** - Stop loss dinamic cu trailStartRR și trailATRMult
5. **📊 Position Tracking** - Urmărire poziții și limite zilnice
6. **💰 Fallback Sizing** - Dimensionare alternativă când riscul fix nu funcționează

## 📋 **VARIABILELE DE MEDIU COMPLETE PENTRU DOKPLOY**

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
FUSION_TEST_MODE=true

# ===== CONFIGURAȚIA FUSION PRO V3.1 =====
# Simboluri și timeframe
FUSION_SYMBOLS=ASTS,AAPL
FUSION_TIMEFRAME=1D

# Risk Management
FUSION_RISK_PCT=0.5
FUSION_ATR_MULT_SL=1.5
FUSION_ATR_MULT_TP=1.0
FUSION_ACCOUNT_SIZE=10000
FUSION_USE_FIXED_RISK=true
FUSION_FALLBACK_PCT=5.0

# Technical Indicators
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

# Trailing Stops
FUSION_TRAIL_START_RR=0.5
FUSION_TRAIL_ATR_MULT=1.2
FUSION_MIN_ATR_PCT=0.20

# Execution Filters
FUSION_VOL_FILTER_ON=true
FUSION_VOL_SMA_LEN=50
FUSION_VOL_MIN_MULT=1.0
FUSION_MIN_BARS_GAP=3
FUSION_MAX_TRADES_DAY=10

# Trading Session (RTH)
FUSION_TRADE_SESSION_START=09:30
FUSION_TRADE_SESSION_END=16:00

# HTF Trend Filter
FUSION_USE_HTF_TREND=true
FUSION_HTF_TIMEFRAME=60

# Cooldown Settings
FUSION_USE_COOLDOWN=true
FUSION_COOLDOWN_BARS=10
```

## 🎯 **FUNCȚIONALITĂȚI DETALIATE**

### 1. **🕐 Filtru Sesiune RTH**
- **Funcție**: Trading doar în orele 09:30-16:00 (Regular Trading Hours)
- **Configurare**: `FUSION_TRADE_SESSION_START=09:30`, `FUSION_TRADE_SESSION_END=16:00`
- **Beneficiu**: Evită trading în orele de volatilitate ridicată

### 2. **📊 HTF Trend Filter**
- **Funcție**: Filtru trend pe timeframe superior (EMA200)
- **Configurare**: `FUSION_USE_HTF_TREND=true`, `FUSION_HTF_TIMEFRAME=60`
- **Beneficiu**: Confirmă trendul pe timeframe mai mare

### 3. **🔄 Cooldown Avansat**
- **Funcție**: Pauză după stop loss pentru a evita overtrading
- **Configurare**: `FUSION_USE_COOLDOWN=true`, `FUSION_COOLDOWN_BARS=10`
- **Beneficiu**: Reduce riscul de pierderi consecutive

### 4. **📈 Trailing Stops**
- **Funcție**: Stop loss dinamic care urmărește profitul
- **Configurare**: `FUSION_TRAIL_START_RR=0.5`, `FUSION_TRAIL_ATR_MULT=1.2`
- **Beneficiu**: Maximizează profiturile și minimizează pierderile

### 5. **📊 Position Tracking**
- **Funcție**: Urmărire poziții și limite zilnice
- **Configurare**: `FUSION_MAX_TRADES_DAY=10`, `FUSION_MIN_BARS_GAP=3`
- **Beneficiu**: Control strict asupra expunerii la risc

### 6. **💰 Fallback Sizing**
- **Funcție**: Dimensionare alternativă când riscul fix nu funcționează
- **Configurare**: `FUSION_USE_FIXED_RISK=true`, `FUSION_FALLBACK_PCT=5.0`
- **Beneficiu**: Asigură execuția ordinelor chiar dacă calculul de risc eșuează

## 🚀 **PAȘII PENTRU ACTIVARE**

### 1. **Adaugă toate variabilele în Dokploy**
- Mergi la aplicația `webhook-trader` în Dokploy
- Click pe tab-ul **Environment**
- Adaugă toate variabilele de mai sus
- Click **Save**

### 2. **Redeploy aplicația**
- Click pe **Deploy** sau **Redeploy**
- Așteaptă ca aplicația să se pornească

### 3. **Verifică funcționalitatea**
- Testează endpoint-ul: `GET https://abot.qub3.uk/status/fusion_pro`
- Trigger manual: `POST https://abot.qub3.uk/fusion_pro/trigger`

## 📊 **EXEMPLU DE RĂSPUNS AVANSAT**

```json
{
  "status": "completed",
  "results": [
    {
      "symbol": "ASTS",
      "status": "completed",
      "signal_data": {
        "signal": "HOLD",
        "reason": "Outside trading session, Volume filter failed",
        "price": 7.21,
        "filters": {
          "in_session": false,
          "vol_ok": false,
          "vol_ok2": true,
          "cooling": false,
          "can_trade_today": true,
          "bars_since_entry": 100000
        },
        "indicators": {
          "ema_fast": 7.85,
          "ema_slow": 8.82,
          "macd_hist": -0.031,
          "rsi": 38.89,
          "adx": 13.43,
          "atr": 0.20,
          "atr_pct": 2.79
        }
      }
    }
  ]
}
```

## 🎯 **BENEFICIILE VERSIUNII V3.1**

- ✅ **Control mai strict** asupra condițiilor de trading
- ✅ **Filtre avansate** pentru a evita semnalele false
- ✅ **Management de risc îmbunătățit** cu trailing stops
- ✅ **Tracking complet** al pozițiilor și limitelor
- ✅ **Flexibilitate** în dimensionarea pozițiilor
- ✅ **Compatibilitate completă** cu PineScript v3.1

---

**🎉 Strategia Fusion Pro v3.1 este acum complet funcțională cu toate funcționalitățile avansate!**

**Aplicația ta este un bot de trading profesional cu strategie avansată!** 🚀
