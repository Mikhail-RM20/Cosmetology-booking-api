from typing import Annotated

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from database import User, get_db
from sqlalchemy import select
from dependencies import oauth2_scheme, get_current_access_token
from fastapi import Depends, HTTPException, status


async def get_role_person(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: AsyncSession = Depends(get_db),
) -> None:
    try:
        user_id = await get_current_access_token(token=token)

        check_role = await db.execute(select(User)
                                      .where(User.id == user_id,
                                             User.role == "admin"))
        result = check_role.scalar_one_or_none()

        if result is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Это действие может выполнить только администратор.")
    except SQLAlchemyError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Ошибка БД.") from error
