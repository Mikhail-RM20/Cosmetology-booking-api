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


async def delete_entries(
    db: AsyncSession,
    id_entry: int,
) -> dict:
    """
    Удаляет запись пользователя на косметологическую процедуру.

    Args:
        db: AsyncSession - Асинхронная сессия базы данных.
        id_entry: int - id записи, которую необходимо удалить.

    Returns:
        dict - Данные удаленной записи:
            id: int - id записи.
            procedure_id: int - id процедуры.
            entry_date: date - Дата записи.
            entry_time: time - Время записи.
            name_user: str - Имя пользователя.
            surname_user: str - Фамилия пользователя.
            name_procedures: str - Название процедуры.
            price: int - Стоимость процедуры.

    Raises:
        HTTPException 404 - Запись не найдена.
        HTTPException 500 - Ошибка базы данных.
    """
    main_log.debug(
        "Функция delete_entries начала выполнение. "
        f"Получен запрос на удаление записи с id: {id_entry}."
    )

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
            main_log.warning(
                "Функция delete_entries: запись не найдена. "
                f"id_entry: {id_entry}."
            )

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

        main_log.debug(
            "Функция delete_entries успешно завершила свое выполнение. "
            f"Удалена запись с id: {id_entry}. "
            f"id_user: {result_check.user_id}, "
            f"id_procedure: {result_check.procedure_id}, "
            f"дата: {result_check.entry_date}, "
            f"время: {result_check.entry_time}."
        )

        return deleted_entry

    except SQLAlchemyError as error:
        await db.rollback()

        main_log.exception(
            "Функция delete_entries: произошла ошибка базы данных "
            f"при удалении записи с id: {id_entry}."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка БД.",
        ) from error
