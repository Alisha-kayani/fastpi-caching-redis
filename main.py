from pydantic import BaseModel
import json
from functools import wraps
from aiocache import Cache
from fastapi import HTTPException
class User(BaseModel):
    id: int
    name: str
    email: str
    age: int



def cache_response(ttl: int = 60, namespace: str = "main"):
    """
    Caching decorator for FastAPI endpoints.

    ttl: Time to live for the cache in seconds.
    namespace: Namespace for cache keys in Redis.
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id') or args[0]  # Assuming the user ID is the first argument
            cache_key = f"{namespace}:user:{user_id}"

            cache = Cache.REDIS(endpoint="localhost", port=6379, namespace=namespace)

            # Try to retrieve data from cache
            cached_value = await cache.get(cache_key)
            if cached_value:
                return json.loads(cached_value)  # Return cached data

            # Call the actual function if cache is not hit
            response = await func(*args, **kwargs)

            try:
                # Store the response in Redis with a TTL
                await cache.set(cache_key, json.dumps(response), ttl=ttl)
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error caching data: {e}")

            return response
        return wrapper
    return decorator
from fastapi import FastAPI

app = FastAPI()

# Sample data representing users in a database
users_db = {
    1: {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 25},
    2: {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 30},
    3: {"id": 3, "name": "Charlie", "email": "charlie@example.com", "age": 22},
}

@app.get("/users/{user_id}")
@cache_response(ttl=120, namespace="users")
async def get_user_details(user_id: int):
    # Simulate a database call by retrieving data from users_db
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)