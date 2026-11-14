from pydantic import BaseModel, Field


class UserOut(BaseModel):
    """
    Pydantic модель для вывода данных текущего пользователя.
    """

    id: int = Field(..., title="ID пользователя.")
    name: str = Field(..., title="Имя пользователя.")
    surname: str = Field(..., title="Фамилия пользователя.")
    phone: str = Field(..., title="Телефон пользователя.")
    email: str | None = Field(default=None, title="Email пользователя.")
    role: str = Field(..., title="Роль пользователя (user или admin).")
