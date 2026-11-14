import logging.config

from core import dict_config
from schemas import LogIn
from sqlalchemy.ext.asyncio import AsyncSession
from utils import WorkTokens

from src import get_user_db

logging.config.dictConfig(dict_config)
main_log = logging.getLogger("services_logger")
main_log.setLevel(logging.DEBUG)

work_tokens = WorkTokens()


async def login_user(db: AsyncSession, user_info: LogIn) -> tuple[str, str]:
    """
    Аутентифицирует пользователя и создает пару токенов.

    Args:
        db: AsyncSession - Асинхронная сессия базы данных.
        user_info: LogIn - Pydantic модель, проверяет данные:
            phone: str - Номер телефона пользователя.
            password: str - Пароль пользователя.

    Returns:
        tuple[str, str] - Пара токенов пользователя:
            access_token: str - Access-токен пользователя.
            refresh_token: str - Refresh-токен пользователя.

    Raises:
        HTTPException 401 - Пользователь не зарегистрирован
            или введен неверный пароль.
        HTTPException 500 - Ошибка базы данных.
    """
    main_log.debug(
        "Функция login_user начала выполнение. "
        "Получен запрос на аутентификацию пользователя."
    )

    id_user = await get_user_db(db, user_info)

    main_log.debug(
        "Функция login_user: пользователь успешно аутентифицирован. "
        f"id_user: {id_user}. "
        "Начата генерация access и refresh токенов."
    )

    (
        access_token,
        refresh_token,
    ) = await work_tokens.pair_generation_access_refresh(
        db=db, id_user=id_user
    )

    main_log.debug(
        "Функция login_user успешно завершила свое выполнение. "
        f"Для пользователя с id: {id_user} "
        "успешно сгенерированы access и refresh токены."
    )

    return access_token, refresh_token
