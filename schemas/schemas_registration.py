from pydantic import BaseModel, EmailStr, Field, field_validator


class RegistrationIn(BaseModel):
    """
    Pydantic модель для регистрации нового пользователя.

    Attributes:
        name: str - Имя пользователя.
            Минимальная длина - 2 символа.
        surname: str - Фамилия пользователя.
            Минимальная длина - 2 символа.
        phone: str - Номер телефона пользователя.
            Должен начинаться с +7 или 8 и содержать 10 цифр после него.
        password: str - Пароль для регистрации
            и последующей аутентификации.
            Минимальная длина пароля - 8 символов.
        email: str - Email пользователя при регистрации.
            Разрешена только почта @mail.ru.

    Validators:
        validate_email: Проверяет корректность email
            и разрешенный домен почты.


    """

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
    email: EmailStr = Field(
        ...,
        title="Email пользователя при регистрации.",
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        """
        Проверяет корректность email пользователя.

        Args:
            value: str - Email пользователя.

        Returns:
            str - Валидный email в нижнем регистре.

        Raises:
            ValueError - Если email не указан.
            ValueError - Если email не содержит символ @.
            ValueError - Если символ @ встречается более одного раза.
            ValueError - Если не указано имя пользователя перед @.
            ValueError - Если домен почты не @mail.ru.
        """
        if not value:
            raise ValueError("Email обязателен")

        if "@" not in value:
            raise ValueError("Email должен содержать символ @")

        if value.count("@") != 1:
            raise ValueError("Email должен содержать только один символ @")

        username, domain = value.split("@")

        if not username:
            raise ValueError("Укажите имя пользователя перед @")

        if domain.lower() != "mail.ru":
            raise ValueError("Разрешена только почта @mail.ru")

        return value.lower()


class RegistrationOut(BaseModel):
    """
    Pydantic модель для вывода результата регистрации пользователя.

    Attributes:
        message: str - Сообщение о регистрации.
        id_user: int - ID созданного пользователя.

    """

    message: str = Field(
        ...,
        title="Сообщение о регистрации.",
    )
    id_user: int = Field(..., title="ID - пользователя.")
