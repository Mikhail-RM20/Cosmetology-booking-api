from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from schemas import LogIn, LogOut

router = APIRouter()

@router.post("/cosmetology/login", response_model=LogOut, status_code=status.HTTP_201_CREATED)
async def cosmetology_login(
        login_user: LogIn,
        db: AsyncSession = Depends(get_db)
):
    pass

