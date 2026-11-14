import json
import logging.config

from core import dict_config, redis_client
from database import Procedures
from fastapi import HTTPException, status
from redis import RedisError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("services_logger")
main_log.setLevel(logging.DEBUG)


async def get_procedures(
    db: AsyncSession,
    procedure_id: int,
) -> dict:
    """
    Получает данные косметологической процедуры по её id.

    Args:
        db: AsyncSession - Асинхронная сессия базы данных.
        procedure_id: int - id процедуры.

    Returns:
        dict - Данные процедуры:
            id: int - id процедуры.
            name_procedure: str - Название процедуры.
            description: str - Описание процедуры.
            price: int - Стоимость процедуры.

    Raises:
        HTTPException 404 - Процедура не найдена.
        HTTPException 500 - Ошибка базы данных.
    """
    key = f"procedures:id:{procedure_id}"

    main_log.debug(
        "Функция get_procedures начала выполнение. "
        f"Получен запрос на получение процедуры с id: {procedure_id}."
    )

    # 1. Пытаемся взять данные из Redis.
    try:
        cached = await redis_client.get(key)

        if cached is not None:
            main_log.debug(
                "Функция get_procedures: данные получены из Redis. "
                f"Ключ: {key}."
            )

            return json.loads(cached)

        main_log.debug(
            "Функция get_procedures: данные в Redis не найдены. "
            f"Ключ: {key}. Данные будут получены из базы данных."
        )

    except RedisError:
        main_log.warning(
            "Функция get_procedures: не удалось получить данные из Redis. "
            f"Ключ: {key}. "
            "Данные будут получены из базы данных."
        )

    # 2. Запрос в БД.
    try:
        result = await db.execute(
            select(Procedures).where(Procedures.id == procedure_id)
        )

        procedure = result.scalar_one_or_none()

        if procedure is None:
            main_log.warning(
                "Функция get_procedures: процедура не найдена. "
                f"procedure_id: {procedure_id}."
            )

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Процедура не найдена.",
            )

        procedure_data = {
            "id": procedure.id,
            "name_procedure": procedure.name_procedures,
            "description": procedure.description,
            "price": procedure.price,
        }

    except SQLAlchemyError:
        await db.rollback()

        main_log.exception(
            "Функция get_procedures: произошла ошибка базы данных "
            "при получении процедуры. "
            f"procedure_id: {procedure_id}."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка базы данных.",
        )

    # 3. Сохраняем в Redis.
    try:
        await redis_client.set(
            key,
            json.dumps(procedure_data, ensure_ascii=False),
            ex=300,
        )

        main_log.debug(
            "Функция get_procedures: данные успешно сохранены в Redis. "
            f"Ключ: {key}. "
            "Время жизни кеша: 300 секунд."
        )

    except RedisError:
        main_log.warning(
            "Функция get_procedures: не удалось сохранить данные в Redis. "
            f"Ключ: {key}. "
            "Функция продолжит выполнение без кеширования."
        )

    # 4. Возвращаем данные.
    main_log.debug(
        "Функция get_procedures успешно завершила свое выполнение. "
        f"Получена процедура с id: {procedure_id}. "
        f"Ключ Redis: {key}."
    )

    return procedure_data
