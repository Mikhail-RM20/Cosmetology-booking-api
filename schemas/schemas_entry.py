from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, field_validator, model_validator

ENTRY_TIMES = {
    time(10, 0),
    time(11, 0),
    time(12, 0),
    time(13, 0),
    time(14, 0),
    time(15, 0),
    time(16, 0),
    time(17, 0),
    time(18, 0),
    time(19, 0),
}


class EntryIn(BaseModel):
    """
    Pydantic модель для создания записи на косметологическую процедуру.

    Attributes:
        procedure_id: int - ID процедуры.
        entry_date: date - Дата записи.
        entry_time: time - Время записи.

    Validators:
        validate_booking_date: Проверяет, что дата записи
            не раньше сегодняшнего дня и не позднее чем через 30 дней.
        validate_booking_time: Проверяет, что время записи
            входит в допустимый интервал с 10:00 до 19:00.
        validate_not_past_datetime: Проверяет, что выбранные дата и время
            не находятся в прошлом (при записи на сегодняшний день).

    Подробнее: /schemas/schemas_entry.py
    """

    procedure_id: int = Field(..., title="ID - процедуры.")
    entry_date: date = Field(..., title="Дата записи.")
    entry_time: time = Field(..., title="Время записи.")

    # Создаем проверку входных данных по дате на уровне валидатора.
    @field_validator("entry_date")
    @classmethod
    def validate_booking_date(cls, v: date) -> date:
        """
        Проверяет корректность даты бронирования.

        Args:
            v: date - Дата бронирования.

        Returns:
            date - Валидная дата бронирования.

        Raises:
            ValueError - Если дата раньше сегодняшнего дня
                или позднее чем через 30 дней.
        """
        today = datetime.now(ZoneInfo("Europe/Moscow")).date()
        max_date = today + timedelta(days=30)

        if v < today:
            raise ValueError(
                "Дата бронирования должна быть сегодня или позже."
            )

        if v > max_date:
            raise ValueError(
                "Дата бронирования должна быть не позднее, чем через 30 дней с сегодняшнего дня."
            )

        return v

    # Создаем проверку входных данных по времени на уровне валидатора.
    @field_validator("entry_time")
    @classmethod
    def validate_booking_time(cls, v: time) -> time:
        """
        Проверяет, что время бронирования входит в допустимый список.

        Args:
            v: time - Время бронирования.

        Returns:
            time - Валидное время бронирования.

        Raises:
            ValueError - Если время не входит в интервал с 10:00 до 19:00.
        """
        if v not in ENTRY_TIMES:
            raise ValueError(
                "Время бронирования должно быть с 10:00 до 19:00."
            )

        return v

    # Создаем проверку на то, что дата и время записи не в прошлом.
    @model_validator(mode="after")
    def validate_not_past_datetime(self) -> "EntryIn":
        """
        Проверяет, что выбранные дата и время не находятся в прошлом
        (актуально при записи на сегодняшний день).

        Returns:
            EntryIn - Валидный экземпляр модели записи.

        Raises:
            ValueError - Если время записи на сегодняшний день уже прошло.
        """
        tz = ZoneInfo("Europe/Moscow")
        now = datetime.now(tz)
        booking_dt = datetime.combine(self.entry_date, self.entry_time, tzinfo=tz)

        if booking_dt <= now:
            raise ValueError(
                "Нельзя записаться на прошедшее время. Выберите более поздний час или другую дату."
            )

        return self

class EntryOut(BaseModel):
    """
    Pydantic модель для вывода сообщения о созданной записи.

    Attributes:
        message: str - Сообщение о регистрации.


    """

    message: str = Field(..., title="Сообщение о регистрации.")


class Entries(EntryIn):
    """
    Pydantic - схема возвращающая данные о бронировании администратору по запросу.

    Attributes:
        id: int - ID брони.
        name_user: str - Имя человека.
        surname_user: str - Фамилия человека.
        name_procedures: str - Название процедуры.
        price: int - Цена за процедуру.


    """

    model_config = {"from_attributes": True}

    id: int = Field(..., title="ID - брони.")
    name_user: str = Field(..., title="Имя человека")
    surname_user: str = Field(..., title="Фамилия человека")
    name_procedures: str = Field(
        ...,
        title="Название процедуры.",
    )
    price: int = Field(..., title="Цена за процедуру.")


class MyEntryOut(BaseModel):
    """
    Pydantic модель для вывода записей текущего пользователя.
    """

    id: int = Field(..., title="ID записи.")
    procedure_id: int = Field(..., title="ID процедуры.")
    name_procedures: str = Field(..., title="Название процедуры.")
    price: int = Field(..., title="Цена процедуры.")
    entry_date: date = Field(..., title="Дата записи.")
    entry_time: time = Field(..., title="Время записи.")
