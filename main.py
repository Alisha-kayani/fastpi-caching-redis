# Import necessary modules from various libraries
from pydantic import BaseModel
import json
from functools import wraps
from aiocache import Cache
from fastapi import FastAPI, HTTPException

# --- 1. Data Model (Pydantic) ---
# This class defines the structure and data types for a 'User'.
# It ensures that any data we handle for a user matches this format.
class User(BaseModel):
    id: int
    name: str
    email: str
    age: int

# --- 2. Caching Decorator ---
# A custom function that wraps another function to add caching functionality.
def cache_response(ttl: int = 60, namespace: str = "main"):
    """
    This is the caching decorator for FastAPI endpoints.

    Args:
        ttl (int): Time to live for the cache in seconds (how long the data stays in Redis).
        namespace (str): A unique name for the group of cache keys.
    """
    def decorator(func):
        # '@wraps' is a helper that preserves the original function's metadata (like its name).
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate a unique key for the cache based on the user ID.
            user_id = kwargs.get('user_id') or args[0]
            cache_key = f"{namespace}:user:{user_id}"

            # Establish a connection to the Redis cache.
            # aiocache will handle the connection pool and other details.
            cache = Cache.REDIS(endpoint="localhost", port=6379, namespace=namespace)

            # --- Try to retrieve data from cache (Cache Hit) ---
            cached_value = await cache.get(cache_key)
            if cached_value:
                # If data is found in the cache, return it immediately after converting it from JSON.
                print(f"Cache HIT for key: {cache_key}")
                return json.loads(cached_value)

            # --- Fetch data if cache is not hit (Cache Miss) ---
            print(f"Cache MISS for key: {cache_key}. Fetching from original source...")
            # This calls the original function (e.g., get_user_details) to get the data.
            response = await func(*args, **kwargs)

            try:
                # After getting the data, store it in Redis for future requests.
                # The data is converted to JSON to be stored as a string.
                await cache.set(cache_key, json.dumps(response), ttl=ttl)
                print(f"Data for key {cache_key} stored in cache with TTL {ttl}s.")
            except Exception as e:
                # If caching fails for any reason, raise an HTTP 500 error.
                raise HTTPException(status_code=500, detail=f"Error caching data: {e}")

            return response
        return wrapper
    return decorator

# --- 3. FastAPI Application Instance ---
# This is the main object for our FastAPI application.
app = FastAPI()

# --- 4. Simulated Database ---
# A simple Python dictionary acting as our "database" of users.
# In a real application, this would be a database query.
users_db = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 25},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 30},
    3: {"id": 3, "name": "Charlie", "email": "charlie@example.com", "age": 22},
}

# --- 5. API Endpoint ---
# This defines an endpoint that a user can access.
@app.get("/users/{user_id}")
@cache_response(ttl=120, namespace="users")
async def get_user_details(user_id: int):
    # This simulates a slow database lookup.
    print("Simulating a slow database lookup...")
    await asyncio.sleep(1) # Added to make the "slow" lookup more noticeable
    user = users_db.get(user_id)
    if not user:
        # If the user is not found, return an HTTP 404 error.
        raise HTTPException(status_code=404, detail="User not found")

    return user

# --- 6. Run the Application ---
# This block makes the file runnable directly.
# When you run `uvicorn main:app --reload`, it executes this block.
if __name__ == "__main__":
    import uvicorn
    import asyncio # Added to enable async sleep
    uvicorn.run(app, host="0.0.0.0", port=8000)