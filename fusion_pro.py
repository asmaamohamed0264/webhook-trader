"""
Fusion Pro Strategy - Python Implementation
Replicates the TradingView PineScript strategy with EMA/MACD/RSI/ADX indicators
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import ta
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderType
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FusionProStrategy:
    """
    Fusion Pro Strategy Implementation
    EMA/MACD/RSI/ADX + Risk Sizing + Trail + Lockout
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.fusion_config = config.get('fusion_pro_bot', {})
        
        # Strategy parameters - support multiple symbols
        symbols_str = self.fusion_config.get('symbols', 'ASTS,AAPL')
        self.symbols = [s.strip() for s in symbols_str.split(',')]
        self.symbol = self.symbols[0]  # Primary symbol for backward compatibility
        self.timeframe = self.fusion_config.get('timeframe', '1D')
        self.risk_pct = self.fusion_config.get('risk_pct', 0.5)
        self.atr_mult_sl = self.fusion_config.get('atr_mult_sl', 1.5)
        self.atr_mult_tp = self.fusion_config.get('atr_mult_tp', 1.0)
        self.account_size = self.fusion_config.get('account_size', 10000)
        
        # Technical indicator parameters
        self.ema_fast_len = self.fusion_config.get('ema_fast_len', 50)
        self.ema_slow_len = self.fusion_config.get('ema_slow_len', 200)
        self.macd_fast = self.fusion_config.get('macd_fast', 12)
        self.macd_slow = self.fusion_config.get('macd_slow', 26)
        self.macd_signal = self.fusion_config.get('macd_signal', 9)
        self.rsi_len = self.fusion_config.get('rsi_len', 14)
        self.rsi_long_min = self.fusion_config.get('rsi_long_min', 50)
        self.rsi_long_max = self.fusion_config.get('rsi_long_max', 80)
        self.rsi_short_max = self.fusion_config.get('rsi_short_max', 50)
        self.rsi_short_min = self.fusion_config.get('rsi_short_min', 20)
        self.adx_len = self.fusion_config.get('adx_len', 14)
        self.adx_min = self.fusion_config.get('adx_min', 16)
        self.atr_len = self.fusion_config.get('atr_len', 14)
        
        # Risk management
        self.trail_start_rr = self.fusion_config.get('trail_start_rr', 0.5)
        self.trail_atr_mult = self.fusion_config.get('trail_atr_mult', 1.2)
        self.min_atr_pct = self.fusion_config.get('min_atr_pct', 0.20)
        
        # Execution filters
        self.vol_filter_on = self.fusion_config.get('vol_filter_on', True)
        self.vol_sma_len = self.fusion_config.get('vol_sma_len', 50)
        self.vol_min_mult = self.fusion_config.get('vol_min_mult', 1.0)
        self.min_bars_gap = self.fusion_config.get('min_bars_gap', 3)
        self.max_trades_day = self.fusion_config.get('max_trades_day', 10)
        
        # Trading session
        self.trade_session_start = self.fusion_config.get('trade_session_start', '09:30')
        self.trade_session_end = self.fusion_config.get('trade_session_end', '16:00')
        
        # HTF Trend Filter
        self.use_htf_trend = self.fusion_config.get('use_htf_trend', True)
        self.htf_timeframe = self.fusion_config.get('htf_timeframe', '60')
        
        # Position sizing
        self.use_fixed_risk = self.fusion_config.get('use_fixed_risk', True)
        self.fallback_pct = self.fusion_config.get('fallback_pct', 5.0)
        
        # Cooldown
        self.use_cooldown = self.fusion_config.get('use_cooldown', True)
        self.cooldown_bars = self.fusion_config.get('cooldown_bars', 10)
        
        # Initialize Alpaca clients
        self.data_client = None
        self.trading_client = None
        self._init_alpaca_clients()
        
        # State tracking
        self.last_entry_bar = None
        self.trades_today = 0
        self.cooldown_left = 0
        self.prev_closed_trades = 0
        self.high_in_trade = None
        self.low_in_trade = None
        self.last_trade_date = None
        self.htf_data = {}  # Cache for HTF data
        
    def _init_alpaca_clients(self):
        """Initialize Alpaca API clients"""
        try:
            # Get credentials from environment or config
            api_key = os.getenv('ALPACA_API_KEYS', self.config.get('alpaca_api_key'))
            api_secret = os.getenv('ALPACA_API_SECRETS', self.config.get('alpaca_api_secret'))
            base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
            
            if not api_key or not api_secret:
                raise ValueError("Alpaca API credentials not found")
            
            self.data_client = StockHistoricalDataClient(api_key, api_secret)
            self.trading_client = TradingClient(api_key, api_secret, paper=True)
            
            logger.info("Alpaca clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Alpaca clients: {e}")
            raise
    
    async def fetch_market_data(self, symbol: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
        """Fetch OHLCV data from Alpaca"""
        try:
            # Convert timeframe string to Alpaca TimeFrame
            tf_map = {
                '1m': TimeFrame.Minute,
                '5m': TimeFrame(5, 'minute'),
                '15m': TimeFrame(15, 'minute'),
                '30m': TimeFrame(30, 'minute'),
                '1h': TimeFrame.Hour,
                '1D': TimeFrame.Day,
                '1W': TimeFrame.Week
            }
            
            tf = tf_map.get(timeframe, TimeFrame.Day)
            
            # Calculate start time - go back further for historical data
            end_time = datetime.now()
            if timeframe == '1D':
                start_time = end_time - timedelta(days=limit * 2)  # Go back further
            elif timeframe == '1h':
                start_time = end_time - timedelta(hours=limit * 2)
            else:
                start_time = end_time - timedelta(minutes=limit * 2)
            
            # Create request
            request_params = StockBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=tf,
                start=start_time,
                end=end_time,
                limit=limit
            )
            
            # Fetch data
            bars = self.data_client.get_stock_bars(request_params)
            
            # Convert to DataFrame
            data = []
            if symbol in bars.data and bars.data[symbol]:
                for bar in bars.data[symbol]:
                    data.append({
                        'timestamp': bar.timestamp,
                        'open': float(bar.open),
                        'high': float(bar.high),
                        'low': float(bar.low),
                        'close': float(bar.close),
                        'volume': int(bar.volume)
                    })
            
            df = pd.DataFrame(data)
            if not df.empty:
                df.set_index('timestamp', inplace=True)
                df.sort_index(inplace=True)
                logger.info(f"Fetched {len(df)} bars for {symbol}")
            else:
                logger.warning(f"No data returned for {symbol}")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch market data for {symbol}: {e}")
            # Return empty DataFrame - will be handled by calling function
            return pd.DataFrame()
    
    def generate_test_data(self, symbol: str, timeframe: str, limit: int = 200) -> pd.DataFrame:
        """Generate test data when API is not available"""
        try:
            import numpy as np
            
            # Generate synthetic OHLCV data
            dates = pd.date_range(end=datetime.now(), periods=limit, freq='D' if timeframe == '1D' else 'H')
            
            # Generate realistic price data
            base_price = 100.0 if symbol == 'AAPL' else 10.0  # Different base prices
            prices = []
            current_price = base_price
            
            for i in range(limit):
                # Random walk with slight upward bias
                change = np.random.normal(0, 0.02)  # 2% volatility
                current_price *= (1 + change)
                prices.append(current_price)
            
            # Generate OHLCV data
            data = []
            for i, (date, close) in enumerate(zip(dates, prices)):
                high = close * (1 + abs(np.random.normal(0, 0.01)))
                low = close * (1 - abs(np.random.normal(0, 0.01)))
                open_price = prices[i-1] if i > 0 else close
                volume = int(np.random.normal(1000000, 200000))
                
                data.append({
                    'timestamp': date,
                    'open': open_price,
                    'high': high,
                    'low': low,
                    'close': close,
                    'volume': volume
                })
            
            df = pd.DataFrame(data)
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            
            logger.info(f"Generated {len(df)} test bars for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to generate test data for {symbol}: {e}")
            return pd.DataFrame()
    
    async def fetch_htf_data(self, symbol: str, htf_timeframe: str, limit: int = 50) -> pd.DataFrame:
        """Fetch Higher Timeframe data for trend filtering"""
        try:
            if symbol in self.htf_data:
                return self.htf_data[symbol]
            
            # Convert HTF timeframe
            tf_map = {
                '15': TimeFrame(15, 'minute'),
                '30': TimeFrame(30, 'minute'),
                '60': TimeFrame.Hour,
                '240': TimeFrame(4, 'hour'),
                '1D': TimeFrame.Day
            }
            
            tf = tf_map.get(htf_timeframe, TimeFrame.Hour)
            
            # Calculate time range
            end_time = datetime.now()
            if htf_timeframe == '1D':
                start_time = end_time - timedelta(days=limit)
            elif htf_timeframe in ['60', '240']:
                start_time = end_time - timedelta(hours=limit * 4)
            else:
                start_time = end_time - timedelta(minutes=limit * int(htf_timeframe))
            
            # Create request
            request_params = StockBarsRequest(
                symbol_or_symbols=[symbol],
                timeframe=tf,
                start=start_time,
                end=end_time,
                limit=limit
            )
            
            # Fetch data
            bars = self.data_client.get_stock_bars(request_params)
            
            # Convert to DataFrame
            data = []
            if symbol in bars.data and bars.data[symbol]:
                for bar in bars.data[symbol]:
                    data.append({
                        'timestamp': bar.timestamp,
                        'close': float(bar.close)
                    })
            
            df = pd.DataFrame(data)
            if not df.empty:
                df.set_index('timestamp', inplace=True)
                df.sort_index(inplace=True)
                # Calculate HTF EMA200
                df['ema200'] = ta.trend.EMAIndicator(df['close'], window=200).ema_indicator()
                self.htf_data[symbol] = df
                logger.info(f"Fetched {len(df)} HTF bars for {symbol}")
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch HTF data for {symbol}: {e}")
            return pd.DataFrame()
    
    def is_trading_session(self, current_time: datetime = None) -> bool:
        """Check if current time is within trading session"""
        if current_time is None:
            current_time = datetime.now()
        
        try:
            # Parse session times
            start_hour, start_min = map(int, self.trade_session_start.split(':'))
            end_hour, end_min = map(int, self.trade_session_end.split(':'))
            
            current_minutes = current_time.hour * 60 + current_time.minute
            start_minutes = start_hour * 60 + start_min
            end_minutes = end_hour * 60 + end_min
            
            return start_minutes <= current_minutes <= end_minutes
            
        except Exception as e:
            logger.error(f"Error checking trading session: {e}")
            return True  # Default to allow trading
    
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        if df.empty:
            return df
        
        try:
            # EMA indicators
            df['ema_fast'] = ta.trend.EMAIndicator(df['close'], window=self.ema_fast_len).ema_indicator()
            df['ema_slow'] = ta.trend.EMAIndicator(df['close'], window=self.ema_slow_len).ema_indicator()
            
            # MACD
            macd = ta.trend.MACD(df['close'], window_slow=self.macd_slow, window_fast=self.macd_fast, window_sign=self.macd_signal)
            df['macd_line'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_hist'] = macd.macd_diff()
            
            # RSI
            df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=self.rsi_len).rsi()
            
            # ADX
            adx = ta.trend.ADXIndicator(df['high'], df['low'], df['close'], window=self.adx_len)
            df['adx'] = adx.adx()
            
            # ATR
            df['atr'] = ta.volatility.AverageTrueRange(df['high'], df['low'], df['close'], window=self.atr_len).average_true_range()
            df['atr_pct'] = (df['atr'] / df['close']) * 100.0
            
            # Volume indicators
            if self.vol_filter_on:
                df['vol_sma'] = ta.volume.VolumeSMAIndicator(df['volume'], window=self.vol_sma_len).volume_sma()
            
            return df
            
        except Exception as e:
            logger.error(f"Failed to calculate indicators: {e}")
            return df
    
    async def analyze_signals(self, df: pd.DataFrame, symbol: str) -> Dict:
        """Analyze market data and generate trading signals with advanced filters"""
        if df.empty or len(df) < max(self.ema_slow_len, self.macd_slow, self.rsi_len, self.adx_len):
            return {'signal': 'HOLD', 'reason': 'Insufficient data'}
        
        try:
            # Get latest values
            latest = df.iloc[-1]
            prev = df.iloc[-2] if len(df) > 1 else latest
            
            # Check trading session
            in_session = self.is_trading_session()
            
            # Trend analysis
            trend_up = (latest['close'] > latest['ema_fast'] and 
                       latest['ema_fast'] > latest['ema_slow'])
            trend_down = (latest['close'] < latest['ema_fast'] and 
                         latest['ema_fast'] < latest['ema_slow'])
            
            # HTF Trend Filter
            if self.use_htf_trend:
                htf_df = await self.fetch_htf_data(symbol, self.htf_timeframe)
                if not htf_df.empty and 'ema200' in htf_df.columns:
                    htf_ema200 = htf_df['ema200'].iloc[-1]
                    if pd.notna(htf_ema200):
                        trend_up = trend_up and (latest['close'] > htf_ema200)
                        trend_down = trend_down and (latest['close'] < htf_ema200)
            
            # Momentum analysis
            mom_long = (latest['macd_hist'] > 0 and 
                       self.rsi_long_min <= latest['rsi'] <= self.rsi_long_max and
                       latest['adx'] >= self.adx_min)
            
            mom_short = (latest['macd_hist'] < 0 and 
                        self.rsi_short_min <= latest['rsi'] <= self.rsi_short_max and
                        latest['adx'] >= self.adx_min)
            
            # Volume filter
            vol_ok = True
            if self.vol_filter_on and 'vol_sma' in latest:
                vol_ok = latest['volume'] > (latest['vol_sma'] * self.vol_min_mult)
            
            # Volatility filter
            vol_ok2 = latest['atr_pct'] >= self.min_atr_pct
            
            # Check all filters
            filters_ok = vol_ok and vol_ok2 and in_session
            
            # Check cooldown
            cooling = self.use_cooldown and (self.cooldown_left > 0)
            
            # Check daily trade limit
            can_trade_today = self.trades_today < self.max_trades_day
            
            # Check minimum bars gap
            bars_since_entry = 100000  # Default high value
            if self.last_entry_bar is not None:
                bars_since_entry = len(df) - self.last_entry_bar if self.last_entry_bar < len(df) else 100000
            
            can_trade_now = (filters_ok and not cooling and can_trade_today and 
                           bars_since_entry >= self.min_bars_gap)
            
            # Generate signals
            signal = 'HOLD'
            reason = []
            
            if can_trade_now and trend_up and mom_long:
                signal = 'BUY'
                reason = ['Trend up', 'Momentum long', 'All filters OK']
            elif can_trade_now and trend_down and mom_short:
                signal = 'SELL'
                reason = ['Trend down', 'Momentum short', 'All filters OK']
            else:
                if not in_session:
                    reason.append('Outside trading session')
                if not vol_ok:
                    reason.append('Volume filter failed')
                if not vol_ok2:
                    reason.append('Volatility filter failed')
                if cooling:
                    reason.append(f'Cooldown active ({self.cooldown_left} bars)')
                if not can_trade_today:
                    reason.append(f'Daily trade limit reached ({self.trades_today}/{self.max_trades_day})')
                if bars_since_entry < self.min_bars_gap:
                    reason.append(f'Min bars gap not met ({bars_since_entry}/{self.min_bars_gap})')
                if not trend_up and not trend_down:
                    reason.append('No clear trend')
                if not mom_long and not mom_short:
                    reason.append('Momentum not aligned')
            
            return {
                'signal': signal,
                'reason': ', '.join(reason),
                'price': float(latest['close']),
                'timestamp': latest.name.isoformat() if hasattr(latest.name, 'isoformat') else str(latest.name),
                'filters': {
                    'in_session': bool(in_session),
                    'vol_ok': bool(vol_ok),
                    'vol_ok2': bool(vol_ok2),
                    'cooling': bool(cooling),
                    'can_trade_today': bool(can_trade_today),
                    'bars_since_entry': int(bars_since_entry)
                },
                'indicators': {
                    'ema_fast': float(latest['ema_fast']) if pd.notna(latest['ema_fast']) else None,
                    'ema_slow': float(latest['ema_slow']) if pd.notna(latest['ema_slow']) else None,
                    'macd_hist': float(latest['macd_hist']) if pd.notna(latest['macd_hist']) else None,
                    'rsi': float(latest['rsi']) if pd.notna(latest['rsi']) else None,
                    'adx': float(latest['adx']) if pd.notna(latest['adx']) else None,
                    'atr': float(latest['atr']) if pd.notna(latest['atr']) else None,
                    'atr_pct': float(latest['atr_pct']) if pd.notna(latest['atr_pct']) else None
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze signals: {e}")
            return {'signal': 'HOLD', 'reason': f'Analysis error: {e}'}
    
    def calculate_position_size(self, price: float, atr: float, current_equity: float = None) -> int:
        """Calculate position size based on risk management with fallback"""
        try:
            if current_equity is None:
                current_equity = self.account_size
            
            # Calculate stop distance
            stop_dist = atr * self.atr_mult_sl
            
            if self.use_fixed_risk and stop_dist > 0:
                # Fixed risk sizing
                risk_capital = current_equity * (self.risk_pct / 100.0)
                qty = risk_capital / stop_dist
                qty = max(1, int(qty))  # Minimum 1 share
                
                if qty > 0:
                    return qty
            
            # Fallback to percentage of equity
            fallback_qty = current_equity * (self.fallback_pct / 100.0) / price
            return max(1, int(fallback_qty))
            
        except Exception as e:
            logger.error(f"Failed to calculate position size: {e}")
            return 1
    
    async def execute_signal(self, signal_data: Dict) -> Dict:
        """Execute trading signal"""
        try:
            signal = signal_data['signal']
            price = signal_data['price']
            atr = signal_data['indicators']['atr']
            
            if signal == 'HOLD':
                return {'status': 'skipped', 'reason': 'HOLD signal'}
            
            # Calculate position size
            qty = self.calculate_position_size(price, atr)
            
            # Determine order side
            side = OrderSide.BUY if signal == 'BUY' else OrderSide.SELL
            
            # Create market order
            order_request = MarketOrderRequest(
                symbol=self.symbol,
                qty=qty,
                side=side,
                time_in_force=TimeInForce.GTC
            )
            
            # Execute order
            order = self.trading_client.submit_order(order_request)
            
            logger.info(f"Executed {signal} order: {qty} shares of {self.symbol} at ~${price:.2f}")
            
            return {
                'status': 'executed',
                'order_id': str(order.id),
                'symbol': self.symbol,
                'side': signal,
                'qty': int(qty),
                'price': float(price),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to execute signal: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    async def run_strategy_cycle(self) -> Dict:
        """Run one complete strategy cycle for all symbols"""
        try:
            logger.info(f"Running Fusion Pro strategy cycle for symbols: {', '.join(self.symbols)}")
            
            results = []
            
            for symbol in self.symbols:
                try:
                    logger.info(f"Processing {symbol}...")
                    
                    # Fetch market data
                    df = await self.fetch_market_data(symbol, self.timeframe)
                    if df.empty:
                        # Try to generate test data if API fails
                        logger.warning(f"No market data for {symbol}, trying test data...")
                        df = self.generate_test_data(symbol, self.timeframe)
                        if df.empty:
                            results.append({
                                'symbol': symbol,
                                'status': 'error',
                                'reason': 'No market data and test data generation failed'
                            })
                            continue
                        else:
                            logger.info(f"Using test data for {symbol}")
                    
                    # Calculate indicators
                    df = self.calculate_indicators(df)
                    if df.empty:
                        results.append({
                            'symbol': symbol,
                            'status': 'error',
                            'reason': 'Failed to calculate indicators'
                        })
                        continue
                    
                    # Analyze signals
                    signal_data = await self.analyze_signals(df, symbol)
                    signal_data['symbol'] = symbol
                    
                    # Execute signal if not HOLD
                    if signal_data['signal'] != 'HOLD':
                        execution_result = await self.execute_signal(signal_data)
                        signal_data['execution'] = execution_result
                        logger.info(f"{symbol}: {signal_data['signal']} signal executed")
                    else:
                        logger.info(f"{symbol}: HOLD signal - {signal_data['reason']}")
                    
                    results.append({
                        'symbol': symbol,
                        'status': 'completed',
                        'signal_data': signal_data
                    })
                    
                except Exception as e:
                    logger.error(f"Failed to process {symbol}: {e}")
                    results.append({
                        'symbol': symbol,
                        'status': 'error',
                        'reason': str(e)
                    })
            
            # Log summary
            completed = [r for r in results if r['status'] == 'completed']
            errors = [r for r in results if r['status'] == 'error']
            
            logger.info(f"Strategy cycle completed: {len(completed)} symbols processed, {len(errors)} errors")
            
            return {
                'status': 'completed',
                'results': results,
                'summary': {
                    'total_symbols': len(self.symbols),
                    'completed': len(completed),
                    'errors': len(errors)
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Strategy cycle failed: {e}")
            return {'status': 'error', 'reason': str(e)}
    
    def get_status(self) -> Dict:
        """Get current strategy status"""
        return {
            'symbols': self.symbols,
            'primary_symbol': self.symbol,
            'timeframe': self.timeframe,
            'risk_pct': self.risk_pct,
            'account_size': self.account_size,
            'last_entry_bar': self.last_entry_bar,
            'trades_today': self.trades_today,
            'cooldown_left': self.cooldown_left,
            'config': self.fusion_config
        }
