from pydantic import BaseModel, Field


class TokenRefreshIn(BaseModel):
    """
    Pydantic модель для обновления access и refresh токенов пользователя.

    Attributes:
        refresh_token: str - Refresh-токен пользователя,
            необходимый для получения новой пары токенов.


    """

    refresh_token: str = Field(..., title="Refresh - токен.")
