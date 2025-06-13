from backend.auth.models import User, AuthProvider
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.auth.schemas import UserCreate, GoogleUserInfo
from backend.auth.utils import generate_passwd_hash, verify_password
from fastapi import HTTPException


class AuthService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def user_exists(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        return user is not None

    async def create_user(self, user_data: UserCreate, session: AsyncSession):
        # Create the user first
        new_user = User(email=user_data.email, thread_ids=[])
        session.add(new_user)
        await session.flush()  # This will get us the user's ID without committing

        # Generate avatar URL using the first letter of the email
        first_letter = user_data.email[0].upper()
        avatar_url = f"https://ui-avatars.com/api/?name={first_letter}&background=random&size=128"

        # Create the auth provider with the hashed password and avatar_url
        auth_provider = AuthProvider(
            user_id=new_user.id,
            provider="email",
            hashed_password=generate_passwd_hash(user_data.password),
            avatar_url=avatar_url,
        )
        session.add(auth_provider)

        await session.commit()
        await session.refresh(new_user)
        return new_user

    async def create_oauth_user(self, user_data: GoogleUserInfo, session: AsyncSession):
        # Check if user exists
        user = await self.get_user_by_email(user_data.email, session)
        if not user:
            # Create new user
            user = User(email=user_data.email, thread_ids=[])
            session.add(user)
            await session.flush()  # Get user.id

        # Check if Google AuthProvider already exists for this user
        auth_provider = await self.get_auth_provider(user.id, "google", session)

        if not auth_provider:
            # Add Google AuthProvider
            auth_provider = AuthProvider(
                user_id=user.id,
                provider="google",
                provider_user_id=user_data.sub,
                name=user_data.name,
                avatar_url=user_data.picture,
                hashed_password=None,
            )
            session.add(auth_provider)
            await session.commit()
            await session.refresh(user)
        return user

    async def get_auth_provider(self, user_id, provider, session: AsyncSession):
        statement = select(AuthProvider).where(
            AuthProvider.user_id == user_id, AuthProvider.provider == provider
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def authenticate_user(self, email: str, password: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        if not user:
            raise HTTPException(status_code=403, detail="Invalid credentials")

        auth_provider = await self.get_auth_provider(user.id, "email", session)

        if not auth_provider:
            raise HTTPException(status_code=403, detail="No email provider found")

        if not verify_password(password, auth_provider.hashed_password):
            raise HTTPException(status_code=403, detail="Wrong password")

        return user
