import json

from fastapi import HTTPException, status
from redis import RedisError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core import redis_client
from database import Category


async def get_categories_data(
    db: AsyncSession,
    category_id: int | None = None,
) -> list[dict]:
    if category_id is None:
        key = "categories:all"
    else:
        key = f"categories:id:{category_id}"

    # 1. Пытаемся получить данные из Redis.
    try:
        cached = await redis_client.get(key)

        if cached is not None:
            return json.loads(cached)

    except RedisError:
        pass

    # 2. Запрашиваем категории из БД.
    try:
        query = select(Category).options(
            selectinload(Category.procedures)
        )

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
    except RedisError:
        pass

    # 4. Возвращаем данные.
    return categories_data