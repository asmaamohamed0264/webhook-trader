from typing import Annotated
from contextlib import asynccontextmanager
import asyncio
import json
import os
from datetime import datetime

from fastapi import FastAPI, Depends, Request, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from lib.api_models import Position
from lib.constants import ORIGINS, WHITELIST as IP_WHITELIST
from lib.db import get_session, create_db_and_tables, AccountSnapshot, Order
from lib.env_vars import get_accounts, TEST_MODE
from lib.utils import (exec_trade, get_client_ip, get_current_position, close_position, get_latest_quote,
                       get_trading_client, is_extended_hours, get_trading_clients)
from fusion_pro import FusionProStrategy


SessionDep = Annotated[Session, Depends(get_session)]


# Global strategy instance
fusion_strategy = None
strategy_task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    '''Creates a lifespan for items that should be run at startup and shutdown.
Startup tasks should be placed before the yield, and shutdown tasks should be placed after the yield.'''
    global fusion_strategy, strategy_task
    
    # Initialize database
    create_db_and_tables()
    
    # Initialize Fusion Pro strategy
    try:
        config = load_config()
        fusion_strategy = FusionProStrategy(config)
        
        # Start background strategy task
        strategy_task = asyncio.create_task(run_fusion_pro_strategy())
        print("🚀 Fusion Pro strategy started in background")
        
    except Exception as e:
        print(f"⚠️ Failed to start Fusion Pro strategy: {e}")
        fusion_strategy = None
    
    yield
    
    # Cleanup
    if strategy_task:
        strategy_task.cancel()
        try:
            await strategy_task
        except asyncio.CancelledError:
            pass
        print("🛑 Fusion Pro strategy stopped")


