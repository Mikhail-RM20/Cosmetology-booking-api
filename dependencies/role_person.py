from sqlalchemy.ext.asyncio import AsyncSession
from database import User
from sqlalchemy import select

async def get_role_person(db: AsyncSession, user_id: int):
    pass