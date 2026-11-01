from typing import Annotated

from database import get_db
from fastapi import APIRouter, Depends, status
from schemas import RegistrationIn, RegistrationOut
from sqlalchemy.ext.asyncio import AsyncSession
from src import create_new_user

router = APIRouter()


@router.post(
    "/cosmetology/registration",
    response_model=RegistrationOut,
    status_code=status.HTTP_201_CREATED,
)
async def cosmetology_registration(
    user_info: RegistrationIn,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    new_user = await create_new_user(db=db, user_info=user_info)
    return RegistrationOut(
        message="Вы успешно зарегистрировались.", id_user=new_user
    )
