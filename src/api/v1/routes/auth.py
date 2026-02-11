from fastapi import APIRouter, Body, Depends, Header, status, Request

from src.models.user import User as UserModel
from src.schemas.auth import Login, ResetPaasword, SignupSendOTP, SignupVerifyOTP, TokenOut, TokenVerifyOut, VerifyResetPassword
from src.services.auth import AuthService
from src.app import limiter
from src.utils.auth import get_current_user

router = APIRouter(
    prefix="/auth",
    tags=["v1 - auth"]
)


@router.post("/send-otp", status_code=status.HTTP_200_OK)
async def signup_send_otp(
    request: Request,
    signup: SignupSendOTP,
    service: AuthService = Depends(AuthService)
):
    await service.signup_send_otp(signup)

@router.put("/send-otp", response_model=TokenOut, status_code=status.HTTP_200_OK)
async def signup_verify_otp(
    request: Request,
    signup: SignupVerifyOTP,
    service: AuthService = Depends(AuthService)
) -> TokenOut:
    return await service.signup_verify_otp(signup)


@router.post("/token", response_model=TokenOut, status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def login(
    request: Request,
    login: Login,
    service: AuthService = Depends()
) -> TokenOut:
    return await service.login(login)


@router.post("/token/refresh", response_model=TokenOut, status_code=status.HTTP_200_OK)
@limiter.limit("1/minute")
async def refresh_token(
    request: Request,
    refresh_token: str = Body(..., embed=True),
    service: AuthService = Depends()
) -> TokenOut:
    return await service.refresh_token(refresh_token)

@router.get("/token/verify", response_model=TokenVerifyOut, status_code=status.HTTP_200_OK)
async def is_access_token_valid(
    access_token: str = Header(..., alias="Authorization"),
    service: AuthService = Depends()
) -> TokenVerifyOut:
    return await service.verify_token(access_token)


@router.post("/token/revoke", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    refresh_token: str = Body(..., embed=True),
    service: AuthService = Depends(),
    user: UserModel = Depends(get_current_user),
):
    await service.revoke_token(refresh_token, user)


@router.post("/reset-password", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def send_email_otp_reset_password(
    request: Request,
    reset_password: ResetPaasword,
    service: AuthService = Depends()
):
    await service.send_reset_password_token(reset_password)

@router.put("/reset-password", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def verify_reset_password(
    request: Request,
    reset_password: VerifyResetPassword,
    service: AuthService = Depends()
):
    await service.verify_reset_password_token(reset_password)