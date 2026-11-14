import logging.config
from datetime import date

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


async def get_entries(
    db: AsyncSession, entries_date: date | None = None
) -> list[EntryCosmetology]:
    """
    Получает список записей на косметологические процедуры.

    Args:
        db: AsyncSession - Асинхронная сессия базы данных.
        entries_date: date | None - Дата, по которой необходимо
            отфильтровать записи. Если не указана, возвращаются
            все записи.

    Returns:
        list[EntryCosmetology] - Список записей, отсортированный
        по дате и времени.

    Raises:
        HTTPException 500 - Ошибка базы данных.
    """
    if entries_date is not None:
        main_log.debug(
            "Функция get_entries начала выполнение. "
            f"Получен запрос на получение записей за дату: {entries_date}."
        )
    else:
        main_log.debug(
            "Функция get_entries начала выполнение. "
            "Получен запрос на получение всех записей."
        )

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
        entries = list(result.unique().all())

        main_log.debug(
            "Функция get_entries успешно завершила свое выполнение. "
            f"Получено записей: {len(entries)}. "
            f"Дата фильтрации: {entries_date if entries_date is not None else 'не указана'}."
        )

        return entries

    except SQLAlchemyError as error:
        main_log.exception(
            "Функция get_entries: произошла ошибка базы данных "
            "при получении списка записей. "
            f"Дата фильтрации: {entries_date if entries_date is not None else 'не указана'}."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка БД.",
        ) from error
