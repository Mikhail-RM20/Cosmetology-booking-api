from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import EntryCosmetology


async def get_entries(
    db: AsyncSession, entries_date: date | None = None
) -> list[EntryCosmetology]:
    try:
        stmt = (
            select(EntryCosmetology)
            .options(
                joinedload(EntryCosmetology.user),
                joinedload(EntryCosmetology.procedure),
            )
            .order_by(
                EntryCosmetology.entry_date,
                EntryCosmetology.entry_time,
            )
        )
        if entries_date is not None:
            stmt = stmt.where(EntryCosmetology.entry_date == entries_date)

        result = await db.scalars(stmt)
        return list(result.unique().all())

    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка БД."
        ) from error
