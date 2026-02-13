from random import randint

from fastapi import Depends, HTTPException, status

from src.repositories.base import RedisRepository
from src.schemas.auth import (
    CreateRevokeToken,
    Login,
    SignupSendOTP,
    SignupVerifyOTP,
    TokenOut,
    TokenType,
    TokenVerifyOut,
    ResetPaasword,
    VerifyResetPassword
)
from src.repositories.user import UserRepository
from src.repositories.auth import RevokedTokenRepository
from src.models.user import User as UserModel
from src.utils.auth import UserPassword
from src.utils.auth import jwt
from src.config import setting
from src.tasks.send_sms import send_sms


class AuthService:
    def __init__(
        self,
        repository: UserRepository = Depends(UserRepository),
        token_repository: RevokedTokenRepository = Depends(RevokedTokenRepository),
        redis_repository: RedisRepository = Depends(RedisRepository),
    ):
        self._repository = repository
        self._token_repository = token_repository
        self._redis_repository = redis_repository

    def OTP_token(slef) -> int:
        return randint(100000, 999999)

    async def signup_send_otp(self, signup: SignupSendOTP) -> None:
        user = await self._repository.get_by_phone_number(signup.phone_number)
        if user is not None:

            if user.is_active == True:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with phone_number: {signup.phone_number} exists.",
                )

            if user.is_delete == True:
                await self._repository.out_of_soft_delete(user)

        else:
            signup.password = UserPassword.generate_password_hash(signup.password)
            user = await self._repository.create(signup)
            
        key = f"signup_{user.phone_number}"

        if await self._redis_repository.get(key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too mant request.",
            )

        # handling test user
        if setting.DEBUG and user.phone_number == "09445566778":
            token = 555555
            await self._redis_repository.set(key, token, setting.OTP_EXPIRE)

        else:
            token = self.OTP_token()
            await self._redis_repository.set(key, token, setting.OTP_EXPIRE)
            
            if setting.DEBUG:
                print(token)
            send_sms.delay(user.phone_number, f"`Mechanic` one time password: {token}")

    async def signup_verify_otp(self, signup: SignupVerifyOTP) -> TokenOut:
        invalid_token = HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token is expired or invalid.",
        )

        user = await self._repository.get_by_phone_number(signup.phone_number)
        if not user or user.is_active:
            raise invalid_token

        key = f"signup_{user.phone_number}"
        cache_token = await self._redis_repository.get(key)
        if cache_token is None or int(cache_token) != signup.token:
            raise invalid_token

        user = await self._repository.user_status(user, True)

        encode = {
            "sub": user.phone_number,
            "role": user.role,
            "is_active": user.is_active,
        }
        access_token = jwt.create_token(encode, TokenType.access_token)
        refresh_token = jwt.create_token(encode, TokenType.refresh_token)

        return TokenOut(
            access_token=access_token, refresh_token=refresh_token, user_id=user.id
        )

    async def login(self, login: Login) -> TokenOut:
        user = await self._repository.get_by_phone_number(login.phone_number)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Phone number or password is wrong",
            )

        if user.is_active == False:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=f"User is not active"
            )

        if not UserPassword.verify_password(login.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Phone number or password is wrong",
            )

        encode = {
            "sub": user.phone_number,
            "role": user.role,
            "is_active": user.is_active,
        }
        access_token = jwt.create_token(encode, TokenType.access_token)
        refresh_token = jwt.create_token(encode, TokenType.refresh_token)

        return TokenOut(
            access_token=access_token, refresh_token=refresh_token, user_id=user.id
        )

    async def refresh_token(self, refresh_token: str) -> TokenOut:
        payload = jwt.verify_token(refresh_token, TokenType.refresh_token)

        jti = payload.get("jti")
        if not jti or await self._token_repository.is_revoked_token(jti):
            raise jwt.INVALID_TOKEN

        phone_number = payload.get("sub")
        if not phone_number:
            raise jwt.INVALID_TOKEN

        user = await self._repository.get_by_phone_number(phone_number)
        if user is None:
            raise jwt.INVALID_TOKEN

        await self._token_repository.create(
            CreateRevokeToken(jti=jti, user_id=user.id)
        )

        encode = {
            "sub": user.phone_number,
            "role": user.role,
            "is_active": user.is_active,
        }

        access_token = jwt.create_token(encode, TokenType.access_token)
        refresh_token = jwt.create_token(encode, TokenType.refresh_token)
        return TokenOut(
            access_token=access_token, refresh_token=refresh_token, user_id=user.id
        )
    
    async def verify_token(self, access_token: str) -> TokenVerifyOut:
        jwt.verify_token(access_token, TokenType.access_token)

        access_token = jwt.normalize_token(access_token)

        return TokenVerifyOut(
            access_token=access_token, token_type=TokenType.access_token
        )

    async def revoke_token(self, refresh_token: str, user: UserModel) -> None:
        payload = payload = jwt.verify_token(refresh_token, TokenType.refresh_token)
        jti = payload.get("jti")

        if not jti or await self._token_repository.is_revoked_token(jti):
            raise jwt.INVALID_TOKEN

        await self._token_repository.create(
            CreateRevokeToken(jti=jti, user_id=user.id)
        )

    
    async def send_reset_password_token(
        self, reset_password: ResetPaasword
    ) -> None:
        phone_number = reset_password.phone_number

        user = await self._repository.get_by_phone_number(phone_number)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"User not found."
            )

        key = f"reset_{phone_number}"

        if await self._redis_repository.get(key):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many Request.",
            )
                # handling test user
        if setting.DEBUG and user.phone_number == "09445566778":
            token = 555555
            await self._redis_repository.set(key, token, setting.OTP_EXPIRE)

        else:
            token = self.OTP_token()
            await self._redis_repository.set(key, token, setting.OTP_EXPIRE)
            send_sms.delay(user.phone_number, f"`Mechanic` one time password: {token}")
    
    async def verify_reset_password_token(
        self, reset_password: VerifyResetPassword
    )-> None:
        key = f"reset_{reset_password.phone_number}"

        cache_token = await self._redis_repository.get(key)
        if not cache_token or int(cache_token) != reset_password.token:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail=f"Token is invalid or expierd.",
            )
        
        await self._redis_repository.delete(key)

        user = await self._repository.get_by_phone_number(reset_password.phone_number)
        password = UserPassword.generate_password_hash(reset_password.password)

        await self._repository.reset_password(user, password)