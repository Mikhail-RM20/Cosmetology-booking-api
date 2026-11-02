import pytest
from httpx import AsyncClient
from sqlalchemy import select

from database import EntryCosmetology
from schemas import LogIn


@pytest.mark.asyncio
async def test_registration_success(client: AsyncClient, sample_registration_in):
    response = await client.post(
        "/cosmetology/registration",
        json=sample_registration_in.model_dump(mode="json"),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id_user"] > 0
    assert data["message"]


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, sample_registration_in):
    await client.post(
        "/cosmetology/registration",
        json=sample_registration_in.model_dump(mode="json"),
    )

    login_data = LogIn(
        phone=sample_registration_in.phone,
        password=sample_registration_in.password,
    )

    response = await client.post(
        "/cosmetology/login",
        json=login_data.model_dump(mode="json"),
    )

    assert response.status_code == 201

    data = response.json()

    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_rotation_success(client: AsyncClient, sample_registration_in):
    await client.post(
        "/cosmetology/registration",
        json=sample_registration_in.model_dump(mode="json"),
    )

    login_response = await client.post(
        "/cosmetology/login",
        json={
            "phone": sample_registration_in.phone,
            "password": sample_registration_in.password,
        },
    )

    refresh_token = login_response.json()["refresh_token"]

    response = await client.post(
        "/cosmetology/rotation",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["access_token"]
    assert data["refresh_token"]


@pytest.mark.asyncio
async def test_get_categories_success(
    client: AsyncClient,
    sample_registration_in,
    procedure,
):
    await client.post(
        "/cosmetology/registration",
        json=sample_registration_in.model_dump(mode="json"),
    )

    login_response = await client.post(
        "/cosmetology/login",
        json={
            "phone": sample_registration_in.phone,
            "password": sample_registration_in.password,
        },
    )

    access_token = login_response.json()["access_token"]

    response = await client.get(
        "/cosmetology/categories",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_create_entry_success(
    client: AsyncClient,
    admin_tokens,
    entry_data,
):
    headers = {
        "Authorization": f"Bearer {admin_tokens['access_token']}"
    }

    response = await client.post(
        "/cosmetology/new_entry",
        json=entry_data,
        headers=headers,
    )

    assert response.status_code == 201


@pytest.mark.asyncio
async def test_get_entries_success(
    client: AsyncClient,
    admin_tokens,
    entry_data,
):
    headers = {
        "Authorization": f"Bearer {admin_tokens['access_token']}"
    }

    await client.post(
        "/cosmetology/new_entry",
        json=entry_data,
        headers=headers,
    )

    response = await client.get(
        "/cosmetology/get_entries",
        headers=headers,
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_delete_entry_success(
    client: AsyncClient,
    admin_tokens,
    entry_data,
    db_session,
):
    headers = {
        "Authorization": f"Bearer {admin_tokens['access_token']}"
    }

    await client.post(
        "/cosmetology/new_entry",
        json=entry_data,
        headers=headers,
    )

    result = await db_session.execute(select(EntryCosmetology))
    entry = result.scalars().first()

    response = await client.delete(
        f"/cosmetology/delete_entries/{entry.id}",
        headers=headers,
    )

    assert response.status_code == 200