from database import EntryCosmetology
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload


async def delete_entries(
    db: AsyncSession,
    id_entry: int,
) -> dict:
    try:
        check_entry = await db.execute(
            select(EntryCosmetology)
            .options(
                joinedload(EntryCosmetology.user),
                joinedload(EntryCosmetology.procedure),
            )
            .where(EntryCosmetology.id == id_entry)
        )

        result_check = check_entry.scalar_one_or_none()

        if result_check is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Записи не найдено.",
            )

        deleted_entry = {
            "id": result_check.id,
            "procedure_id": result_check.procedure_id,
            "entry_date": result_check.entry_date,
            "entry_time": result_check.entry_time,
            "name_user": result_check.user.name,
            "surname_user": result_check.user.surname,
            "name_procedures": result_check.procedure.name_procedures,
            "price": result_check.procedure.price,
        }

        await db.delete(result_check)
        await db.commit()

        return deleted_entry

    except SQLAlchemyError as error:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка БД.",
        ) from error
