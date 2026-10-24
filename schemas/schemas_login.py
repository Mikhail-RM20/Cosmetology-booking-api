from pydantic import BaseModel, Field
from typing import Literal

class LogIn(BaseModel):
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