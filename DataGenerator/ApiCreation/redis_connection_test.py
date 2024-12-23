import redis

REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "decode_responses": True,
}

# Initialize the Redis client
def create_redis_client():
    try:
        print("Connection creation started!!")
        # Connect to Redis server (non-cluster)
        redis_client = redis.Redis(**REDIS_CONFIG)
        print("Successfully connected to Redis.")
        return redis_client
    except Exception as e:
        print(f"Error connecting to Redis: {e}")
        return None

if __name__ == '__main__':
    create_redis_client()
