from pydantic import BaseModel, Field

from schemas import ProcedureOut


class CategoryOut(BaseModel):
    id: int = Field(..., title="ID - категории.")
    name: str = Field(..., title="Название категории.")
    procedures: list[ProcedureOut] = Field(
        default_factory=list,
        title="Процедуры категории.",
    )
