import asyncio
from typing import List

import ujson

import aiofiles


async def main():

    def graceful_shutdown():
        print("Don't press Ctrl-C again. Closing application... ")
        stop_servers(servers)

    conf = await read_config("config.json")
    servers_config = conf["backendServers"]
    servers = await run_servers(servers_config)
    try:
        await asyncio.sleep(500)
    finally:
        graceful_shutdown()


async def read_config(file):
    async with aiofiles.open(file) as fp:
        config = ujson.loads(await fp.read())
    return config


async def run_servers(servers):
    tasks = [asyncio.create_subprocess_exec("uvicorn", "backendServer:app", f"--host={server['host']}",
                                            f"--port={server['port']}", "--workers=4", "--log-level=critical")
             for server in servers]
    completed_tasks, pending_tasks = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
    return [task.result() for task in completed_tasks]


def stop_servers(servers: List[asyncio.subprocess.Process]):
    for server in servers:
        try:
            server.kill()
            server.terminate()
        except Exception as err:
            print(type(err).__name__, ": ", str(err))


if __name__ == "__main__":
    asyncio.run(main())
