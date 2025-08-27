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
uvicorn main:app --reload
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