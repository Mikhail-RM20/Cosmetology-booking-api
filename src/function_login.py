from sqlalchemy.ext.asyncio import AsyncSession

from schemas import LogIn
from src import get_user_db
from utils import WorkTokens

work_tokens = WorkTokens()


async def login_user(db: AsyncSession, user_info: LogIn) -> tuple[str, str]:
    id_user = await get_user_db(db, user_info)
    access_token, refresh_token = await work_tokens.pair_generation_access_refresh(
        db=db, id_user=id_user
    )
    return access_token, refresh_token
