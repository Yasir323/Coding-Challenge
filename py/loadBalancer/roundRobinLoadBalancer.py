import collections
import threading
import time

import aiohttp
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import ujson

PROTOCOL = "http://"
PING_ENDPOINT = "/ping"
POLLING_INTERVAL = 30

app = FastAPI()
PROFILING = True  # Set this from a settings model

# Enable CORS (Cross-Origin Resource Sharing)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# Custom logging middleware
# @app.middleware("http")
# async def log_requests(request: Request, call_next):
#     response = await call_next(request)
#
#     date_header = response.headers.get("date", "-")
#
#     log_message = f'{request.client.host} - - [{date_header}] "{request.method} {request.url.path} {request.scope["query_string"].decode("utf-8")}" {response.status_code} {response.headers.get("content-length", "-")} "{request.headers.get("referer", "-")}" "{request.headers.get("user-agent", "-")}" "{request.headers.get("x-forwarded-for", "-")}"'
#     print(log_message)
#
#     return response


@app.get("/")
async def read_root(request: Request):
    data = {}
    async with aiohttp.ClientSession() as session:
        while active_servers:
            server = active_servers.popleft()
            try:
                response = await session.request(
                    method=request.method,
                    url=f"{PROTOCOL}{server['host']}:{server['port']}",
                    headers=request.headers
                )
                data = await response.json()
                active_servers.append(server)
            except aiohttp.ClientError:
                # Retry on a different server
                print(f"Could not connect to Server: {server}")
            except ConnectionError:
                continue
            else:
                break
        if not active_servers:
            raise HTTPException(status_code=502, detail="Error connecting to backend")
    return data


def read_config(file):
    with open(file) as fp:
        config = ujson.load(fp)
    return config


class ServerHealthCheck(threading.Thread):

    def __init__(self):
        super().__init__()
        self.all_servers = []

    def run(self):
        try:
            while True:
                active_server_ids = set()
                with threading.Lock():
                    for i in range(len(active_servers)):
                        server = active_servers.popleft()
                        try:
                            response = requests.get(url=f"{PROTOCOL}{server['host']}:{server['port']}{PING_ENDPOINT}", timeout=3)
                            if response.status_code == 200:
                                active_servers.append(server)
                                active_server_ids.add(server["id"])
                        except requests.exceptions.ConnectionError:
                            continue
                        else:
                            response.close()
                self.all_servers = read_config("config.json")["backendServers"]
                if len(self.all_servers) > len(active_servers):
                    for server in self.all_servers:
                        if server["id"] not in active_server_ids:
                            try:
                                response = requests.get(url=f"{PROTOCOL}{server['host']}:{server['port']}{PING_ENDPOINT}")
                                if response.status_code == 200:
                                    with threading.Lock():
                                        active_servers.append(server)
                                    active_server_ids.add(server["id"])
                            except requests.exceptions.ConnectionError:
                                continue
                            else:
                                response.close()
                print("Active Servers: ", active_server_ids)
                time.sleep(POLLING_INTERVAL)
        except Exception as err:
            print(f"{type(err).__name__}: {str(err)}")


if __name__ == "__main__":
    import uvicorn

    conf = read_config("config.json")
    load_balancer_conf = conf["loadBalancer"]

    active_servers = collections.deque()

    server_health_check = ServerHealthCheck()
    server_health_check.start()
    try:
        uvicorn.run(
            app,
            host=load_balancer_conf["host"],
            port=load_balancer_conf["port"],
            log_level="critical"
        )
    finally:
        server_health_check.join()
