from sqlalchemy import select
from sqlalchemy.exc import NoResultFound, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import RegistrationIn
from database import User
from fastapi import HTTPException, status
from core import hash_password

async def create_new_user(db: AsyncSession, user_info: RegistrationIn) -> int:
    try:
        name = user_info.name.title()
        surname = user_info.surname.title()
        phone = user_info.phone
        password = user_info.password
        email = user_info.email

        database_query = await db.execute(select(User)
                                          .where(User.phone == user_info.phone))
        result_check_user = database_query.scalar_one_or_none()
        if result_check_user is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Пользователь с таким номером уже зарегистрирован.")
        hashed_password = hash_password(password)

        new_user = User(
            name=name,
            surname=surname,
            phone=phone,
            role="user",
            hash_password=hashed_password,
            email=email,
        )

        db.add(new_user)
        await db.commit()

        return new_user.id


    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка БД. / Database error.",
        )