import uuid  # type: ignore

from typing import Any  # type: ignore
from datetime import datetime, timedelta  # type: ignore

from pydantic import UUID4
from sqlalchemy import select, update, insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from utils import utils
from auth.config import auth_config
from auth.exceptions import InvalidCredentials
from auth.schemas import AuthUser
from auth.security import check_password, hash_password
from auth.models import User, RefreshToken


async def create_user(db: AsyncSession, user_data: AuthUser) -> User:
    hashed_password = hash_password(user_data.password)
    created_user = User(id=str(uuid.uuid4()), email=user_data.email,
                        password=hashed_password)
    db.add(created_user)
    await db.commit()
    return created_user


async def get_user_by_id(db: AsyncSession, user_id: int) -> dict[str, Any] | None:
    select_query = (
        select(
            User
        )
        .where(
            User.id == user_id
        )
    )
    result = await db.execute(select_query)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    select_query = (
        select(
            User
        )
        .where(
            User.email == email
        )
    )
    result = await db.execute(select_query)
    return result.scalar_one_or_none()


async def create_refresh_token(
    db: AsyncSession,
    *,
    user_id: int,
    refresh_token: str | None = None
) -> str:
    if not refresh_token:
        refresh_token = utils.generate_random_alphanum(64)

    # insert_query = RefreshToken.insert().values(
    #     uuid=uuid.uuid4(),
    #     refresh_token=refresh_token,
    #     expires_at=datetime.now() + timedelta(seconds=auth_config.REFRESH_TOKEN_EXP),
    #     user_id=user_id,
    # )
    insert_query = insert(RefreshToken).values(
        id=uuid.uuid4(),
        refresh_token=refresh_token,
        expires_at=datetime.now() + timedelta(seconds=auth_config.REFRESH_TOKEN_EXP),
        user_id=user_id,
    )
    await db.execute(insert_query)

    return refresh_token


async def get_refresh_token(db: AsyncSession, refresh_token: str) -> dict[str, Any] | None:
    select_query = (
        select(
            RefreshToken
        )
        .where(
            RefreshToken.refresh_token == refresh_token
        )
        .options(selectinload(RefreshToken.user))
    )
    result = await db.execute(select_query)
    return result.scalar_one_or_none()


async def expire_refresh_token(db: AsyncSession, refresh_token_uuid: UUID4) -> None:
    update_query = (
        update(RefreshToken)
        .where(
            RefreshToken.id == refresh_token_uuid
        )
        .values(
            expires_at=datetime.now()
        )
    )
    await db.execute(update_query)


async def authenticate_user(db: AsyncSession, auth_data: AuthUser) -> User:
    user = await get_user_by_email(db, auth_data.email)
    if not user:
        raise InvalidCredentials()

    if not check_password(auth_data.password, user.password):
        raise InvalidCredentials()

    return user
