import redis
import json
from postgres_handler import fetch_data_from_postgres_with_rotation

REDIS_CLUSTER_CONFIG = {
    "host": "localhost",
    "port": 6379,  
    "decode_responses": True  
}

# redis data transfer limit
red_limit = 1000
# offset for pagination
red_offset = 0

# Initialize the Redis cluster client
redis_client = redis.Redis(**REDIS_CLUSTER_CONFIG, ssl=True)

def update_redis_with_postgres_data():
    try:
        global red_offset, red_limit, fetch_data_from_postgres_with_rotation
        print("Data Fetching Started!!")
        # Fetch data in chunks from PostgreSQL and update Redis
        rows = fetch_data_from_postgres_with_rotation(red_limit, red_offset)

        print("Data Has been Fetched!!")
        
        while rows:
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
            
            # Move the offset forward
            red_offset += red_limit
            print(f"Processed {red_offset} rows.")
            
            # Fetch the next chunk of data
            rows = fetch_data_from_postgres_with_rotation(red_limit, red_offset)

    except Exception as e:
        print("Error updating Redis:", e)

# Function to fetch data from Redis
def fetch_data_from_redis_with_rotation(last_index: int, limit: int = 10) -> (list, int): # type: ignore
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

if __name__ == "__main__":
    update_redis_with_postgres_data()