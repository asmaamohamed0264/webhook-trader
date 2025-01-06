from typing import Optional
from datetime import datetime

from sqlmodel import Field, Session, SQLModel, create_engine

from lib.env_vars import DB_URI, DB_ECHO


class AccountSnapshot(SQLModel, table=True):
    '''AccountSnapshot model for the database. Represents a snapshot of an account's equity and cash at a given time. Can be read from the API and doubles as a response model.'''
    id: Optional[int] = Field(default=None, primary_key=True)
    account_id: str
    name: str
    cash: float
    equity: float
    created_at: datetime = Field(default_factory=datetime.now)


class Order(SQLModel, table=True):
    '''Order model for the database. Doubles as the request model for the webhook endpoint.'''
    id: Optional[int] = Field(default=None, primary_key=True)
    nickname: Optional[str] = Field(nullable=True, default=None)
    ticker: str
    action: str  # buy, sell
    price: float
    market_position: str  # long, short, flat
    prev_market_position: Optional[str] = Field(
        nullable=True, default=None)  # long, short, flat
    interval: str
    leveraged: bool
    buying_power_pct: float  # percentage of buying power to use
    sl: Optional[float] = Field(nullable=True, default=None)
    tp: Optional[float] = Field(nullable=True, default=None)
    trailing_stop: Optional[float] = Field(nullable=True, default=None)
    high: Optional[float] = Field(nullable=True, default=None)
    low: Optional[float] = Field(nullable=True, default=None)
    close: Optional[float] = Field(nullable=True, default=None)
    open: Optional[float] = Field(nullable=True, default=None)
    volume: Optional[int] = Field(nullable=True, default=None)
    time: Optional[str] = Field(nullable=True, default=None)
    comment: Optional[str] = Field(nullable=True, default=None)
    alert_message: Optional[str] = Field(nullable=True, default=None)
    asset_class: Optional[str] = Field(nullable=False, default="stock")
    order_id: Optional[str] = Field(
        nullable=True, default=None)  # order ID from Alpaca
    created_at: Optional[datetime] = Field(default_factory=datetime.now)


connect_args = {"check_same_thread": False}
engine = create_engine(DB_URI, echo=DB_ECHO, connect_args=connect_args)


def create_db_and_tables():
    '''Creates the database and tables if they don't exist.'''
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
