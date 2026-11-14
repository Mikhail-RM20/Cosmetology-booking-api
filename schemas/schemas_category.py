from pydantic import BaseModel, Field

from .schemas_procedure import ProcedureOut


class CategoryOut(BaseModel):
    """
    Pydantic модель для вывода данных категории.

    Attributes:
        id: int - ID категории.
        name: str - Название категории.
        procedures: list[ProcedureOut] - Список процедур,
            относящихся к категории.
    """

    id: int = Field(..., title="ID - категории.")
    name: str = Field(..., title="Название категории.")
    procedures: list[ProcedureOut] = Field(
        default_factory=list,
        title="Процедуры категории.",
    )
