import time
from fastapi import HTTPException, Depends
from fastapi.security.oauth2 import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_async_session
from backend.auth.models import User
from backend.auth.utils import decode_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
):
    user_details = decode_token(token)
    if not user_details:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if user_details["refresh"]:
        raise HTTPException(status_code=401, detail="Refresh token is not allowed")
    user = await session.execute(
        select(User).where(User.id == user_details["user"]["user_id"])
    )
    user = user.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user


async def get_refresh_token(token: str = Depends(oauth2_scheme)):
    user_details = decode_token(token)
    if not user_details:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user_details["refresh"]:
        raise HTTPException(status_code=401, detail="Please provide a refresh token")
    return token


async def get_current_user_id(token: str = Depends(oauth2_scheme)):
    user_details = decode_token(token)
    if not user_details:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return user_details["user"]["user_id"]
