from enum import Enum
import re

from pydantic import BaseModel, Field, field_validator
from fastapi import HTTPException, status

class SignupSendOTP(BaseModel):
    phone_number: str
    password: str
    first_name: str = Field(..., max_length=100)
    last_name: str = Field(..., max_length=100)

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, v: str) -> str:
        pattern = r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$'
        
        if not re.match(pattern, v):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation."
            )
        
        return v
    
    @field_validator("phone_number", mode="after")
    @classmethod
    def validate_phone_number(cls, v: str) -> str:
        pattern = r'^09\d{9}$'
        
        if not re.match(pattern, v):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation."
            )
        
        return v
    

class SignupVerifyOTP(BaseModel):
    phone_number: str
    token: int



class TokenType(str, Enum):
    access_token = "access"
    refresh_token = "refresh"


class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    user_id: int


class CreateRevokeToken(BaseModel):
    jti: str
    user_id: int


class TokenVerifyOut(BaseModel):
    access_token: str
    token_type: TokenType


class Login(BaseModel):
    phone_number: str
    password: str


class ResetPaasword(BaseModel):
    phone_number: str

class VerifyResetPassword(BaseModel):
    phone_number: str
    password: str
    token: int

    @field_validator("password", mode="after")
    @classmethod
    def validate_password(cls, v: str) -> str:
        pattern = r'^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[#?!@$%^&*-]).{8,}$'
        
        if not re.match(pattern, v):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password validation."
            )
        
        return v