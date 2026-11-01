from typing import Annotated

from database import User, get_db
from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import get_current_access_token, oauth2_scheme


async def get_role_person(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    try:
        user_id = await get_current_access_token(token=token)

        check_role = await db.execute(
            select(User).where(User.id == user_id, User.role == "admin")
        )
        result = check_role.scalar_one_or_none()

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Это действие может выполнить только администратор.",
            )
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка БД.",
        ) from error
