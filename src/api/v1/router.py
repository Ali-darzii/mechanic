from src.api.v1.routes.auth import router as auth_router
from src.api.v1.routes.permission import router as permission_router
from src.api.v1.routes.mechanic import router as mechanic_router
from src.api.v1.routes.car import router as car_router
from src.api.v1.routes.mechanic_car_request import rotuer as mechanic_car_request_router
from src.api.v1.routes.mechanic_comment import router as mechanic_comment_router

v1_routers = (
    auth_router,
    permission_router,
    mechanic_router,
    car_router,
    mechanic_car_request_router,
    mechanic_comment_router,
)