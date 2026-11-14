# Aesthetic Clinic — Система онлайн-записи в косметологическую клинику

Веб-приложение и REST API для автоматизации онлайн-записи клиентов в косметологическую клинику, реализованное на Python 3.13 с использованием FastAPI, SQLAlchemy (async), PostgreSQL, Redis, Nginx и Docker. Приложение предоставляет адаптивный веб-интерфейс (SPA на Vanilla JS) с разделением ролей для клиентов и администратора, а также документированный HTTP API.

---

## Принятые архитектурные решения

* **JWT-аутентификация с ротацией Refresh-токенов**: access-токен живёт 15 минут, а refresh-токен хранится в PostgreSQL исключительно в виде SHA-256 хеша. При обновлении пары (`/cosmetology/rotation`) старый refresh-токен немедленно деактивируется (`is_working = False`), а фронтенд автоматически перехватывает `401 Unauthorized` и прозрачно обновляет сессию пользователя без повторного входа.
* **Защита от двойного бронирования (Race Condition)**: на уровне базы данных установлено составное уникальное ограничение `UniqueConstraint("entry_date", "entry_time")` с обработкой `IntegrityError`. Даже при одновременной отправке двух запросов на одно время система гарантирует создание только одной записи.
* **Кэширование справочников через Redis с отказоустойчивым фоллбэком**: список категорий и процедур кэшируется в Redis (TTL 300 секунд). При временной недоступности кэш-сервера приложение перехватывает `RedisError` и автоматически переключается на чтение из PostgreSQL без потери работоспособности.
* **Reverse Proxy и единая точка входа через Nginx**: наружу открыт только 80-й порт контейнера Nginx, который отдаёт статику фронтенда и проксирует API-запросы (`/cosmetology/*`, `/docs`) во внутреннюю изолированную сеть Docker на Uvicorn. База данных и Redis полностью закрыты от внешнего доступа.
* **Безопасность персональных данных**: пароли хешируются с помощью современного алгоритма **Argon2** (`pwdlib`), а номера телефонов клиентов маскируются в файлах логов (`RotatingFileHandler`).

---

## ПРЕДВАРИТЕЛЬНЫЕ ТРЕБОВАНИЯ ДЛЯ ЗАПУСКА ПРОЕКТА

* Установленные **Docker** и **Docker Compose**.
* **Python 3.13+** (при локальном запуске без Docker).

В проекте используются **Ruff** (линтер и форматер) и **Mypy** (статический анализатор типов). Настройки находятся в `pyproject.toml`.

* Проверка кода на ошибки и стиль: `ruff check .`
* Автоматическое исправление ошибок: `ruff check --fix .`
* Сортировка импортов: `ruff check --fix --select I .`
* Форматирование кода: `ruff format .`
* Проверка типов: `mypy .`
* Полный цикл: `ruff check --fix . && ruff format . && mypy .`

**ПРИМЕЧАНИЕ:** Проверка длины строк в Ruff отключена в конфигурации (`E501`, `W505` игнорируются).

---

## ИНСТРУКЦИЯ К ЗАПУСКУ

### ВНИМАНИЕ: `.env` файл
**Файл `.env` не хранится в репозитории — в проекте приложен шаблон `.env.example`.**

1. Создайте файл `.env` в корне проекта на основе `.env.example`:
   ```bash
   cp .env.example .env
   ```
   Пример содержимого `.env` для запуска в Docker:
   ```env
   # Postgres
   POSTGRES_USER=Ваш логин
   POSTGRES_PASSWORD=Ваш пароль
   POSTGRES_DB=Ваша БД
   POSTGRES_HOST=postgres
   POSTGRES_PORT=5432

   # Redis
   REDIS_HOST=redis
   REDIS_PORT=6379
   REDIS_DB=0

   # JWT (сгенерируйте свой ключ командой: python -c "import secrets; print(secrets.token_hex(32))")
   SECRET_KEY=replace_with_generated_secret_key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=15
   REFRESH_TOKEN_EXPIRE_DAYS=30

   # Данные администратора
   ADMIN_NAME=Имя администратора
   ADMIN_SURNAME=Фамилия Администратора
   ADMIN_PHONE=Номер телеофна
   ADMIN_EMAIL=Почта
   ADMIN_PASSWORD=Парольь
   ADMIN_ROLE=admin
   ```

