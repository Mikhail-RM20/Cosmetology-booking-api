import pytest
import pytest_asyncio
from datetime import date, time, timedelta

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db, Category, Procedures, User
from core import hash_password
from schemas import RegistrationIn

from main import app


TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def clean_tables():
    yield

    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app, raise_app_exceptions=False)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.pop(get_db, None)


@pytest.fixture()
def sample_registration_in():
    return RegistrationIn(
        name="Клиент",
        surname="Тестовый",
        phone="+79161234567",
        password="test_password_1",
        email="test_email@mail.ru",
    )


@pytest_asyncio.fixture
async def procedure(db_session):
    category = Category(name="Косметология")
    db_session.add(category)
    await db_session.flush()

    procedure = Procedures(
        category_id=category.id,
        name_procedures="Чистка лица",
        description="Описание процедуры",
        price=1000,
    )
    db_session.add(procedure)
    await db_session.commit()

    return procedure


@pytest.fixture
def entry_data(procedure):
    return {
        "procedure_id": procedure.id,
        "entry_date": (date.today() + timedelta(days=1)).isoformat(),
        "entry_time": "12:00",
    }


@pytest_asyncio.fixture
async def admin_tokens(client, db_session):
    admin = User(
        name="Админ",
        surname="Тестовый",
        phone="+79160000001",
        role="admin",
        hash_password=hash_password("test_password_1"),
        email="admin@test.com",
    )

    db_session.add(admin)
    await db_session.commit()

    login_response = await client.post(
        "/cosmetology/login",
        json={
            "phone": admin.phone,
            "password": "test_password_1",
        },
    )

    return login_response.json()