import random

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
async def read_root():
    # await asyncio.sleep(0.1)
    return {"message": "Hello"}


@app.get("/ping")
async def ping():
    if random.randint(1, 10) % 5 == 0:
        raise HTTPException(status_code=503, detail="Connection timed out")
    return {"Health": "Ok"}
