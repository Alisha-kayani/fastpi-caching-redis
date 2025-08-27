### What You'll Learn

This guide will teach you how to build a simple web API with FastAPI and make it super-fast using **caching** with **Redis**.

  * **FastAPI**: A modern and fast web framework for Python.
  * **Caching**: A way to store data temporarily so you don't have to fetch it every time.
  * **Redis**: A special database that's incredibly fast, perfect for caching.
  * **uv**: A new, very fast tool for managing your project's dependencies.

### Step 1: Set Up Your Project

1.  Create a new, empty folder for your project.
    ```bash
    mkdir my-fastapi-project
    cd my-fastapi-project
    uv init .
    ```
2.  Create a file named `main.py` inside this folder and paste the entire Python code into it.

### Step 2: Install All the Tools

You'll use the **uv** tool to set up your project's environment and install everything you need.

1.  Open your terminal in the `my-fastapi-project` folder.
2.  Run the following command to create a virtual environment and install all the necessary libraries at once.
    ```bash
    uv add fastapi uvicorn aiocache pydantic
    ```
    This command creates a virtual environment for you automatically and installs all the tools you need in one go.

### Step 3: Start the Redis Server

Your code needs a Redis server to work. The easiest way to get one is with Docker.

1.  Make sure Docker is running on your computer.
2.  Open a **new terminal window** and run this command:
    ```bash
    docker run --name my-redis-db -d -p 6379:6379 redis
    ```
    This command starts a Redis server and makes it accessible to your Python code.

### Step 4: Run Your Web API

Now, go back to your **first terminal window** and start the application.

```bash
uv run main.py
```

You should see a message saying the server is running. It's now ready to accept requests\!

### Step 5: See How Caching Works

Let's test the caching.

1.  Open your web browser and go to `http://127.0.0.1:8000/users/1`.
2.  The first time you visit this page, the app gets the data and saves a copy in Redis.
3.  Reload the page. You will notice the response is almost instant\! This is because the app is now getting the data from the super-fast Redis cache instead of doing the work again.

### Step 6: Verify the Cache

You can even check Redis yourself to see the cached data.

1.  In the terminal where you ran the Docker command, type:
    ```bash
    docker exec -it my-redis-db redis-cli
    ```
2.  Then, inside the Redis command line, type:
    ```
    KEYS *
    ```
    You will see a new key, like `users:user:1`, which confirms that your data is in the cache.

https://dev.to/sivakumarmanoharan/caching-in-fastapi-unlocking-high-performance-development-20ej




------------------
Code into smaller, more understandable chunks and explain what each part does.

-----

### 1\. The Data Model (`User` class)

This section defines the structure of the data you're working with.

```python
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    age: int
```

  * **`from pydantic import BaseModel`**: Imports the `BaseModel` class from the Pydantic library. Pydantic is a tool that helps you define data formats and validates that the data you receive matches the format you expect.
  * **`class User(BaseModel):`**: This creates a class named `User` that inherits from `BaseModel`. This means the `User` class will have all the smart features of a Pydantic model.
  * **`id: int`, `name: str`**, etc.: These lines define the **fields** of your data. You're telling the program that every `User` object must have an `id` that is a number (`int`), a `name` that is text (`str`), and so on.

-----

### 2\. The Caching Logic (`cache_response` decorator)

This is the most complex part of the code. It's a special function called a **decorator** that wraps another function to add new behavior—in this case, caching.

```python
def cache_response(ttl: int = 60, namespace: str = "main"):
    # The outer function that takes caching settings (ttl, namespace)
    def decorator(func):
        # The decorator itself, which wraps your API function
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This is the actual function that runs when your API is called
            # ... all the caching code goes here ...
            cache = Cache.REDIS(endpoint="localhost", port=6379, namespace=namespace)
            cached_value = await cache.get(cache_key)
            # ... more caching logic ...
            response = await func(*args, **kwargs)
            # ... more caching logic ...
            return response
        return wrapper
    return decorator
```

  * **`def cache_response(...)`**: This is a function that takes arguments like `ttl` (time-to-live) and `namespace`. These arguments let you customize how the caching works for each API endpoint.
  * **`def decorator(func)`**: This function takes the actual API endpoint function as its input (`func`).
  * **`async def wrapper(*args, **kwargs)`**: This is the most important part. It's the wrapper function that runs **every time** the decorated endpoint is called.
  * **`cache = Cache.REDIS(...)`**: This line creates a connection to your Redis server.
  * **`cached_value = await cache.get(cache_key)`**: This line checks if the data is already in the cache using a unique `cache_key`.
  * **`if cached_value: return json.loads(cached_value)`**: If the data is found in the cache, it's immediately returned without running the original function. This is the **cache hit**.
  * **`response = await func(*args, **kwargs)`**: If the data is not in the cache, this line calls the original function (`func`)—which is your `get_user_details` function—to get the data. This is the **cache miss**.
  * **`await cache.set(cache_key, ...)`**: After getting the data, this line stores it in the cache for future use.

-----

### 3\. The FastAPI Application

This is the core of your web API. It defines the server and the endpoints that users can access.

```python
from fastapi import FastAPI
# ... other code ...
app = FastAPI()
```

  * **`from fastapi import FastAPI`**: This imports the main class from the FastAPI library.
  * **`app = FastAPI()`**: This creates an instance of the FastAPI application. This `app` object is what Uvicorn will use to run your API.

-----

### 4\. The API Endpoint

This section defines the specific URL that your application responds to.

```python
@app.get("/users/{user_id}")
@cache_response(ttl=120, namespace="users")
async def get_user_details(user_id: int):
    user = users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

  * **`@app.get("/users/{user_id}")`**: This is a decorator that tells FastAPI this function should run when a user makes a `GET` request to the `/users/{user_id}` URL. The `{user_id}` part is a **path parameter** that captures a value from the URL, like `1` or `2`.
  * **`@cache_response(...)`**: This applies your custom caching decorator to this specific endpoint.
  * **`async def get_user_details(...)`**: This is the function that actually runs when a request comes in. It takes the `user_id` from the URL.
  * **`user = users_db.get(user_id)`**: This line simulates a database lookup. It tries to get a user from the `users_db` dictionary using the `user_id` from the URL.
  * **`if not user: raise HTTPException(...)`**: This checks if the user was found. If not, it raises an error that FastAPI will turn into a "404 Not Found" response.
  * **`return user`**: If the user is found, the function returns the user data, which FastAPI automatically converts to a JSON response.

-----

### 5\. Running the Application

This final block makes your file runnable as a script.

```python
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

  * **`if __name__ == "__main__":`**: This is a standard Python expression. The code inside this block only runs when the file is executed directly (e.g., with `uvicorn main:app`). It doesn't run if the file is imported as a module into another script.
  * **`uvicorn.run(...)`**: This command starts the Uvicorn web server.
      * `app`: Tells Uvicorn to run the `app` instance you created.
      * `host="0.0.0.0"`: Makes the server accessible from any machine on your network.
      * `port=8000`: Sets the server to listen for requests on port 8000.