2. Запустите контейнеры:
   ```bash
   docker compose up -d --build
   ```
   При первом запуске контейнер `migrations` автоматически дождётся готовности PostgreSQL, применит миграции Alembic и заполнит базу базовыми категориями, процедурами и учётной записью администратора (`seed_data.py`).

3. После успешного запуска сервисы будут доступны по адресам:
   * **Веб-интерфейс клиники:** http://localhost
   * **Интерактивная документация Swagger UI:** http://localhost/docs

4. Остановка контейнеров:
   ```bash
   docker compose down
   ```
   *(Для полного сброса базы данных, кэша Redis и повторной загрузки стартовых данных: `docker compose down -v && docker compose up -d --build`)*

---

## Функциональные возможности

| № | Описание | Метод и URL | Доступ |
|---|----------|-------------|--------|
| 1 | Регистрация нового клиента | `POST /cosmetology/registration` | Публичный |
| 2 | Аутентификация и получение пары JWT-токенов | `POST /cosmetology/login` | Публичный |
| 3 | Ротация пары access и refresh токенов | `POST /cosmetology/rotation` | По Refresh-токену |
| 4 | Получение профиля и роли текущего пользователя | `GET /cosmetology/me` | Авторизованный |
| 5 | Получение списка категорий с вложенными процедурами | `GET /cosmetology/categories` | Авторизованный |
| 6 | Получение списка процедур (с фильтром по категории) | `GET /cosmetology/procedures` | Авторизованный |
| 7 | Создание новой записи на процедуру | `POST /cosmetology/new_entry` | Авторизованный |
| 8 | Просмотр активных записей текущего клиента | `GET /cosmetology/my_entries` | Авторизованный |
| 9 | Отмена собственной записи клиентом | `DELETE /cosmetology/my_entries/{entry_id}` | Авторизованный |
| 10 | Просмотр всех записей клиники (с фильтром по дате) | `GET /cosmetology/get_entries` | Администратор |
| 11 | Удаление любой записи из расписания | `DELETE /cosmetology/delete_entries/{id_entry}` | Администратор |

---

## Технологический стек

| № | Компонент | Технология |
|---|-----------|------------|
| 1 | Язык | Python 3.13 |
| 2 | Веб-фреймворк | FastAPI |
| 3 | ORM и миграции | SQLAlchemy 2.0 (async), Alembic |
| 4 | База данных | PostgreSQL 16 + asyncpg |
| 5 | Кэширование | Redis 7 |
| 6 | Безопасность | PyJWT, Argon2 (`pwdlib`) |
| 7 | Веб-сервер и прокси | Nginx, Uvicorn |
| 8 | Фронтенд | HTML5, CSS3, Vanilla JavaScript (SPA) |
| 9 | Контейнеризация | Docker, Docker Compose |
| 10 | Валидация и качество кода | Pydantic v2, Ruff, Mypy |

---

## Структура проекта

