import json

from fastapi import HTTPException, status
from redis import RedisError
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core import redis_client
from database import Procedures


async def get_procedures(
    db: AsyncSession,
    procedure_id: int,
) -> dict:
    key = f"procedures:id:{procedure_id}"

    # 1. Пытаемся взять данные из Redis.
    try:
        cached = await redis_client.get(key)

        if cached is not None:
            return json.loads(cached)

    except RedisError:
        pass

    # 2. Запрос в БД.
    try:
        result = await db.execute(
            select(Procedures).where(Procedures.id == procedure_id)
        )

        procedure = result.scalar_one_or_none()

        if procedure is None:
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
    except RedisError:
        pass

    # 4. Возвращаем данные.
    return procedure_data
