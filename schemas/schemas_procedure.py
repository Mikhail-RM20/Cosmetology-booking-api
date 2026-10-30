from pydantic import BaseModel, Field

class ProcedureOut(BaseModel):
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