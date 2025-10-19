# Fusion Pro Strategy Setup Guide

## 🚀 Overview

The webhook-trader application has been extended with the **Fusion Pro Strategy** - a fully automated trading bot that runs your PineScript strategy natively in Python.

## 📋 Features

- ✅ **Automated Strategy Execution**: Runs every 5 minutes during market hours
- ✅ **Technical Indicators**: EMA, MACD, RSI, ADX, ATR
- ✅ **Risk Management**: Position sizing based on ATR and risk percentage
- ✅ **Market Data**: Fetches real-time data from Alpaca API
- ✅ **Webhook Compatibility**: Maintains existing webhook functionality
- ✅ **Monitoring**: Real-time status and manual trigger endpoints

## 🔧 Configuration

### Environment Variables to Add in Dokploy

Add these variables to your Dokploy application's Environment tab:

```bash
# Fusion Pro Strategy Configuration
FUSION_SYMBOL=ASTS
FUSION_TIMEFRAME=1D
FUSION_RISK_PCT=0.5
FUSION_ATR_MULT_SL=1.5
FUSION_ATR_MULT_TP=1.0
FUSION_ACCOUNT_SIZE=10000

# Technical Indicator Parameters
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

# Risk Management
FUSION_TRAIL_START_RR=0.5
FUSION_TRAIL_ATR_MULT=1.2
FUSION_MIN_ATR_PCT=0.20

# Execution Filters
FUSION_VOL_FILTER_ON=true
FUSION_VOL_SMA_LEN=50
FUSION_VOL_MIN_MULT=1.0
FUSION_MIN_BARS_GAP=3
FUSION_MAX_TRADES_DAY=10

# Cooldown Settings
FUSION_USE_COOLDOWN=true
FUSION_COOLDOWN_BARS=10
```

## 🎯 API Endpoints

### 1. Strategy Status
```bash
GET https://abot.qub3.uk/status/fusion_pro
```

### 2. Manual Trigger
```bash
POST https://abot.qub3.uk/fusion_pro/trigger
```

### 3. Webhook (Existing)
```bash
POST https://abot.qub3.uk/webhook/alpaca-paper-bot
```

## 📊 How It Works

1. **Background Process**: Runs every 5 minutes during market hours (9 AM - 4 PM)
2. **Data Fetching**: Gets OHLCV data from Alpaca API
3. **Technical Analysis**: Calculates EMA, MACD, RSI, ADX, ATR indicators
4. **Signal Generation**: Determines BUY/SELL/HOLD signals based on strategy logic
5. **Order Execution**: Places orders via Alpaca API when signals are generated
6. **Risk Management**: Uses ATR-based position sizing and stop losses

## 🔍 Monitoring

### Console Logs
The application logs all strategy decisions:
```
📊 Fusion Pro cycle: completed
🚀 Fusion Pro strategy started in background
📊 Fusion Pro: Market closed, skipping cycle
```

### Status Endpoint Response
```json
{
  "symbol": "ASTS",
  "timeframe": "1D",
  "risk_pct": 0.5,
  "account_size": 10000,
  "last_entry_bar": null,
  "trades_today": 0,
  "cooldown_left": 0,
  "config": { ... }
}
```

## 🚀 Deployment Steps

1. **Add Environment Variables**: Add all FUSION_* variables to Dokploy
2. **Redeploy Application**: The strategy will start automatically
3. **Monitor Logs**: Check application logs for strategy activity
4. **Test Endpoints**: Use `/status/fusion_pro` to verify functionality

## ⚠️ Important Notes

- **Paper Trading**: Currently configured for Alpaca Paper Trading
- **Market Hours**: Strategy only runs during market hours (9 AM - 4 PM)
- **Risk Management**: Uses 0.5% risk per trade by default
- **Cooldown**: 10-bar cooldown after stop loss hits
- **Webhook Compatibility**: Existing webhook functionality remains unchanged

## 🎯 Strategy Logic

The Fusion Pro strategy replicates your PineScript logic:

1. **Trend Analysis**: EMA(50) vs EMA(200) crossover
2. **Momentum**: MACD histogram + RSI + ADX confirmation
3. **Volume Filter**: Volume > SMA(50) * 1.0
4. **Volatility Filter**: ATR% > 0.20%
5. **Risk Sizing**: Position size based on ATR * 1.5 stop loss
6. **Stop Loss**: ATR * 1.5
7. **Take Profit**: ATR * 1.0
8. **Trailing Stop**: Activates after 0.5 RR profit

## 🔧 Customization

You can customize any parameter by updating the environment variables in Dokploy. The strategy will automatically reload with new settings on the next cycle.

---

**Your webhook-trader is now a fully automated trading bot! 🚀**
