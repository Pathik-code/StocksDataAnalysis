from redis.cluster import RedisCluster

# Cluster connection details (assuming you have a Redis cluster running)
cluster = RedisCluster(
    startup_nodes=[{"host": "localhost", "port": "7000"}],  # Cluster nodes
    decode_responses=True
)

# Test the connection
try:
    cluster.ping()  # Ping to check if the connection is successful
    print("Connected to Redis Cluster!")
except redis.ConnectionError as e:
    print(f"Error connecting to Redis Cluster: {e}")
