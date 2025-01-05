import os

from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# plain string variables
DB_URI = os.getenv("DB_URI", "sqlite:///trader.db")

# boolean variables
# if TEST_MODE is set, don't execute trades and only log them
TEST_MODE = os.getenv("TEST_MODE", "False") == "True"
DB_ECHO = os.getenv("DB_ECHO", "False") == "True"

# list variables
# ALPACA_API_KEYS, ALPACA_API_SECRETS, and ALPACA_NAMES are all comma-separated strings
# ALPACA_PAPER is a comma separate list of ints
# all variables should be the same length once split, and all trailing empty strings should be removed
ALPACA_API_KEYS = os.getenv("ALPACA_API_KEYS").split(",")
ALPACA_API_SECRETS = os.getenv("ALPACA_API_SECRETS").split(",")
ALPACA_NAMES = os.getenv("ALPACA_NAMES").split(",")
ALPACA_PAPER = [int(x) for x in os.getenv("ALPACA_PAPER").split(",")]
IP_WHITELIST = os.getenv("IP_WHITELIST", "").split(",")

# remove any trailing empty strings
ALPACA_API_KEYS = [x for x in ALPACA_API_KEYS if x]
ALPACA_API_SECRETS = [x for x in ALPACA_API_SECRETS if x]
ALPACA_NAMES = [x for x in ALPACA_NAMES if x]
IP_WHITELIST = [x for x in IP_WHITELIST if x]


class AlpacaCreds(BaseModel):
    api_key: str
    api_secret: str
    name: str
    paper: bool


def get_accounts() -> dict[str, AlpacaCreds]:
    '''Returns a dictionary using the name as the key and the AlpacaCreds object as the value.'''
    accounts = {}
    for key, secret, name, paper in zip(ALPACA_API_KEYS, ALPACA_API_SECRETS, ALPACA_NAMES, ALPACA_PAPER):
        accounts[name] = AlpacaCreds(
            api_key=key, api_secret=secret, name=name, paper=paper)
    return accounts


def get_account(name: str) -> AlpacaCreds:
    '''Returns the AlpacaCreds object for the given name.'''
    return get_accounts()[name]
