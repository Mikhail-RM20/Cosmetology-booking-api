import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database import User, TokenUser
from core import hash_password
from utils import WorkTokens


@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    person = User(
        name="Клиент",
        surname="Тестовый",
        phone="+79161234567",
        role="user",
        hash_password=hash_password("test_password_1"),
        email="test_email@mail.ru",
    )

    db_session.add(person)
    await db_session.commit()

    assert person.id is not None
    assert person.name == "Клиент"
    assert person.phone == "+79161234567"


@pytest.mark.asyncio
async def test_generate_tokens(db_session: AsyncSession):
    person = User(
        name="Клиент",
        surname="Тестовый",
        phone="+79161234567",
        role="user",
        hash_password=hash_password("test_password_1"),
        email="test_email@mail.ru",
    )

    db_session.add(person)
    await db_session.commit()

    work_tokens = WorkTokens()

    access, refresh = await work_tokens.pair_generation_access_refresh(
        db=db_session,
        id_user=person.id,
    )

    assert isinstance(access, str)
    assert isinstance(refresh, str)
    assert access
    assert refresh

    result = await db_session.execute(
        select(TokenUser).where(TokenUser.user_id == person.id)
    )
    token_row = result.scalar_one()

    assert token_row.is_working is True
    assert token_row.token_hash


@pytest.mark.asyncio
async def test_old_refresh_tokens_disabled(db_session: AsyncSession):
    person = User(
        name="Клиент",
        surname="Тестовый",
        phone="+79161234567",
        role="user",
        hash_password=hash_password("test_password_1"),
        email="test_email@mail.ru",
    )

    db_session.add(person)
    await db_session.commit()

    work_tokens = WorkTokens()

    await work_tokens.pair_generation_access_refresh(
        db=db_session,
        id_user=person.id,
    )
    await work_tokens.pair_generation_access_refresh(
        db=db_session,
        id_user=person.id,
    )

    result = await db_session.execute(
        select(TokenUser).where(TokenUser.user_id == person.id)
    )
    tokens = result.scalars().all()

    assert len(tokens) == 2
    assert tokens[0].is_working is False
    assert tokens[1].is_working is True


@pytest.mark.asyncio
async def test_user_without_required_fields_fails(db_session: AsyncSession):
    person = User(
        name="Клиент",
        surname="Тестовый",
        role="user",
        hash_password=hash_password("test_password_1"),
    )

    db_session.add(person)

    with pytest.raises(IntegrityError):
        await db_session.commit()

    await db_session.rollback()