```text
├── alembic/                                # Миграции базы данных Alembic
│   ├── versions/                           # Файлы ревизий схемы БД
│   └── env.py                              # Конфигурация окружения Alembic
├── core/                                   # Конфигурация, логирование, Redis и безопасность
│   ├── __init__.py
│   ├── config.py                           # ConfigSetting (Pydantic BaseSettings)
│   ├── logger.py                           # Конфигурация RotatingFileHandler
│   ├── redis_config.py                     # Асинхронный клиент Redis
│   └── security_password.py                # Хеширование и проверка паролей (Argon2)
├── database/                               # Подключение к БД и ORM-модели
│   ├── __init__.py
│   ├── base.py                             # AsyncEngine, Base, SessionLocal, get_db
│   └── models.py                           # Модели User, Category, Procedures, TokenUser, EntryCosmetology
├── dependencies/                           # Зависимости FastAPI (проверка токенов и ролей)
│   ├── __init__.py
│   ├── authorization.py                    # OAuth2PasswordBearer и проверка access-токена
│   └── role_person.py                      # Проверка прав администратора
├── frontend/                               # Клиентское SPA-приложение
│   ├── index.html                          # Разметка кабинета клиента, админ-панели и модальных окон
│   ├── style.css                           # Адаптивные стили интерфейса
│   └── app.js                              # Логика работы с API, авто-ротация JWT и роутинг по ролям
├── nginx/                                  # Конфигурация Reverse Proxy
│   └── nginx.conf                          # Раздача статики фронтенда и проксирование на FastAPI
├── routes/                                 # Роутеры FastAPI (HTTP-слой)
│   ├── __init__.py
│   ├── route_registration.py               # POST /cosmetology/registration
│   ├── route_login.py                      # POST /cosmetology/login
│   ├── route_rotation.py                   # POST /cosmetology/rotation
│   ├── route_me.py                         # GET /cosmetology/me
│   ├── route_get_categories.py             # GET /cosmetology/categories
│   ├── route_get_procedures.py             # GET /cosmetology/procedures
│   ├── route_new_entry.py                  # POST /cosmetology/new_entry
│   ├── route_my_entries.py                 # GET и DELETE /cosmetology/my_entries
│   ├── route_get_all_entry.py              # GET /cosmetology/get_entries
│   └── route_delete_entries.py             # DELETE /cosmetology/delete_entries/{id_entry}
├── schemas/                                # Pydantic-схемы валидации запросов и ответов
│   ├── __init__.py
│   ├── schemas_category.py                 # CategoryOut
│   ├── schemas_entry.py                    # EntryIn, EntryOut, Entries, MyEntryOut
│   ├── schemas_login.py                    # LogIn, LogOut
│   ├── schemas_procedure.py                # ProcedureOut
│   ├── schemas_registration.py             # RegistrationIn, RegistrationOut
│   ├── schemas_user.py                     # UserOut
│   └── shemas_token.py                     # TokenRefreshIn
├── src/                                    # Бизнес-логика операций и транзакций
│   ├── __init__.py
│   ├── function_registration.py            # Регистрация пользователя
│   ├── function_login.py                   # Проверка учётных данных при входе
│   ├── function_check_user_db.py           # Поиск пользователя в БД
│   ├── function_get_me.py                  # Получение профиля пользователя
│   ├── function_get_procedure.py           # Получение категорий и процедур с кэшем Redis
│   ├── function_create_entry.py            # Создание записи с проверкой слота
│   ├── function_my_entries.py              # Просмотр и отмена записей клиентом
│   ├── function_get_all_entries.py         # Выборка всех записей для администратора
│   └── function_delete_entries.py          # Удаление записи администратором
├── utils/                                  # Вспомогательные утилиты
│   ├── __init__.py
│   ├── utils_tokens.py                     # Генерация, валидация и ротация JWT (WorkTokens)
│   └── mask_phone.py                       # Маскирование номеров телефонов в логах
├── alembic.ini                             # Настройки Alembic
├── docker-compose.yml                      # Оркестрация контейнеров (postgres, redis, migrations, api, nginx)
├── Dockerfile                              # Сборка образа Python 3.13
├── main.py                                 # Точка входа FastAPI
├── pyproject.toml                          # Настройки Ruff и Mypy
├── requirements.txt                        # Зависимости Python
├── seed_data.py                            # Скрипт начального наполнения БД
├── .env.example                            # Шаблон переменных окружения
└── README.md
```
---

## Проверка пользовательских сценариев

```text
После запуска проекта на http://localhost можно проверить все основные сценарии:
1. Регистрация и вход клиента:
	• На стартовом экране перейти во вкладку «Регистрация», заполнить имя, фамилию, номер телефона (в формате +79991234567), email и пароль (от 8 символов), затем войти в личный кабинет.
2. Фильтрация услуг и онлайн-запись:
	• Во вкладке «Услуги и запись» отфильтровать процедуры по категориям (Чистка лица, Пилинг, Инъекционные процедуры и др.), выбрать процедуру, дату (в пределах 30 дней) и свободное время.
	• При попытке записаться на уже занятое время в выбранную дату система заблокирует создание дубля и выведет уведомление об ошибке.
3. Личный кабинет и отмена визита:
	• Во вкладке «Мой профиль» отображаются контактные данные клиента, номер карты и счетчик активных записей.
	• Во вкладке «Мои записи» клиент может просмотреть предстоящие визиты и отменить любую запись.
4. Панель администратора (врача):
	• Выйдите из аккаунта клиента и войдите под учетной записью администратора из .env (+79000000000 / secket_key_1990).
	• Откроется панель управления со всеми записями клиники, возможностью фильтрации расписания по конкретной дате и удаления записей.
```
---
## Описание эндпоинтов


1. POST /cosmetology/registration

