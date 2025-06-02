import json
from datetime import timedelta, datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from authlib.integrations.starlette_client import OAuth
from fastapi.responses import RedirectResponse
from fastapi import APIRouter, Depends, HTTPException, Request, Response, Cookie
from fastapi.security.oauth2 import OAuth2PasswordRequestForm

from backend.auth.service import AuthService
from backend.auth.utils import create_access_token, decode_token
from backend.auth.dependencies import get_refresh_token
from backend.auth.schemas import UserCreate, UserOut, Token, GoogleUserInfo
from backend.database import get_async_session
from backend.auth.config import jwt_config, oauth_config
from backend.redis import redis_client
from backend.auth.models import User, AuthProvider
from backend.auth.dependencies import get_current_user


oauth = OAuth()
oauth.register(
    name="google",
    client_id=oauth_config.GOOGLE_CLIENT_ID,
    client_secret=oauth_config.GOOGLE_CLIENT_SECRET,
    client_kwargs={"scope": "openid email profile"},
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
)

router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()


@router.get("/google/login")
async def login_via_google(request: Request):
    redirect_uri = request.url_for("google_callback")
    print(redirect_uri)
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/google/callback")
async def google_callback(
    request: Request, session: AsyncSession = Depends(get_async_session)
):
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get("userinfo")
        if not user_info:
            raise HTTPException(status_code=400, detail="No user info from Google")
        google_user = GoogleUserInfo(
            email=user_info["email"],
            sub=user_info["sub"],
            name=user_info["name"],
            picture=user_info["picture"],
        )
        user = await auth_service.create_oauth_user(google_user, session)

        access_token = create_access_token(
            user_data={
                "email": user.email,
                "user_id": str(user.id),
            }
        )
        refresh_token = create_access_token(
            user_data={
                "email": user.email,
                "user_id": str(user.id),
            },
            refresh=True,
            expiry=timedelta(days=jwt_config.REFRESH_TOKEN_EXPIRE_DAYS),
        )
        # Store refresh token JTI in Redis
        refresh_token_data = decode_token(refresh_token)
        jti = refresh_token_data["jti"]
        exp = refresh_token_data["exp"]
        ttl = int(exp - datetime.now(UTC).timestamp())
        await redis_client.set(jti, str(user.id), ex=ttl)

        frontend_url = (
            "http://localhost:3000/auth/callback"  # Or your deployed frontend URL
        )
        response = RedirectResponse(f"{frontend_url}?access_token={access_token}")
        # Set the refresh token as an HTTP-only, Secure cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,  # Set to True in production (requires HTTPS)
            samesite="lax",  # Or "strict" depending on your needs
            max_age=60 * 60 * 24 * jwt_config.REFRESH_TOKEN_EXPIRE_DAYS,
            path="/",
        )
        return response

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/register", response_model=UserOut, status_code=201)
async def register(
    user: UserCreate, session: AsyncSession = Depends(get_async_session)
):
    user_exists = await auth_service.user_exists(user.email, session)
    if user_exists:
        raise HTTPException(
            status_code=403, detail="User with this email already exists"
        )
    new_user = await auth_service.create_user(user, session)
    return new_user


@router.post("/login", response_model=Token)
async def login(
    login_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    user = await auth_service.authenticate_user(
        login_data.username, login_data.password, session
    )

    access_token = create_access_token(
        user_data={
            "email": user.email,
            "user_id": str(user.id),
        }
    )
    refresh_token = create_access_token(
        user_data={
            "email": user.email,
            "user_id": str(user.id),
        },
        refresh=True,
        expiry=timedelta(days=jwt_config.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    # Store refresh token JTI in Redis
    refresh_token_data = decode_token(refresh_token)
    jti = refresh_token_data["jti"]
    exp = refresh_token_data["exp"]
    ttl = int(exp - datetime.now(UTC).timestamp())
    await redis_client.set(jti, str(user.id), ex=ttl)

    response = Response(
        content=json.dumps(
            {
                "access_token": access_token,
                "token_type": "Bearer",
            }
        ),
        media_type="application/json",
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Set to True in production
        samesite="lax",
        max_age=60 * 60 * 24 * jwt_config.REFRESH_TOKEN_EXPIRE_DAYS,
        path="/",
    )
    return response


@router.post("/refresh", response_model=Token)
async def get_new_access_token(refresh_token: str = Cookie(None)):
    token_details = decode_token(refresh_token)
    jti = token_details["jti"]
    jti_exists = await redis_client.exists(jti)
    if not jti_exists:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    # Remove the old refresh token's JTI from Redis (invalidate old refresh token)
    await redis_client.delete(jti)

    # Generate new refresh token and access token
    user_data = token_details["user"]
    new_access_token = create_access_token(user_data=user_data)
    new_refresh_token = create_access_token(
        user_data=user_data,
        refresh=True,
        expiry=timedelta(days=jwt_config.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    # Store new refresh token JTI in Redis
    new_refresh_token_data = decode_token(new_refresh_token)
    new_jti = new_refresh_token_data["jti"]
    new_exp = new_refresh_token_data["exp"]
    new_ttl = int(new_exp - datetime.now(UTC).timestamp())
    await redis_client.set(new_jti, str(user_data["user_id"]), ex=new_ttl)

    response = Response(
        content=json.dumps(
            {
                "access_token": new_access_token,
                "token_type": "Bearer",
            }
        ),
        media_type="application/json",
    )
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        secure=True,  # Set to True in production
        samesite="lax",
        max_age=60 * 60 * 24 * jwt_config.REFRESH_TOKEN_EXPIRE_DAYS,
        path="/",
    )
    return response


@router.get("/me")
async def read_users_me(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    # Get the first auth_provider for the user
    result = await session.execute(
        select(AuthProvider).where(AuthProvider.user_id == user.id)
    )
    auth_provider = result.scalars().first()
    avatar_url = auth_provider.avatar_url if auth_provider else None
    return {
        "authenticated": user is not None,
        "user": {
            "id": user.id,
            "email": user.email,
            "thread_ids": user.thread_ids,
            "created_at": user.created_at,
            "avatar_url": avatar_url,
        },
    }


@router.post("/logout")
async def logout(refresh_token: str = Depends(get_refresh_token)):
    # Remove refresh token JTI from Redis
    try:
        token_details = decode_token(refresh_token)
        jti = token_details["jti"]
        await redis_client.delete(jti)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "Logged out"}
