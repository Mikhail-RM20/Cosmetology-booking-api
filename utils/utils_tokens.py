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
    def __init__(self):
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
