from pydantic import BaseModel, Field, field_validator
from datetime import date, time, timedelta

ENTRY_TIMES = {
    time(10, 0),
    time(13, 0),
    time(14, 0),
    time(15, 0),
    time(16, 0),
    time(17, 0),
    time(18, 0),
    time(19, 0),
}

class EntryIn(BaseModel):
    procedure_id: int = Field(
        ...,
        title="ID - процедуры."
    )
    entry_date: date = Field(
        ...,
        title="Дата записи."
    )
    entry_time: time = Field(
        ...,
        title="Время записи."
    )

    # Создаем проверку входных данных по дате на уровне валидатора.
    @field_validator("entry_date")
    @classmethod
    def validate_booking_date(cls, v: date) -> date:
        today = date.today()
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
        if v not in ENTRY_TIMES:
            raise ValueError(
                "Время бронирования должно быть с 10:00 до 19:00."
            )
        return v


class EntryOut(BaseModel):
    message: str = Field(
        ...,
        title="Сообщение о регистрации."
    )

class Entries(EntryIn):
    """Pydantic - схема возвращающая данные о бронировании администратору по запросу."""

    id: int = Field(
        ...,
        title="ID - брони."
    )
    name_user: str = Field(
        ...,
        title="Имя человека"
    )
    surname_user: str = Field(
        ...,
        title="Фамилия человека"
    )
    price: int = Field(
        ...,
        title="Цена за процедуру."
    )