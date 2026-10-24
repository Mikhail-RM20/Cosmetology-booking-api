from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import LogIn
from sqlalchemy import select
from database import User
from core import verify_password

async def get_user_db(db: AsyncSession, user_info: LogIn) -> int:
    try:
        phone = user_info.phone
        password = user_info.password

        get_password = await db.execute(select(User)
                                        .where(User.phone==phone))
        result_get_password = get_password.scalar_one_or_none()
        if result_get_password is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Пользователь не зарегистрирован.")

        verify_check_password = verify_password(password, result_get_password.hash_password)
        if not verify_check_password:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Неверный пароль.")

        return result_get_password.id

    except SQLAlchemyError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Ошибка базы данных.") from error