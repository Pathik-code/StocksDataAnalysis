import redis
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
import asyncio
import json

app = FastAPI()

# Redis Cluster connection details
redis_cluster = redis.RedisCluster(
    host='localhost',  # Use the cluster nodes IPs if using a distributed Redis cluster
    port=7000,  # Adjust port if required
    decode_responses=True
)

# Simulating a list of users
users = [
    {"userid": 1, "name": "Alice", "age": 30, "city": "New York"},
    {"userid": 2, "name": "Bob", "age": 25, "city": "San Francisco"},
    {"userid": 3, "name": "Charlie", "age": 35, "city": "Chicago"},
]

@app.get("/")
async def read_root():
    description_dict = {
        "/": "Home Page",
        "/getusers": "Details of users will continuously show after each 1-second interval",
        "/cached_user/{userid}": "Retrieve cached user data from Redis by user ID",
        "/stocksdata": "Simulates stock data that changes every second",
        "/all": "Show all the details one by one"
    }
    return description_dict


# Real-time updates for users using SSE
@app.get("/getusers", response_class=EventSourceResponse)
async def get_users():
    async def event_generator():
        while True:
            for user in users:
                # Simulate user data update
                user["age"] += 1  # Increment the age as an example of changing data

                # Cache the updated user data in Redis
                redis_cluster.set(f"user:{user['userid']}", json.dumps(user))

                # Yield the updated user data
                yield {
                    "event": "update",  # Custom SSE event name (optional)
                    "data": json.dumps(user)
                }

                await asyncio.sleep(2)  # Simulate a 2-second interval for updates

    return EventSourceResponse(event_generator())


# Endpoint to retrieve user data from Redis cache
@app.get("/cached_user/{userid}")
async def get_cached_user(userid: int):
    user = redis_cluster.get(f"user:{userid}")
    if user:
        return {"cached_user": json.loads(user)}
    else:
        return {"error": "User not found in cache"}


# Simulated stock data updates (optional SSE example)
@app.get("/stocksdata", response_class=EventSourceResponse)
async def get_stocks_data():
    stock_data = [
        {"stocksymbol": "AAPL", "date": "2024-12-15", "openprice": 145.0, "highprice": 150.0, "lowprice": 144.0,
         "closeprice": 148.0, "volume": 1000000},
        {"stocksymbol": "GOOG", "date": "2024-12-15", "openprice": 2800.0, "highprice": 2850.0, "lowprice": 2780.0,
         "closeprice": 2820.0, "volume": 500000},
        {"stocksymbol": "AMZN", "date": "2024-12-15", "openprice": 3400.0, "highprice": 3450.0, "lowprice": 3380.0,
         "closeprice": 3425.0, "volume": 800000},
    ]

    async def event_generator():
        while True:
            for stock in stock_data:
                stock["volume"] += 1000  # Simulate volume change
                yield {"data": json.dumps(stock)}
                await asyncio.sleep(1)  # Simulate real-time updates every second

    return EventSourceResponse(event_generator())
