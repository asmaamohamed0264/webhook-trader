import time

from fastapi import Request
from alpaca.trading import Position, Order as AlpacaOrder
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus
from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest, ClosePositionRequest

from lib.db import Order
from lib.env_vars import get_accounts, get_account

FINISHED_STATUSES = [OrderStatus.FILLED, OrderStatus.CANCELED,
                     OrderStatus.EXPIRED, OrderStatus.DONE_FOR_DAY]


def get_client_ip(request: Request):
    '''Checks for the real client IP address in the request headers from a number of common sources.'''
    headers = [
        'X-Real-IP',
        'X-Forwarded-For',
        'CF-Connecting-IP',
        'True-Client-IP',
        'X-Client-IP',
        'X-Cluster-Client-IP',
        'X-Forwarded',
        'Forwarded-For',
        'Forwarded',
        'X-Forwarded-Host',
    ]
    for header in headers:
        ip = request.headers.get(header)
        if ip:
            return ip

    return request.client.host


def get_trading_clients() -> dict[str, TradingClient]:
    '''Returns a dictionary using the name as the key and the TradingClient object as the value.'''
    accounts = get_accounts()
    clients = {}
    for name, creds in accounts.items():
        clients[name] = TradingClient(
            creds.api_key, creds.api_secret, paper=creds.paper)
    return clients


def get_trading_client(name: str) -> TradingClient:
    creds = get_account(name)
    return TradingClient(creds.api_key, creds.api_secret, paper=creds.paper)


def is_extended_hours(client: TradingClient) -> bool:
    '''Returns true if the market is closed but extended hours are active.'''
    clock = client.get_clock()
    if clock.is_open:
        return False

    # check if the time is before 8pm or after 4am
    current_time = clock.timestamp
    return current_time.hour < 20 or current_time.hour >= 4


def can_trade(client: TradingClient) -> bool:
    '''Returns true if the market is open or extended hours are active.'''
    clock = client.get_clock()
    return clock.is_open or is_extended_hours(client)


def exec_trade(client: TradingClient, order: Order, extended_hours: bool = False, wait_for_fill: bool = False) -> AlpacaOrder:
    account = client.get_account()
    # we're doing notional orders, but we need to know how much.
    # If its a stock and not leveraged, get our regular buying power and multiply by the percentage
    # If its a stock and leveraged or crypto, get our non marginable buying power and multiply by the percentage
    buying_power = float(account.buying_power)
    if order.leveraged or order.asset_class == "crypto":
        buying_power = float(account.non_marginable_buying_power)

    # cannot have more than 2 decimal places
    notional = round(buying_power * order.buying_power_pct, 2)

    # if the value is less than a dollar, we can't trade. Throw bad request
    if notional < 1:
        raise Exception("Notional value is less than $1. Cannot trade.")

    order_req = MarketOrderRequest(
        symbol=order.ticker,
        notional=notional,
        time_in_force=TimeInForce.DAY,
        side=OrderSide.BUY if order.action == "buy" else OrderSide.SELL,
    )

    if extended_hours:
        order_req = LimitOrderRequest(
            symbol=order.ticker,
            qty=round(notional / order.price, 0),
            time_in_force=TimeInForce.DAY,
            side=OrderSide.BUY if order.action == "buy" else OrderSide.SELL,
            limit_price=order.high,
        )

    if not wait_for_fill:
        return client.submit_order(order_req)

    alpaca_order = client.submit_order(order_req)

    while alpaca_order.status not in FINISHED_STATUSES:
        if alpaca_order.status != OrderStatus.NEW:
            time.sleep(0.25)
        alpaca_order = client.get_order_by_id(alpaca_order.id)

    return alpaca_order


def get_current_position(client: TradingClient, ticker: str) -> Position | None:
    position = None
    try:
        position = client.get_open_position(ticker)
    except Exception as e:
        pass
    return position


def close_position(client: TradingClient, ticker: str, percentage: float = 100.0, wait_for_fill: bool = False) -> AlpacaOrder | None:
    position = None
    try:
        position = client.close_position(ticker, ClosePositionRequest(
            percentage=percentage
        ))
        if wait_for_fill:
            while position.status not in FINISHED_STATUSES:
                if position.status != OrderStatus.NEW:
                    time.sleep(0.25)
                position = client.get_order_by_id(position.id)
    except Exception as e:
        pass
    return position
