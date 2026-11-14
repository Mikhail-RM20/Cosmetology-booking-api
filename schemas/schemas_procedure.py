from pydantic import BaseModel, Field


class ProcedureOut(BaseModel):
    """
    Pydantic модель для вывода данных косметологической процедуры.

    Attributes:
        id: int - ID процедуры.
        name: str - Название процедуры.
        description: str - Описание процедуры.
        price: int - Цена процедуры.


    """

    id: int = Field(
        ...,
        title="ID - процедуры.",
    )
    name: str = Field(
        ...,
        title="Название процедуры.",
    )
    description: str = Field(
        ...,
        title="Описание процедуры.",
    )
    price: int = Field(
        ...,
        title="Цена процедуры.",
    )
