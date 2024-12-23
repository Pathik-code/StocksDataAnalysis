import redis
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import asyncio
from fastapi import FastAPI
from typing import List
from sse_starlette.sse import EventSourceResponse
import uvicorn

# from postgres_handler import fetch_data_from_postgres_with_rotation

app = FastAPI()

# Redis client initialization
REDIS_CLUSTER_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "decode_responses": True
}
redis_client = redis.Redis(**REDIS_CLUSTER_CONFIG, ssl=False)

# PostgreSQL connection details
POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "postgres"
}

# redis data transfer limit
red_limit = 1000
# offset for pagination
red_offset = 0


# Update Redis with data from PostgreSQL
def update_redis_with_postgres_data():
    try:
        global red_offset, red_limit
        # Connect to PostgreSQL
        with psycopg2.connect(**POSTGRES_CONFIG) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = "select count(*) from stockanalysis.stockdata;"
                cur.execute(query)
                total_rows = cur.fetchone()["count"]

                while red_offset < total_rows:
                    # Fetch a chunk of data from PostgreSQL
                    query = f"select stockid,stocksymbol,tradedate,openprice,highprice,lowprice,closeprice,volume,createdat,updatedat from stockanalysis.stockdata limit {red_limit} offset {red_offset};"
                    cur.execute(query)
                    rows = cur.fetchall()

                    if rows:
                        # Use a Redis pipeline to batch commands for this chunk
                        with redis_client.pipeline() as pipe:
                            for row in rows:
                                redis_key = f"stock:{row['stockid']}"
                                redis_value = json.dumps(row)

                                # Add set command to pipeline
                                pipe.set(redis_key, redis_value)
                                print(f"Queued Redis key: {redis_key} with value: {redis_value}")

                            # Execute the pipeline
                            pipe.execute()
                            print(f"Uploaded {len(rows)} records to Redis in this chunk.")

                    red_offset += red_limit
                    print(f"Processed {red_offset}/{total_rows} rows.")

    except Exception as e:
        print("Error updating Redis:", e)


# Fetch data from Redis and store it in a list
def fetch_data_from_redis_with_rotation(last_index: int, limit: int = 10) -> (List[dict], int):
    try:
        keys = sorted(redis_client.keys("stock:*"))  # Sort keys for predictable rotation

        total_keys = len(keys)
        if total_keys == 0:
            return [], last_index  # No records in Redis

        start_index = last_index % total_keys
        end_index = (start_index + limit) % total_keys

        if start_index < end_index:
            selected_keys = keys[start_index:end_index]
        else:
            selected_keys = keys[start_index:] + keys[:end_index]

        stock_list = []
        for key in selected_keys:
            stock_data = redis_client.get(key)
            if stock_data:
                stock_list.append(json.loads(stock_data))

        return stock_list, end_index

    except Exception as e:
        print("Error fetching data from Redis:", e)
        return [], last_index


# API endpoint to publish data using Server-Sent Events (SSE)
@app.get("/stream_stocks", response_class=EventSourceResponse)
async def stream_stocks():
    last_index = 0

    async def event_generator():
        nonlocal last_index
        while True:
            stock_list, last_index = fetch_data_from_redis_with_rotation(last_index, limit=1000)
            await asyncio.sleep(1)  # Simulate data publishing every second
            yield {"event": "update", "data": json.dumps(stock_list)}

    return EventSourceResponse(event_generator())


# Endpoint to retrieve stock data from Redis cache
@app.get("/cached_stock/{stockid}")
async def get_cached_stock(stockid: int):
    stock = redis_client.get(f"stock:{stockid}")
    if stock:
        return {"cached_stock": json.loads(stock)}
    else:
        return {"error": "Stock not found in cache"}


@app.get("/")
async def read_root():
    description_dict = {
        "/": "Home Page",
        "/stream_stocks": "Stream real-time stock data",
        "/cached_stock/{stockid}": "Retrieve cached stock data by stock ID"
    }
    return description_dict
