from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import LogIn, LogOut
from src import login_user

router = APIRouter()

@router.post("/cosmetology/login", response_model=LogOut, status_code=status.HTTP_201_CREATED)
async def cosmetology_login(
        login_user_info: LogIn,
        db: AsyncSession = Depends(get_db)
):
    access_token, refresh_token = await login_user(db=db, user_info=login_user_info)
    return LogOut(
        access_token=access_token,
        refresh_token=refresh_token
    )

