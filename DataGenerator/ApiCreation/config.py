REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "decode_responses": True
}

POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "postgres"
}

StocksQuery = """
    select stockid,stocksymbol,tradedate,openprice,highprice,lowprice,closeprice,volume,createdat,updatedat from stockanalysis.stockdata
"""
