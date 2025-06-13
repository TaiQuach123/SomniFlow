import jwt
import uuid
from passlib.context import CryptContext
from datetime import timedelta, datetime, UTC
from backend.auth.config import jwt_config
from fastapi import HTTPException
# import logging

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_passwd_hash(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
    user_data: dict, expiry: timedelta = None, refresh: bool = False
):
    payload = {}
    payload["user"] = user_data
    payload["exp"] = int(
        (
            datetime.now(UTC)
            + (
                expiry
                if expiry
                else timedelta(minutes=jwt_config.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
        ).timestamp()
    )
    payload["jti"] = str(uuid.uuid4())
    payload["refresh"] = refresh

    token = jwt.encode(
        payload=payload,
        key=jwt_config.JWT_SECRET,
        algorithm=jwt_config.JWT_ALGORITHM,
    )

    return token


def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            token,
            jwt_config.JWT_SECRET,
            algorithms=[jwt_config.JWT_ALGORITHM],
        )
        required_claims = ["user", "exp", "jti", "refresh"]
        for claim in required_claims:
            if claim not in token_data:
                raise HTTPException(
                    status_code=401, detail=f"Token missing required claim: {claim}"
                )
        return token_data

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")

    except jwt.PyJWTError as e:
        print(f"Error decoding token: {e}")
        return None
