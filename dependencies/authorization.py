from core import dict_config
import logging.config

from fastapi.security import OAuth2PasswordBearer
from utils import WorkTokens

# Настройка логирования в файле.
logging.config.dictConfig(dict_config)
main_log = logging.getLogger("services_logger")
main_log.setLevel(logging.DEBUG)


# Используем oauth2_scheme для зависимости, чтобы достать токен из заголовка.
# Используем также oauth2_scheme, чтобы указать в Swagger UI кнопку Authorize.

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/cosmetology/login")
work_tokens = WorkTokens()


async def get_current_access_token(token: str) -> int:
    """
    Функция проверки access - токена.
    Проверяет токен на действительность и работоспособность.
    Подробнее можно узнать в /utils/utils_tokens.py

    Args:
        token: str -  Access - токен пользователя.

    Returns:
        user_id: int - Возвращает ID пользователя, если проверка успешна.

    """
    main_log.debug("Начало проверки access - токена.")
    user_id = work_tokens.check_access_token(access_token=token)
    return user_id
