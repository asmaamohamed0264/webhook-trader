# Webhook Trader

A very, very opinionated trading interface for TradingView Webhook Notifications and the Alpaca API.

## Deployment Pre-requisites

- [Alpaca API Key](https://alpaca.markets/)
- [Python 3.12+](https://www.python.org/downloads/)
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (The **best** Python package manager!)
- [Docker](https://docs.docker.com/)
- [Fly.io](https://fly.io/) account
- [flyctl CLI](https://fly.io/docs/)
- [Just](https://just.systems/man/en/packages.html) (Like a Makefile but better!)

## Configuration 

### Environment Variables

| Environment Variable | Description | Example |
|---------------------|-------------|---------|
| `ALPACA_API_KEYS` | Comma-separated list of Alpaca API keys. | `PK1234567890,PK0987654321` |
| `ALPACA_API_SECRETS` | Comma-separated list of Alpaca API secrets. | `SK1234567890,SK0987654321` |
| `ALPACA_NAMES` | Comma-separated list of unique identifiers for each account. | `trading-bot-1,trading-bot-2` |
| `ALPACA_PAPER` | Comma-separated list of boolean values (1=true, 0=false) indicating if account is paper trading. | `1,0` |
| `IP_WHITELIST` | Comma-separated list of allowed IP addresses (IPv4 and IPv6). | `8.8.8.8,2001:4860:4860::8888` |
| `DB_URI` | SQLAlchemy database connection string. Currently we support Postgres and SQLite | `sqlite:///trader.db` |
| `DB_ECHO` | Enable SQL query logging. | `True` |
| `TEST_MODE` | Enable test mode for development. Disables sending the orders to Alpaca and just logs them in the database. | `True` |

### Alpaca Accounts

The environment variables for the various accounts should be a comma separated list, and order does matter. The first item in the list of API Keys should correspond to the first item in the list of API Secrets, their names, and if they are a paper account or not.

For example if you have these two accounts:

| Account Name | API Key | API Secret | Paper? |
|--------------|---------|------------|---------|
| Trading-Bot-1 | PK1A2B3C4D5E6F7G8H9I | SK9I8H7G6F5E4D3C2B1A | true |
| Trading-Bot-2 | PK9H8G7F6E5D4C3B2A1 | SK1B2C3D4E5F6G7H8I9J | false |

Then your environment variables would look like:

```bash
ALPACA_API_KEYS="PK1A2B3C4D5E6F7G8H9I,PK9H8G7F6E5D4C3B2A1"
ALPACA_API_SECRETS="SK9I8H7G6F5E4D3C2B1A,SK1B2C3D4E5F6G7H8I9J"
ALPACA_NAMES="Trading-Bot-1,Trading-Bot-2"
ALPACA_PAPER="1,0" # 1 for true, 0 for false
```

You should make the names something long, unique per account, and not easily guessable. TradingView doesn't support API keys or any other sort of authentication for the webhooks, so those names and the IP Whitelist are the only things that protect your accounts. For this reason I recommend creating UUIDs for the names. I used this script to generate the names:

```bash
python -c "import uuid; print(uuid.uuid4())"
```

### IP Whitelist

For the IP Whitelist, you should put both your IPv4 and your IPv6 addresses in the environment variable. For now it only accepts complete IP addresses, no CIDR notation. Loopback addresses (`127.0.0.1` and `localhost`) as well as the addresses listed on the TradingView webhook documentation are already included in the whitelist.

If you want a quick way to get your IPs at the command line, you can use these commands:

```bash
curl -s ipinfo.io # for IPv4
curl -s v6.ipinfo.io # for IPv6
```

Here is an example of what the IP Whitelist environment variable should look like:

```bash
IP_WHITELIST=8.8.8.8,2001:4860:4860::8888 # Replace with your IP addresses
```

### Database

The database connection string should be a SQLAlchemy connection string. For SQLite, it should look like this:

```bash
DB_URI="sqlite:///trader.db" # Path to the SQLite database file
```

For Postgres, it should look like this:

```bash
DB_URI="postgresql://user:password@localhost:5432/dbname" # Replace with your Postgres connection string
```

When developing, hosting locally, or deploying in an environment where you have persistent storage, SQLite should be fine for most use cases. If you are deploying to a cloud provider or a managed service, like [Fly.io](https://fly.io/), you should use Postgres. I use [Supabase](https://supabase.com/) for my Postgres databases, but you can use any provider you like.

You can also optionally enable SQL query logging by setting the `DB_ECHO` environment variable to `True`. This is recommended for development and debugging, but should be disabled in production.

### Test Mode

Test mode is a way to test the application without actually sending orders to Alpaca. It will log the orders to the database, but not send them to Alpaca. This is useful for development and testing. To enable test mode, set the `TEST_MODE` environment variable to `True`.

## Building, Running, and Deploying

### Building

```bash
just build
```

This will build the Docker image and tag it with `latest`.

### Running Locally

```bash
just run
```

This will run the Docker container locally. You can access the application at `http://localhost:8000`. If you want to run the container in the background, you can use the following command:

```bash
just run-bg
```

### Deploy to Fly.io

Once you have the CLI set up, create a new file called `.env.fly`. Then add your environment variables to that file. Then you can simply import the environment variables and deploy the application:

```bash
fly launch
fly ext supabase create
# add the Postgres connection string to the .env.fly file, then run
fly secrets import < .env.fly
# finally redeploy
fly deploy
```

I should write a more in-depth guide on how to deploy to Fly.io, but for now you can follow the [official documentation](https://fly.io/docs/).

## Usage

Coming Soon :tm:!

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
