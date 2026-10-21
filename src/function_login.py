from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import LogIn


async def login_user(db: AsyncSession, user_info: LogIn):
    pass