from core import config_set

# Класс, для работы с токенами.
# Метод 1: создает пару access и refresh токенов.
# Метод 2: выдает access-токен, по refresh - токену.
# Метод 3: проводит ротацию refresh - токена.
# Метод 4: проверяет access - токен для работы с роутами.

class WorkTokens():
    def __init__(self):
        # Берем данные из Pydantic-settings

        self.secret_key = config_set.secret_key
        self.algorithm = config_set.algorithm
        self.access_token_expire_minutes = config_set.access_token_expire_minutes
        self.refresh_token_expire_days = config_set.refresh_token_expire_days


    def pair_generation(self, id_user: int) -> tuple[str, str]:
        pass
