import psycopg2
from psycopg2.extras import RealDictCursor
from config import StocksQuery
import redis
import json


REDIS_CLUSTER_CONFIG = {
    "host": "localhost",
    "port": 6379,  
    "decode_responses": True  
}
# Initialize the Redis cluster client
redis_client = redis.Redis(**REDIS_CLUSTER_CONFIG, ssl=True)

POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "postgres",
    "user": "postgres",
    "password": "postgres"
}

def fetch_data_from_postgres_with_rotation(limit=1000, offset=0):
    try:
        print(f"Data fetching.. started from {offset} to {offset + limit}")
        # Connect to PostgreSQL
        with psycopg2.connect(**POSTGRES_CONFIG) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Construct the query with pagination
                query = StocksQuery + f" LIMIT {limit} OFFSET {offset};"
                cur.execute(query)
                result = cur.fetchall()
                return result
    except Exception as e:
        print("Error fetching data from PostgreSQL:", e)
        return []
    

def update_redis_with_postgres_data(red_limit, red_offset):
    try:
        print("Data Fetching Started!!")
        # Fetch data in chunks from PostgreSQL and update Redis
        rows = fetch_data_from_postgres_with_rotation(red_limit, red_offset)

        print("Data Has been Fetched!!")
        
        while rows:
            # Use a Redis pipeline to batch commands for this chunk
            with redis_client.pipeline() as pipe:
                for row in rows:
                    print(row)
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

# Main logic to call the function
if __name__ == "__main__":
    limit = 1000  # Example limit, adjust as needed
    offset = 0    # Example offset, adjust as needed
    result = fetch_data_from_postgres_with_rotation(limit, offset)
    print(f"Fetched {result} records")

