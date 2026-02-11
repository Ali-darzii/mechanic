from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi import _rate_limit_exceeded_handler

from src.config import setting
from src.utils.throttle import limiter
from src.api.v1.router import v1_routers


app = FastAPI(
    root_path=setting.ROUTES_PREFIX, 
    swagger_ui_parameters={"filter": True},
)

# throttle middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"detail": "Too many requests"}
    )

# v1 APIs
v1_prefix = "/v1"
for router in v1_routers:
    app.include_router(router=router, prefix=v1_prefix)