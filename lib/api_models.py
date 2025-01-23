from pydantic import BaseModel
from alpaca.trading.models import Position as AlpacaPosition

class Position(BaseModel):
    asset_id: str
    symbol: str
    exchange: str
    asset_class: str
    asset_marginable: bool
    qty: float
    avg_entry_price: float
    side: str
    market_value: float
    cost_basis: float
    unrealized_pl: float
    unrealized_plpc: float
    unrealized_intraday_pl: float
    unrealized_intraday_plpc: float
    current_price: float
    lastday_price: float
    change_today: float
    qty_available: float

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            asset_id=data["asset_id"],
            symbol=data["symbol"],
            exchange=data["exchange"],
            asset_class=data["asset_class"],
            asset_marginable=data["asset_marginable"],
            qty=float(data["qty"]),
            avg_entry_price=float(data["avg_entry_price"]),
            side=data["side"],
            market_value=float(data["market_value"]),
            cost_basis=float(data["cost_basis"]),
            unrealized_pl=float(data["unrealized_pl"]),
            unrealized_plpc=float(data["unrealized_plpc"]),
            unrealized_intraday_pl=float(data["unrealized_intraday_pl"]),
            unrealized_intraday_plpc=float(data["unrealized_intraday_plpc"]),
            current_price=float(data["current_price"]),
            lastday_price=float(data["lastday_price"]),
            change_today=float(data["change_today"]),
            qty_available=float(data["qty_available"])
        )
    
    @classmethod
    def from_alpaca(cls, position: AlpacaPosition):
        return cls(
            asset_id=str(position.asset_id),
            symbol=position.symbol,
            exchange=position.exchange,
            asset_class=position.asset_class,
            asset_marginable=position.asset_marginable,
            qty=float(position.qty),
            avg_entry_price=float(position.avg_entry_price),
            side=position.side,
            market_value=float(position.market_value),
            cost_basis=float(position.cost_basis),
            unrealized_pl=float(position.unrealized_pl),
            unrealized_plpc=float(position.unrealized_plpc),
            unrealized_intraday_pl=float(position.unrealized_intraday_pl),
            unrealized_intraday_plpc=float(position.unrealized_intraday_plpc),
            current_price=float(position.current_price),
            lastday_price=float(position.lastday_price),
            change_today=float(position.change_today),
            qty_available=float(position.qty_available)
        )
