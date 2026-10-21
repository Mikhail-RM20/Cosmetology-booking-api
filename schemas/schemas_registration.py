from pydantic import BaseModel, Field, field_validator


class RegistrationIn(BaseModel):
    name: str = Field(
        ...,
        title="Имя человека.",
        min_length=2,
        examples=["Сергей", "Мария"],
    )
    surname: str = Field(
        ...,
        title="Фамилия человека.",
        min_length=2,
        examples=["Петров", "Петрова"],
    )
    phone: str = Field(
        ...,
        title="Номер телефона человека.",
        pattern=r"^(?:\+7|8)\d{10}$",
    )
    password: str = Field(
        ...,
        title="Пароль для регистрации и последующей аутентификации.",
        min_length=8,
    )
    email: str = Field(
        ...,
        title="Email пользователя при регистрации.",
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        # 1. Email вообще передан?
        if not value:
            raise ValueError("Email обязателен")

        # 2. Есть ли собачка?
        if "@" not in value:
            raise ValueError("Email должен содержать символ @")

        # 3. Собачка должна быть одна
        if value.count("@") != 1:
            raise ValueError("Email должен содержать только один символ @")

        # 4. Разделяем на логин и домен
        username, domain = value.split("@")

        # 5. Логин не должен быть пустым
        if not username:
            raise ValueError("Укажите имя пользователя перед @")

        # 6. Домен должен быть mail.ru
        if domain.lower() != "mail.ru":
            raise ValueError("Разрешена только почта @mail.ru")

        return value.lower()

class RegistrationOut(BaseModel):
    message: str = Field(
        ...,
        title="Сообщение о регистрации.",
    )
    id_user: int = Field(
        ...,
        title="ID - пользователя."
    )