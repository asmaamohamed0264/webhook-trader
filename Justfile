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
  #!/bin/bash
  cd ui
  npm run build
  rm -rf ../public
  cp -r dist ../public
  cd ..
  uv run -- fastapi dev

install:
  #!/bin/bash
  uv sync
  cd ui
  npm install
  cd ..

req example_name account_name:
  #!/bin/bash
  cd examples/webhook_payloads
  echo "Sending webhook payload to http://localhost:8000/webhook/{{account_name}}"
  curl -X POST -H "Content-Type: application/json" -d @{{example_name}}.json http://localhost:8000/webhook/{{account_name}}
  cd ../..

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

run-bg:
  docker run -d --name webhook-trader -p 8000:8000 -v {{DATA_DIRECTORY}}:/app/data \
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


# delete all pycache files in the current and subdirectories
# deletes public and ui/dist
clean:
  find . -name __pycache__ -exec rm -rf {} +
  rm -rf public
  rm -rf ui/dist
