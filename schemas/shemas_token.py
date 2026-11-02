from pydantic import BaseModel, Field


class TokenRefreshIn(BaseModel):
    refresh_token: str = Field(..., title="Refresh - токен.")
