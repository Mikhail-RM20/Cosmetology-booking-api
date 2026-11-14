import logging.config

from core import dict_config
from database import EntryCosmetology
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("services_logger")
main_log.setLevel(logging.DEBUG)


async def get_user_entries(
    db: AsyncSession, user_id: int
) -> list[EntryCosmetology]:
    """
    Получает список всех записей конкретного пользователя.
    """
    main_log.debug(
        "Функция get_user_entries начала выполнение. user_id: %s.", user_id
    )
    try:
        stmt = (
            select(EntryCosmetology)
            .options(joinedload(EntryCosmetology.procedure))
            .where(EntryCosmetology.user_id == user_id)
            .order_by(
                EntryCosmetology.entry_date,
                EntryCosmetology.entry_time,
            )
        )
        result = await db.scalars(stmt)
        return list(result.unique().all())

    except SQLAlchemyError as error:
        main_log.exception(
            "Функция get_user_entries: ошибка БД при получении записей пользователя."
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка базы данных.",
        ) from error


async def cancel_user_entry(
    db: AsyncSession, user_id: int, entry_id: int
) -> None:
    """
    Отменяет (удаляет) запись, принадлежащую текущему пользователю.
    """
    main_log.debug(
        "Функция cancel_user_entry начала выполнение. user_id: %s, entry_id: %s.",
        user_id,
        entry_id,
    )
    try:
        result = await db.execute(
            select(EntryCosmetology).where(
                EntryCosmetology.id == entry_id,
                EntryCosmetology.user_id == user_id,
            )
        )
        entry = result.scalar_one_or_none()

        if entry is None:
            main_log.warning(
                "Запись %s не найдена или не принадлежит пользователю %s.",
                entry_id,
                user_id,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Запись не найдена.",
            )

        await db.delete(entry)
        await db.commit()

    except HTTPException:
        raise

    except SQLAlchemyError as error:
        await db.rollback()
        main_log.exception(
            "Функция cancel_user_entry: ошибка БД при отмене записи."
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка базы данных.",
        ) from error
