"""
This python file is to store the all the important details required by the components.
"""

# URL of the JSON schema
schema_url = "https://finnhub.io/static/swagger.json"

# File path to save the JSON data
schema_output_file = "finnhub_schema.json"

# finhub token keys
token_key = "ctcld11r01qjor98sj80ctcld11r01qjor98sj8g"

# websocket connection url
FINNHUB_WS_URL = "wss://ws.finnhub.io?token=<your_token>"

# Stock symbols to subscribe to (example: US stock symbols)
US_STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]