• Что делает: Регистрирует нового пользователя с ролью user, хеширует пароль с помощью Argon2 и проверяет уникальность номера телефона.
• Тело запроса (JSON): name (str), surname (str), phone (str, формат ^\+7|8\d{10}$), email (EmailStr), password (str, от 8 символов).
• Ответ: 201 Created (RegistrationOut).
• Возможные ошибки: 400 (телефон уже зарегистрирован), 422 (ошибка валидации полей), 500 (ошибка БД).

2. POST /cosmetology/login

• Что делает: Проверяет телефон и пароль пользователя, деактивирует предыдущие токены обновления и выдает новую пару JWT (access_token, refresh_token).
• Тело запроса (JSON): phone (str), password (str).
• Ответ: 201 Created (LogOut).
• Возможные ошибки: 401 (неверный телефон или пароль), 500 (ошибка БД).

3. POST /cosmetology/rotation

• Что делает: Проверяет действительность и активность refresh_token в базе данных, отзывает его (is_working = False) и генерирует новую пару токенов.
• Тело (JSON): refresh_token (str).
• Ответ: 201 Created (LogOut).
• Возможные ошибки: 401 (токен просрочен, поврежден или уже использован).

4. GET /cosmetology/me

• Что делает: Возвращает профиль текущего авторизованного пользователя (id, name, surname, phone, email, role).
• Заголовки: Authorization: Bearer <access_token>.
• Ответ: 200 OK (UserOut).
• Возможные ошибки: 401 (недействительный или просроченный токен доступа), 404 (пользователь не найден).

5. GET /cosmetology/categories

• Что делает: Возвращает список всех категорий косметологических услуг вместе со списком процедур внутри каждой категории (с кэшированием в Redis).
• Заголовки: Authorization: Bearer <access_token>.
• Ответ: 200 OK (list[CategoryOut]).

6. GET /cosmetology/procedures

• Что делает: Возвращает список процедур с возможностью фильтрации по category_id (с кэшированием в Redis).
• Headers: Authorization: Bearer <access_token>.
• Query Params: category_id (int, опционально).
• Ответ: 200 OK (list[ProcedureOut]).

7. POST /cosmetology/new_entry

• Что делает: Создаёт новую запись клиента на выбранную процедуру, дату и время с проверкой занятости слота.
• Headers: Authorization: Bearer <access_token>.
• Body (JSON): procedure_id (int), entry_date (date), entry_time (time).
• Ответ: 201 Created (EntryOut).
• Возможные ошибки: 400 (выбранное время уже занято или дата некорректна), 404 (процедура не найдена).

8. GET /cosmetology/my_entries

• Что делает: Возвращает список всех предстоящих записей текущего авторизованного клиента.
• Headers: Authorization: Bearer <access_token>.
• Ответ: 200 OK (list[MyEntryOut]).

9. DELETE /cosmetology/my_entries/{entry_id}

• Что делает: Отменяет (удаляет) запись, принадлежащую текущему клиенту.
• Headers: Authorization: Bearer <access_token>.
• Path Params: entry_id (int).
• Ответ: 204 No Content.
• Возможные ошибки: 404 (запись не найдена или принадлежит другому пользователю).

10. GET /cosmetology/get_entries

• Что делает: Возвращает список всех записей клиники с данными клиентов и процедур. Доступно только администратору.
• Headers: Authorization: Bearer <access_token>.
• Query Params: date (datetime, опционально — фильтрация по дате).
• Ответ: 200 OK (list[Entries]).
• Возможные ошибки: 401 (нет прав администратора).

11. DELETE /cosmetology/delete_entries/{id_entry}

• Что делает: Удаляет любую запись из расписания клиники. Доступно только администратору.
• Headers: Authorization: Bearer <access_token>.
• Path Params: id_entry (int).
• Ответ: 200 OK (Entries).
• Возможные ошибки: 401 (нет прав администратора), 404 (запись не найдена).

---

### 2. Файл `.env.example` (положи в корень проекта)

```env
# Postgres
POSTGRES_USER=beauty_Ivan
POSTGRES_PASSWORD=changeme_password
POSTGRES_DB=cosmetology_database
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# JWT
SECRET_KEY=replace_with_your_own_secret_key_hex
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=30

# Данные администратора
ADMIN_NAME=Имя
ADMIN_SURNAME=Фамилия
ADMIN_PHONE=Номер телефона
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=changeme_admin_password
ADMIN_ROLE=admin
```
---