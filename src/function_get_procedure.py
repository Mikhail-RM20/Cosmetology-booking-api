import json
from typing import Optional

from fastapi import HTTPException, status
from redis import RedisError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import Procedures
from core import redis_client

async def get_procedures(
    db: AsyncSession,
    price: Optional[int] = None,
) -> list[dict]:
    if price is None:
        key = "procedures:all"
    else:
        key = f"procedures:price:{price}"

    # 1. Пытаемся взять данные из Redis
    try:
        cached = await redis_client.get(key)

        if cached is not None:
            return json.loads(cached)

    except RedisError:
        pass

    # 2. Запрос в БД
    try:
        query = select(Procedures)

        if price is not None:
            query = query.where(Procedures.price == price)

        result = await db.execute(query)
        procedures = result.scalars().all()

        procedures_data = [
            {
                "id": procedure.id,
                "name_procedure": procedure.name_procedures,
                "description": procedure.description,
                "price": procedure.price,
            }
            for procedure in procedures
        ]

    except SQLAlchemyError:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка базы данных.",
        )

    # 3. Сохраняем в Redis
    try:
        await redis_client.set(
            key,
            json.dumps(procedures_data, ensure_ascii=False),
            ex=300,
        )

    except RedisError:
        pass

    # 4. Возвращаем данные
    return procedures_data