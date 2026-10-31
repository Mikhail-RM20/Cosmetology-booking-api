import redis.asyncio as redis

from core import config_set

redis_client = redis.Redis(
    # Импортируем HOST на котором будет работать Redis.
    # Импортируем PORT, который будет слушать Redis.
    # Импортируем базу внутри Redis.
    # decode_responses - Для возврата, строк вместо байтов.
    host=config_set.redis_host,
    port=config_set.redis_port,
    db=config_set.redis_db,
    decode_responses=True,
)
