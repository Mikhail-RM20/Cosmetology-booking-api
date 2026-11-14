from typing import Literal

from pydantic import BaseModel, Field


class LogIn(BaseModel):
    """
    Pydantic модель для входа пользователя в систему.

    Attributes:
        phone: str - Номер телефона пользователя.
            Должен начинаться с +7 или 8 и содержать 10 цифр после него.
        password: str - Пароль пользователя.
            Минимальная длина пароля - 8 символов.

    Подробнее: /schemas/schemas_login.py
    """

    phone: str = Field(
        ...,
        title="Номер телефона человека.",
        pattern=r"^(?:\+7|8)\d{10}$",
    )
    password: str = Field(
        ...,
        title="Пароль человека.",
        min_length=8,
    )


class LogOut(BaseModel):
    """
    Pydantic модель для вывода токенов после аутентификации пользователя.

    Attributes:
        access_token: str - Access-токен пользователя.
        refresh_token: str - Refresh-токен пользователя.
        token_type: Literal["bearer"] - Тип токена.
            По умолчанию используется значение "bearer".


    """

    access_token: str = Field(
        ...,
        title="Access - токен.",
    )
    refresh_token: str = Field(
        ...,
        title="Refresh - токен.",
    )
    token_type: Literal["bearer"] = Field(
        default="bearer",
        title="Тип токена",
    )
