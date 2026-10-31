from pwdlib import PasswordHash

# Используем современный рекомендуемый алгоритм Argon2.
password_hash = PasswordHash.recommended()


# Функция хеширования при регистрации.
def hash_password(password: str) -> str:
    return password_hash.hash(password)


# Функция проверки хешированного пароля.
def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)
