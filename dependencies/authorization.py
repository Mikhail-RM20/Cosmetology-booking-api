from fastapi.security import OAuth2PasswordBearer

from utils import WorkTokens

# Используем oauth2_scheme для зависимости, чтобы достать токен из заголовка.
# Используем также oauth2_scheme, чтобы указать в Swagger UI кнопку Authorize.

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/cosmetology/login")
work_tokens = WorkTokens()


async def get_current_access_token(token: str) -> int:
    user_id = work_tokens.check_access_token(access_token=token)
    return user_id
