import hashlib
from datetime import UTC, datetime, timedelta

import jwt
from core import config_set
from database import TokenUser
from fastapi import HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# Класс, для работы с токенами.
# Метод 1: создает пару access и refresh токенов.
# Метод 2: выдает access-токен, по refresh - токену.
# Метод 3: проводит ротацию refresh - токена.
# Метод 4: проверяет access - токен для работы с роутами.


class WorkTokens:
    """
    Класс для работы с access и refresh токенами пользователя.

    Отвечает за:
        - Генерацию пары access и refresh токенов.
        - Проверку access токена.
        - Обновление токенов через refresh токен.
        - Сохранение хеша активного refresh токена в базе данных.

    Attributes:
        secret_key: str - Секретный ключ для подписи токенов.
        algorithm: str - Алгоритм подписи JWT.
        access_token_expire_minutes: int - Время жизни access токена в минутах.
        refresh_token_expire_days: int - Время жизни refresh токена в днях.

    Methods:
        pair_generation_access_refresh: Создает новую пару токенов.
        check_access_token: Проверяет access токен и возвращает id пользователя.
        rotation_tokens: Обновляет пару токенов по refresh токену.

    Подробнее: /utils/utils_tokens.py
    """

    def __init__(self):
        """
        Инициализирует настройки для работы с токенами.

        Attributes:
            secret_key: str - Секретный ключ из Pydantic-settings.
            algorithm: str - Алгоритм подписи JWT.
            access_token_expire_minutes: int - Время жизни access токена.
            refresh_token_expire_days: int - Время жизни refresh токена.
        """
        # Берем данные из Pydantic-settings

        self.secret_key = config_set.secret_key
        self.algorithm = config_set.algorithm
        self.access_token_expire_minutes = (
            config_set.access_token_expire_minutes
        )
        self.refresh_token_expire_days = config_set.refresh_token_expire_days

    async def pair_generation_access_refresh(
        self, db: AsyncSession, id_user: int
    ) -> tuple[str, str]:
        """
        Создает новую пару access и refresh токенов для пользователя.

        Деактивирует все ранее активные refresh токены пользователя,
        создает новый активный refresh токен и сохраняет его хеш в БД.

        Args:
            db: AsyncSession - Асинхронная сессия базы данных.
            id_user: int - ID пользователя, для которого создаются токены.

        Returns:
            tuple[str, str] - Пара токенов пользователя:
                access_token: str - Access-токен пользователя.
                refresh_token: str - Refresh-токен пользователя.

        Raises:
            HTTPException 500 - Некорректный секретный ключ.
            HTTPException 500 - Неподдерживаемый алгоритм подписи.
            HTTPException 500 - Отсутствует необходимая библиотека cryptography.
        """

        # "sub" - subject, сохраняет id - пользователя.
        # "iat" - issued at, время создания токена.
        # "exp" - expiration time, время окончания действия токена.
        # "type" - тип токена.
        # "now" - текущее время.

        try:
            now = datetime.now(UTC)

            access = {
                "sub": str(id_user),
                "iat": now,
                "exp": now
                + timedelta(minutes=self.access_token_expire_minutes),
                "type": "access",
            }

            refresh = {
                "sub": str(id_user),
                "iat": now,
                "exp": now + timedelta(days=self.refresh_token_expire_days),
                "type": "refresh",
            }

            # Подписываем access и refresh, по секретному ключу и алгоритму.

            access_token = jwt.encode(
                access, self.secret_key, algorithm=self.algorithm
            )
            refresh_token = jwt.encode(
                refresh, self.secret_key, algorithm=self.algorithm
            )

            # Хешируем refresh, чтобы добавить его в БД.
            refresh_token_hash = hashlib.sha256(
                refresh_token.encode("utf-8")
            ).hexdigest()

            await db.execute(
                update(TokenUser)
                .where(
                    TokenUser.user_id == id_user,
                    TokenUser.is_working.is_(True),
                )
                .values(is_working=False)
            )

            db.add(
                TokenUser(
                    user_id=id_user,
                    token_hash=refresh_token_hash,
                    expires_at=now
                    + timedelta(days=self.refresh_token_expire_days),
                    is_working=True,
                )
            )

            await db.commit()

            return access_token, refresh_token

        except jwt.exceptions.InvalidKeyError as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Секретный ключ неправильного формата или не подходит для алгоритма.",
            ) from error

        except jwt.exceptions.InvalidAlgorithmError as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Указан неизвестный или неподдерживаемый алгоритм.",
            ) from error

        except NotImplementedError as error:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Алгоритм требует пакет <cryptography>, но он не установлен.",
            ) from error

    def check_access_token(self, access_token: str) -> int:
        """
        Проверяет access токен пользователя.

        Проверяет подпись, срок действия, тип токена и наличие id пользователя.

        Args:
            access_token: str - Access-токен пользователя.

        Returns:
            int - ID пользователя из access токена.

        Raises:
            HTTPException 401 - Неверный тип токена.
            HTTPException 401 - В токене отсутствует id пользователя.
            HTTPException 401 - Access токен истек.
            HTTPException 401 - Подпись токена недействительна.
            HTTPException 401 - Токен поврежден.
            HTTPException 401 - Использован недопустимый алгоритм.
        """
        try:
            payload = jwt.decode(
                access_token, self.secret_key, algorithms=[self.algorithm]
            )

            # Проверяем тип токена. Должен быть access.
            if payload.get("type") != "access":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверный тип токена.",
                )
            # Проверяем, привязан ли ID. Должен быть привязан.
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Невалидный access token.",
                )
            return int(user_id)

        except jwt.ExpiredSignatureError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access - токен истек.",
            ) from error

        except jwt.InvalidSignatureError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен подделан или подписан другим секретом.",
            ) from error

        except jwt.DecodeError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access - токен поврежден.",
            ) from error

        except jwt.InvalidAlgorithmError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="В access - токене обнаружен недопустимый алгоритм.",
            ) from error

    async def rotation_tokens(
        self, db: AsyncSession, refresh_token: str
    ) -> tuple[str, str]:
        """
        Обновляет access и refresh токены пользователя.

        Проверяет действительность старого refresh токена, деактивирует его
        и создает новую пару access и refresh токенов. Новый refresh токен
        сохраняет срок действия старого.

        Args:
            db: AsyncSession - Асинхронная сессия базы данных.
            refresh_token: str - Действующий refresh токен пользователя.

        Returns:
            tuple[str, str] - Новая пара токенов пользователя:
                access_token: str - Новый access-токен пользователя.
                refresh_token: str - Новый refresh-токен пользователя.

        Raises:
            HTTPException 401 - Refresh токен недействителен или истёк.
            HTTPException 401 - Неверный тип токена.
            HTTPException 401 - В токене отсутствует id пользователя.
            HTTPException 401 - Подпись токена недействительна.
            HTTPException 401 - Токен поврежден.
            HTTPException 401 - Использован недопустимый алгоритм.
        """
        try:
            now = datetime.now(UTC)

            # Хешируем старый токен, чтобы сравнить его с токкеном из БД.
            old_token_hash = hashlib.sha256(
                refresh_token.encode("utf-8")
            ).hexdigest()

            # Получаем старый refresh-токен.
            result = await db.execute(
                select(TokenUser).where(
                    TokenUser.token_hash == old_token_hash,
                    TokenUser.is_working == True,
                    TokenUser.expires_at > now,
                )
            )
            old_token = result.scalar_one_or_none()

            if old_token is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Refresh-токен недействителен или истёк.",
                )

            payload = jwt.decode(
                refresh_token, self.secret_key, algorithms=[self.algorithm]
            )
            if payload.get("type") != "refresh":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Неверный тип токена.",
                )
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Невалидный refresh токен.",
                )

            access = {
                "sub": str(user_id),
                "iat": now,
                "exp": now
                + timedelta(minutes=self.access_token_expire_minutes),
                "type": "access",
            }
            refresh = {
                "sub": str(user_id),
                "iat": now,
                "exp": old_token.expires_at,
                "type": "refresh",
            }

            access_token = jwt.encode(
                access, self.secret_key, algorithm=self.algorithm
            )
            refresh_token = jwt.encode(
                refresh, self.secret_key, algorithm=self.algorithm
            )

            refresh_token_hash = hashlib.sha256(
                refresh_token.encode("utf-8")
            ).hexdigest()

            old_token.is_working = False

            db.add(
                TokenUser(
                    user_id=old_token.user_id,
                    token_hash=refresh_token_hash,
                    expires_at=old_token.expires_at,
                    is_working=True,
                )
            )

            await db.commit()

            return access_token, refresh_token

        except jwt.ExpiredSignatureError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access - токен истек.",
            ) from error

        except jwt.InvalidSignatureError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен подделан или подписан другим секретом.",
            ) from error

        except jwt.DecodeError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access - токен поврежден.",
            ) from error

        except jwt.InvalidAlgorithmError as error:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="В access - токене обнаружен недопустимый алгоритм.",
            ) from error
