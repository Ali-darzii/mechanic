from src.api.v1.routes.auth import router as auth_router
from src.api.v1.routes.permission import router as permission_router


v1_routers = (
    auth_router,
    permission_router,
)