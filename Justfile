set dotenv-load
set export

ALPACA_API_KEYS := env("ALPACA_API_KEYS")
ALPACA_API_SECRETS := env("ALPACA_API_SECRETS")
ALPACA_NAMES := env("ALPACA_NAMES")
ALPACA_PAPER := env("ALPACA_PAPER")
IP_WHITELIST := env("IP_WHITELIST")
DB_URI := "sqlite:///data/trader.db"
DATA_DIRECTORY := `pwd` + "/data"

# Print out some help
default:
	@just --list --unsorted

dev:
  uv run -- fastapi dev

# build the docker container
build:
  uv pip freeze > requirements.txt
  docker build -t chand1012/webhook-trader:latest .

# run the docker container
run:
  @docker run --rm --name webhook-trader -p 8000:8000 -v {{DATA_DIRECTORY}}:/app/data \
    -e ALPACA_API_KEYS={{ALPACA_API_KEYS}} \
    -e ALPACA_API_SECRETS={{ALPACA_API_SECRETS}} \
    -e ALPACA_NAMES={{ALPACA_NAMES}} \
    -e ALPACA_PAPER={{ALPACA_PAPER}} \
    -e IP_WHITELIST={{IP_WHITELIST}} \
    -e DB_URI={{DB_URI}} \
    -e DB_ECHO=True \
    chand1012/webhook-trader:latest

deploy:
  flyctl deploy
