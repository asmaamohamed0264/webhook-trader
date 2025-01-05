from lib.env_vars import IP_WHITELIST

# most of these IPs are from TradingView
# https://www.tradingview.com/support/solutions/43000529348-about-webhooks/
ips = [
    '52.89.214.238',
    '34.212.75.30',
    '54.218.53.128',
    '52.32.178.7',
    '127.0.0.1'
]

WHITELIST = ips + IP_WHITELIST

ORIGINS = ['*']
