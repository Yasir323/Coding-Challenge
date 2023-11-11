import asyncio
import random


def randomly_stop_a_server(servers):
    if servers:
        server_to_stop = random.choice(servers)
        try:
            server_to_stop.terminate()
            print(f"Stopped server on port {server_to_stop.args[-1]}")
        except Exception as err:
            print(type(err).__name__, ": ", str(err))


def stop_servers(servers):
    count = 0
    for server in servers:
        try:
            server.terminate()
            count += 1
        except Exception as err:
            print(type(err).__name__, ": ", str(err))





async def main():

    def graceful_shutdown():
        print("Don't press Ctrl-C again. Closing application... ")
        stop_servers(servers)
        if process:
            process.terminate()

    ports = [8000, 8001, 8002, 8003, 8004, 8005]
    servers = await run_servers(ports)
    process = None
    try:
        process = await asyncio.create_subprocess_exec("uvicorn", "load_balancer:app", "--port", str(80))
        await asyncio.sleep(100)
    finally:
        graceful_shutdown()


if __name__ == "__main__":
    asyncio.run(main())
