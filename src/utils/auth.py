from passlib.context import CryptContext
from uuid import uuid4
from typing import Any, Dict
import jwt as pyjwt
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, Header, status, Depends
from sqlalchemy.ext.asyncio.session import AsyncSession


from src.repositories.user import UserRepository
from src.schemas.auth import TokenType
from src.models.user import User as UserModel
from src.config import setting
from src.utils.singleton import SingletonMeta


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserPassword:
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> str:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def generate_password_hash(password: str) -> str:
        return pwd_context.hash(password)
    


class Jwt(metaclass=SingletonMeta):
    
    INVALID_TOKEN = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Session has been expired."
    )

    def normalize_token(self, token: str) -> str:
        return token.replace("Bearer ", "")
    
    def create_token(
        self,
        encode: dict,
        token_type: TokenType,
        expires_delta: timedelta = timedelta(days=setting.ACCESS_EXPIRE)
    ) -> str:
        to_encode = encode.copy()

        expire = datetime.now(timezone.utc) + expires_delta
        
        to_encode.update({"exp": expire, "token_type": token_type, "jti": str(uuid4())})
        
        encoded_jwt = pyjwt.encode(to_encode, setting.SECRET_KEY, algorithm=setting.JWT_ALGORITHM)

        return encoded_jwt
        
    def verify_token(self, token: str, token_type: TokenType) -> Dict[str, Any]:
        """ token need to be healty and will return payload """
        token = self.normalize_token(token)
        try:
            if not token:
                raise
            
            payload: dict = pyjwt.decode(token, key=setting.SECRET_KEY, algorithms=[setting.JWT_ALGORITHM])
            if payload["token_type"] != token_type:
                raise 
            
            return payload   
        except Exception:
            raise self.INVALID_TOKEN
        

async def get_current_user(
    access_token: str = Header(..., alias="Authorization"),
    repository: UserRepository = Depends(UserRepository)
) -> UserModel:
    payload = jwt.verify_token(access_token, TokenType.access_token)
    phone_number = payload.get("sub")
    if not phone_number:
        raise jwt.INVALID_TOKEN
    
    user = await repository.get_by_phone_number(phone_number)
    if not user:
        raise jwt.INVALID_TOKEN

    if not user.is_active or user.is_delete:
        raise jwt.INVALID_TOKEN
    
    return user

jwt = Jwt()