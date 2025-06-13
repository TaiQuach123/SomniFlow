from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from uuid import UUID


class GoogleUserInfo(BaseModel):
    email: str
    name: str
    picture: str
    sub: str


class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class UserOut(BaseModel):
    id: UUID
    email: EmailStr
    thread_ids: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str

    class Config:
        from_attributes = True


class TokenData(BaseModel):
    id: Optional[int] = None
