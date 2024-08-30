from functools import wraps
from hashlib import sha256
from json import loads
from time import time
from typing import Any, Callable
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from random import choice
from fastapi.responses import HTMLResponse, PlainTextResponse
from os import path
from requests import get
from re import findall
from asyncio import get_event_loop, sleep
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel


app = FastAPI(docs_url="/api/docs", openapi_url="/api/openapi.json")
SCRAPE_INTERVAL = 86400  # 1 Day


app.mount("/static", StaticFiles(directory="static"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HealthCheck(BaseModel):
    """Response model to validate and return when performing a health check."""

    status: str = "OK"


@app.get(
    "/health",
    tags=["healthcheck"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    response_model=HealthCheck,
)
def get_health() -> HealthCheck:
    """
    ## Perform a Health Check
    Endpoint to perform a healthcheck on. This endpoint can primarily be used Docker
    to ensure a robust container orchestration and management is in place. Other
    services which rely on proper functioning of the API service will not deploy if this
    endpoint returns any other HTTP status code except 200 (OK).
    Returns:
        HealthCheck: Returns a JSON response with the health status
    """
    return HealthCheck(status="OK")


def extract_keys(raw_keys):
    pattern = r"🔐 Key: ([a-zA-Z0-9-]+) \(\d+ GB\)"
    keys = findall(pattern, raw_keys)
    return keys


def rate_limit(max_calls: int, period: int):
    def decorator(func: Callable[[Request], Any]) -> Callable[[Request], Any]:
        usage: dict[str, list[float]] = {}

        @wraps(func)
        async def wrapper(request: Request) -> Any:
            # get the client's IP address
            if not request.client:
                raise ValueError("Request has no client information")
            ip_address: str = request.client.host

            # create a unique identifier for the client
            unique_id: str = sha256((ip_address).encode()).hexdigest()

            # update the timestamps
            now = time()
            if unique_id not in usage:
                usage[unique_id] = []
            timestamps = usage[unique_id]
            timestamps[:] = [t for t in timestamps if now - t < period]

            if len(timestamps) < max_calls:
                timestamps.append(now)
                return await func(request)

            # calculate the time to wait before the next request
            wait = period - (now - timestamps[0])
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Retry after {wait:.2f} seconds",
            )

        return wrapper

    return decorator


async def scrape_keys():

    last_post_id_response = get(
        "https://telegram-channel-scraper-api.vercel.app/api/v2/getlastpost_id/warpplus"
    )
    last_post_id_content = last_post_id_response.content.decode("utf-8")
    last_post_id_json = loads(last_post_id_content)
    last_post_id = last_post_id_json["last_post_id"]
    key_posts = last_post_id - 2  # to scrape the keys off of the last 2 posts

    raw_keys = get(
        f"https://telegram-channel-scraper-api.vercel.app/api/v2/get_post/warpplus?after={key_posts}"
    )
    raw_keys = (raw_keys.content).decode("utf-8")
    keys = extract_keys(raw_keys)
    keys = set(keys)
    with open("keys.txt", "w") as file:
        for key in keys:
            file.write(f"{key}\n")
    print("Keys have been scraped")


@app.get("/", response_class=FileResponse)
@rate_limit(max_calls=20, period=60)
async def read_root(request: Request):
    return FileResponse(path="static/index.html")


@app.get("/api/", response_class=PlainTextResponse)
@rate_limit(max_calls=20, period=60)
async def main(request: Request):
    if not path.isfile("keys.txt"):
        return HTMLResponse("Server is starting or out of keys", status_code=500)
    with open("keys.txt", "r") as file:
        keys = file.read().split("\n")
        keys = [key for key in keys if key]  # This removes any empty strings
        return choice(keys) if keys else "No keys available"


async def periodic():
    while True:
        # code to run periodically starts here
        await scrape_keys()
        # code to run periodically ends here
        # sleep for 3 seconds after running above code
        await sleep(SCRAPE_INTERVAL)


@app.on_event("startup")
async def schedule_periodic():
    loop = get_event_loop()
    loop.create_task(periodic())


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
