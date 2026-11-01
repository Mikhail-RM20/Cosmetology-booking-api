from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigSetting(BaseSettings):
    # Настройка чтения .env-файла.
    # BaseSettings - класс, который сам может находить значения для переменных окружения.
    # SettingConfigDict - класс, который говорит BaseSettings, где искать и как обрабатывать переменные окружения.

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Переменные окружения для работы с СУБД Postgres.
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_host: str
    postgres_port: int

    # Переменные окружения для работы с Redis.
    redis_host: str
    redis_port: int
    redis_db: int

    # Переменные окружения для работы с JWT-токенами
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int

    # Переменные окружения данных админа.
    admin_name: str
    admin_surname: str
    admin_phone: str
    admin_email: str | None = None
    admin_password: str
    admin_role: str

    # Используем декоратор property, позволяющий обращаться к функции как к полю.
    # Возвращаем строку подключения к БД.
    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}"
            f":{self.postgres_password}@{self.postgres_host}:{self.postgres_port}"
            f"/{self.postgres_db}"
        )

    @property
    def database_url_sync(self) -> str:
        return (
            f"postgresql://{self.postgres_user}"
            f":{self.postgres_password}@{self.postgres_host}:{self.postgres_port}"
            f"/{self.postgres_db}"
        )


# Используем декоратор lru_cache, для кеширования, создания настройки.
# Возвращает объект настройки.
@lru_cache
def get_config() -> ConfigSetting:
    return ConfigSetting()  # type: ignore[call-arg]


config_set = get_config()