app = FastAPI(name="Webhook Trader", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def background_snapshot(session: Session, exclude: list[str] = []):
    clients = get_trading_clients()
    for name, client in clients.items():
        if name in exclude:
            continue
        account = client.get_account()
        snapshot = AccountSnapshot(
            account_id=str(account.id),
            name=name,
            cash=float(account.cash),
            equity=float(account.equity),
        )
        session.add(snapshot)
    session.commit()


@app.get('/account/{name}')
async def get_account(name: str):
    client = get_trading_client(name)
    if not client:
        # return a 404
        return JSONResponse(content={"error": "Account not found"}, status_code=status.HTTP_404_NOT_FOUND)
    account = client.get_account()
    return account


@app.get("/snapshots", response_model=list[AccountSnapshot])
async def get_snapshots(session: SessionDep):
    # Get the last 12 snapshots for each account
    limit = 12 * len(get_accounts())
    statement = select(AccountSnapshot).order_by(
        AccountSnapshot.created_at.desc()).limit(limit)
    snapshots = session.exec(statement).all()

    return snapshots


@app.get("/snapshot/{name}", response_model=AccountSnapshot)
async def get_snapshot(name: str, session: SessionDep, background_task: BackgroundTasks):
    # create and return a snapshot for the account
    # save the new snapshot to the database
    client = get_trading_client(name)
    account = client.get_account()
    snapshot = AccountSnapshot(
        account_id=str(account.id),
        name=name,
        cash=float(account.cash),
        equity=float(account.equity),
    )
    session.add(snapshot)
    session.commit()
    session.refresh(snapshot)
    background_task.add_task(
        background_snapshot, session=session, exclude=[name])
    return snapshot


@app.get("/positions/{name}", response_model=list[Position])
async def positions(name: str, req: Request):
    ip = get_client_ip(req)
    if type(ip) is str and ip not in IP_WHITELIST:
        return JSONResponse(content={"error": f"IP '{ip}' not in whitelist"}, status_code=status.HTTP_401_UNAUTHORIZED)
    elif type(ip) is list and all(x not in IP_WHITELIST for x in ip):
        return JSONResponse(content={"error": f"IPs '{ip}' not in whitelist"}, status_code=status.HTTP_401_UNAUTHORIZED)
    client = get_trading_client(name)
    alpaca_positions = client.get_all_positions()
    positions = [Position.from_alpaca(p) for p in alpaca_positions]
    return positions


@app.post("/webhook/{name}")
async def webhook(name: str, order: Order, session: SessionDep, req: Request, background_task: BackgroundTasks):
    # first, check if the IP is in the whitelist
    ip = get_client_ip(req)

    if type(ip) is str and ip not in IP_WHITELIST:
        return JSONResponse(content={"error": f"IP '{ip}' not in whitelist"}, status_code=status.HTTP_401_UNAUTHORIZED)
    elif type(ip) is list and all(x not in IP_WHITELIST for x in ip):
        return JSONResponse(content={"error": f"IPs '{ip}' not in whitelist"}, status_code=status.HTTP_401_UNAUTHORIZED)

    if not order.nickname:
        order.nickname = name
    if not order.max_slippage:
        order.max_slippage = 0
    # log the order
    session.add(order)
    session.commit()
    # if we're in test mode, we're done. Echo the order back.
    if TEST_MODE:
        session.refresh(order)
        return order

    print(get_accounts().keys())
    # otherwise, we need to forward to alpaca and add the order ID to the order
    client = get_trading_client(name)
    if not client:
        return JSONResponse(content={"error": f"Account '{name}' not found"}, status_code=status.HTTP_404_NOT_FOUND)
    # the webhooks should only fire if we're in extended hours or the market is open
    # so we don't need to check if we can trade
    # we do need to check if we're in extended hours, as the order type will be different
    extended_hours = is_extended_hours(client)

    # check if we've hit 3 day trades with equity under $25k
    # this is needed because we can always buy, but selling gets restricted if we hit the limit
    # so we should prevent the order from going through so that we're not in a position where we can't sell
    account = client.get_account()
    if account.daytrade_count >= 3 and float(account.equity) < 25_000:
        return JSONResponse(content={"error": "Pattern day trader"}, status_code=status.HTTP_429_TOO_MANY_REQUESTS)

    position = get_current_position(client, order.ticker)
    # if we don't hold the position, simply long or short the position
    if not position:
        if order.max_slippage > 0:
            # do a slippage check
            quote = get_latest_quote(order.ticker, order.asset_class)
            # if we are selling (shorting), use bid
            # if we are buying (longing), use ask
            price = quote.bid_price if order.action == "sell" else quote.ask_price
            # get the absolute value of the slippage
            slippage = abs((price - order.price) / order.price)
            if slippage > order.max_slippage:
                return JSONResponse(content={"error": "Slippage too high"}, status_code=status.HTTP_412_PRECONDITION_FAILED)

        new_order = exec_trade(client, order, extended_hours)
        order.order_id = str(new_order.id)
        session.commit()
        session.refresh(order)
        background_task.add_task(background_snapshot, session=session)
        return order
    else:
        if not order.pyramiding:
            # if the position is flat, or the same as what we already have, we're done
            if position.side == order.market_position or order.market_position == "flat":
                background_task.add_task(background_snapshot, session=session)
                return order
            # at this point, we have to close the position and open a new one regardless of the market position
            close_position(client, order.ticker, wait_for_fill=True)
        # once the existing position is closed, we can open a new one
        new_order = exec_trade(client, order, extended_hours)
        order.order_id = str(new_order.id)
        session.commit()
        session.refresh(order)
        background_task.add_task(background_snapshot, session=session)
        return order


# Helper functions for Fusion Pro strategy
def load_config():
    """Load configuration from environment variables and config file"""
    config = {}
    
    # Load from environment variables
    config['alpaca_api_key'] = os.getenv('ALPACA_API_KEYS')
    config['alpaca_api_secret'] = os.getenv('ALPACA_API_SECRETS')
    config['alpaca_base_url'] = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
    
    # Load Fusion Pro configuration
    fusion_config = {
        'symbol': os.getenv('FUSION_SYMBOL', 'ASTS'),
        'timeframe': os.getenv('FUSION_TIMEFRAME', '1D'),
        'risk_pct': float(os.getenv('FUSION_RISK_PCT', '0.5')),
        'atr_mult_sl': float(os.getenv('FUSION_ATR_MULT_SL', '1.5')),
        'atr_mult_tp': float(os.getenv('FUSION_ATR_MULT_TP', '1.0')),
        'account_size': float(os.getenv('FUSION_ACCOUNT_SIZE', '10000')),
        'ema_fast_len': int(os.getenv('FUSION_EMA_FAST', '50')),
        'ema_slow_len': int(os.getenv('FUSION_EMA_SLOW', '200')),
        'macd_fast': int(os.getenv('FUSION_MACD_FAST', '12')),
        'macd_slow': int(os.getenv('FUSION_MACD_SLOW', '26')),
        'macd_signal': int(os.getenv('FUSION_MACD_SIGNAL', '9')),
        'rsi_len': int(os.getenv('FUSION_RSI_LEN', '14')),
        'rsi_long_min': int(os.getenv('FUSION_RSI_LONG_MIN', '50')),
        'rsi_long_max': int(os.getenv('FUSION_RSI_LONG_MAX', '80')),
        'rsi_short_max': int(os.getenv('FUSION_RSI_SHORT_MAX', '50')),
        'rsi_short_min': int(os.getenv('FUSION_RSI_SHORT_MIN', '20')),
        'adx_len': int(os.getenv('FUSION_ADX_LEN', '14')),
        'adx_min': int(os.getenv('FUSION_ADX_MIN', '16')),
        'atr_len': int(os.getenv('FUSION_ATR_LEN', '14')),
        'trail_start_rr': float(os.getenv('FUSION_TRAIL_START_RR', '0.5')),
        'trail_atr_mult': float(os.getenv('FUSION_TRAIL_ATR_MULT', '1.2')),
        'min_atr_pct': float(os.getenv('FUSION_MIN_ATR_PCT', '0.20')),
        'vol_filter_on': os.getenv('FUSION_VOL_FILTER_ON', 'true').lower() == 'true',
        'vol_sma_len': int(os.getenv('FUSION_VOL_SMA_LEN', '50')),
        'vol_min_mult': float(os.getenv('FUSION_VOL_MIN_MULT', '1.0')),
        'min_bars_gap': int(os.getenv('FUSION_MIN_BARS_GAP', '3')),
        'max_trades_day': int(os.getenv('FUSION_MAX_TRADES_DAY', '10')),
        'use_cooldown': os.getenv('FUSION_USE_COOLDOWN', 'true').lower() == 'true',
        'cooldown_bars': int(os.getenv('FUSION_COOLDOWN_BARS', '10'))
    }
    
    config['fusion_pro_bot'] = fusion_config
    return config

async def run_fusion_pro_strategy():
    """Background task to run Fusion Pro strategy periodically"""
    global fusion_strategy
    
    if not fusion_strategy:
        print("⚠️ Fusion Pro strategy not initialized")
        return
    
    # Run every 5 minutes during market hours
    while True:
        try:
            # Check if market is open (simplified check)
            now = datetime.now()
            if 9 <= now.hour <= 16:  # Market hours (simplified)
                result = await fusion_strategy.run_strategy_cycle()
                print(f"📊 Fusion Pro cycle: {result.get('status', 'unknown')}")
            else:
                print("📊 Fusion Pro: Market closed, skipping cycle")
            
            # Wait 5 minutes
            await asyncio.sleep(300)
            
        except asyncio.CancelledError:
            print("🛑 Fusion Pro strategy task cancelled")
            break
        except Exception as e:
            print(f"❌ Fusion Pro strategy error: {e}")
            await asyncio.sleep(60)  # Wait 1 minute on error

# Fusion Pro monitoring endpoint
@app.get("/status/fusion_pro")
async def get_fusion_pro_status():
    """Get Fusion Pro strategy status"""
    global fusion_strategy
    
    if not fusion_strategy:
        return JSONResponse(
            content={"error": "Fusion Pro strategy not initialized"},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    try:
        status_data = fusion_strategy.get_status()
        return JSONResponse(content=status_data)
    except Exception as e:
        return JSONResponse(
            content={"error": f"Failed to get status: {e}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# Manual strategy trigger endpoint
@app.post("/fusion_pro/trigger")
async def trigger_fusion_pro():
    """Manually trigger Fusion Pro strategy cycle"""
    global fusion_strategy
    
    if not fusion_strategy:
        return JSONResponse(
            content={"error": "Fusion Pro strategy not initialized"},
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    try:
        result = await fusion_strategy.run_strategy_cycle()
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(
            content={"error": f"Strategy execution failed: {e}"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

app.mount("/", StaticFiles(directory="public", html=True), name="public")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
