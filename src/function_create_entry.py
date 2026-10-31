from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import EntryCosmetology
from schemas import EntryIn


async def new_entry(db: AsyncSession, entry_data: EntryIn, id_user: int) -> dict:
    try:
        id_procedure = entry_data.id_procedure
        entry_date = entry_data.entry_date
        entry_time = entry_data.entry_time

        check_entry = await db.execute(
            select(EntryCosmetology).where(
                EntryCosmetology.entry_date == entry_date,
                EntryCosmetology.entry_time == entry_time,
            )
        )
        result_check_entry = check_entry.scalar_one_or_none()

        if result_check_entry:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Ошибка. Данное окно уже занято."
                "\n Выберите другую дату или время.",
            )
        new_create = EntryCosmetology(
            user_id=id_user,
            entry_date=entry_date,
            entry_time=entry_time,
            procedure_id=id_procedure,
        )
        db.add(new_create)
        await db.commit()

        data_entry = await db.execute(
            select(EntryCosmetology)
            .options(
                selectinload(EntryCosmetology.procedure),
                selectinload(EntryCosmetology.user),
            )
            .where(EntryCosmetology.id == new_create.id)
        )
        result_data_entry = data_entry.scalar_one()

        return {
            "id": result_data_entry.id,
            "procedure_name": result_data_entry.procedure.name_procedures,
            "user_name": result_data_entry.user.name,
            "user_surname": result_data_entry.user.surname,
            "entry_date": result_data_entry.entry_date,
            "entry_time": result_data_entry.entry_time,
        }

    except HTTPException:
        raise

    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="На это время уже есть бронь.",
        )

    except SQLAlchemyError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка БД. / Database error.",
        )
