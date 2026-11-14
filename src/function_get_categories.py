import json
import logging.config

from core import dict_config, redis_client
from database import Category
from fastapi import HTTPException, status
from redis import RedisError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("services_logger")
main_log.setLevel(logging.DEBUG)


async def get_categories_data(
    db: AsyncSession,
    category_id: int | None = None,
) -> list[dict]:
    """
    Получает список категорий косметологических процедур.

    Args:
        db: AsyncSession - Асинхронная сессия базы данных.
        category_id: int | None - id категории. Если не указан,
            возвращаются все категории.

    Returns:
        list[dict] - Список категорий с процедурами:
            id: int - id категории.
            name: str - Название категории.
            procedures: list[dict] - Список процедур категории:
                id: int - id процедуры.
                name: str - Название процедуры.
                description: str - Описание процедуры.
                price: int - Стоимость процедуры.

    Raises:
        HTTPException 500 - Ошибка базы данных.
    """
    if category_id is None:
        key = "categories:all"

        main_log.debug(
            "Функция get_categories_data начала выполнение. "
            "Получен запрос на получение всех категорий."
        )
    else:
        key = f"categories:id:{category_id}"

        main_log.debug(
            "Функция get_categories_data начала выполнение. "
            f"Получен запрос на получение категории с id: {category_id}."
        )

    # 1. Пытаемся получить данные из Redis.
    try:
        cached = await redis_client.get(key)

        if cached is not None:
            main_log.debug(
                "Функция get_categories_data: данные получены из Redis. "
                f"Ключ: {key}."
            )

            return json.loads(cached)

        main_log.debug(
            "Функция get_categories_data: данные в Redis не найдены. "
            f"Ключ: {key}. Данные будут получены из базы данных."
        )

    except RedisError:
        main_log.warning(
            "Функция get_categories_data: не удалось получить данные "
            f"из Redis. Ключ: {key}. "
            "Данные будут получены из базы данных."
        )

    # 2. Запрашиваем категории из БД.
    try:
        query = select(Category).options(selectinload(Category.procedures))

        if category_id is not None:
            query = query.where(Category.id == category_id)

        query = query.order_by(Category.id)

        result = await db.execute(query)
        categories = result.scalars().all()

        categories_data = [
            {
                "id": category.id,
                "name": category.name,
                "procedures": [
                    {
                        "id": procedure.id,
                        "name": procedure.name_procedures,
                        "description": procedure.description,
                        "price": procedure.price,
                    }
                    for procedure in category.procedures
                ],
            }
            for category in categories
        ]

    except SQLAlchemyError:
        await db.rollback()

        main_log.exception(
            "Функция get_categories_data: произошла ошибка базы данных "
            "при получении категорий. "
            f"category_id: {category_id if category_id is not None else 'не указан'}."
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка базы данных.",
        )

    # 3. Сохраняем результат в Redis.
    try:
        await redis_client.set(
            key,
            json.dumps(categories_data, ensure_ascii=False),
            ex=300,
        )

        main_log.debug(
            "Функция get_categories_data: данные успешно сохранены в Redis. "
            f"Ключ: {key}. Количество категорий: {len(categories_data)}. "
            "Время жизни кеша: 300 секунд."
        )

    except RedisError:
        main_log.warning(
            "Функция get_categories_data: не удалось сохранить данные в Redis. "
            f"Ключ: {key}. "
            "Функция продолжит выполнение без кеширования."
        )

    # 4. Возвращаем данные.
    main_log.debug(
        "Функция get_categories_data успешно завершила свое выполнение. "
        f"Получено категорий: {len(categories_data)}. "
        f"Ключ Redis: {key}."
    )

    return categories_data
