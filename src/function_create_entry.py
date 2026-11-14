import logging.config

from core import dict_config
from database import EntryCosmetology
from fastapi import HTTPException, status
from schemas import EntryIn
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("services_logger")
main_log.setLevel(logging.DEBUG)


async def new_entry(
    db: AsyncSession, entry_data: EntryIn, id_user: int
) -> dict:
    """
    Создает новую запись пользователя на косметологическую процедуру.

    Args:
        db: AsyncSession - Асинхронная сессия базы данных.
        entry_data: EntryIn - Pydantic модель, проверяет данные:
            procedure_id: int - id процедуры.
            entry_date: date - Дата записи.
            entry_time: time - Время записи.
        id_user: int - id пользователя, который записывается.

    Returns:
        dict - Данные созданной записи:
            id: int - id записи.
            procedure_name: str - Название процедуры.
            user_name: str - Имя пользователя.
            user_surname: str - Фамилия пользователя.
            entry_date: date - Дата записи.
            entry_time: time - Время записи.

    Raises:
        HTTPException 409 - Выбранное время уже занято.
        HTTPException 409 - Ошибка целостности данных при создании записи.
        HTTPException 500 - Ошибка базы данных.
    """
    main_log.debug(
        "Функция new_entry начала выполнение. "
        f"Получен запрос на создание записи. "
        f"id_user: {id_user}, id_procedure: {entry_data.procedure_id}, "
        f"дата: {entry_data.entry_date}, время: {entry_data.entry_time}."
    )

    try:
        id_procedure = entry_data.procedure_id
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
            main_log.warning(
                "Функция new_entry: выбранное время уже занято. "
                f"id_user: {id_user}, id_procedure: {id_procedure}, "
                f"дата: {entry_date}, время: {entry_time}."
            )

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

        main_log.debug(
            "Функция new_entry успешно завершила свое выполнение. "
            f"Создана запись с id: {result_data_entry.id}. "
            f"id_user: {id_user}, id_procedure: {id_procedure}, "
            f"дата: {result_data_entry.entry_date}, "
            f"время: {result_data_entry.entry_time}."
        )

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

        main_log.warning(
            "Функция new_entry: произошла ошибка целостности данных. "
            f"Не удалось создать запись для пользователя с id: {id_user}. "
            f"id_procedure: {entry_data.procedure_id}, "
            f"дата: {entry_data.entry_date}, "
            f"время: {entry_data.entry_time}."
        )

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="На это время уже есть бронь.",
        )

    except SQLAlchemyError:
        await db.rollback()

        main_log.exception(
            "Функция new_entry: произошла ошибка базы данных "
            "при создании записи. "
            f"id_user: {id_user}, id_procedure: {entry_data.procedure_id}, "
            f"дата: {entry_data.entry_date}, "
            f"время: {entry_data.entry_time}."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка БД. / Database error.",
        )
