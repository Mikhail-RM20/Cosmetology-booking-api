import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_registration_duplicate_phone(
    client: AsyncClient,
    sample_registration_in,
):
    await client.post(
        "/cosmetology/registration",
        json=sample_registration_in.model_dump(mode="json"),
    )

    response = await client.post(
        "/cosmetology/registration",
        json=sample_registration_in.model_dump(mode="json"),
    )

    assert response.status_code in (400, 409)


@pytest.mark.asyncio
async def test_registration_invalid_phone(client: AsyncClient):
    response = await client.post(
        "/cosmetology/registration",
        json={
            "name": "Клиент",
            "surname": "Тестовый",
            "phone": "123",
            "password": "test_password_1",
            "email": "test_email@mail.ru",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_registration_short_password(client: AsyncClient):
    response = await client.post(
        "/cosmetology/registration",
        json={
            "name": "Клиент",
            "surname": "Тестовый",
            "phone": "+79161234567",
            "password": "123",
            "email": "test_email@mail.ru",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_wrong_password(
    client: AsyncClient,
    sample_registration_in,
):
    await client.post(
        "/cosmetology/registration",
        json=sample_registration_in.model_dump(mode="json"),
    )

    response = await client.post(
        "/cosmetology/login",
        json={
            "phone": sample_registration_in.phone,
            "password": "wrong_password_1",
        },
    )

    assert response.status_code in (400, 401)


@pytest.mark.asyncio
async def test_login_unknown_user(client: AsyncClient):
    response = await client.post(
        "/cosmetology/login",
        json={
            "phone": "+79999999999",
            "password": "test_password_1",
        },
    )

    assert response.status_code in (400, 401, 404)


@pytest.mark.asyncio
async def test_rotation_invalid_token(client: AsyncClient):
    response = await client.post(
        "/cosmetology/rotation",
        json={"refresh_token": "invalid_token"},
    )

    assert response.status_code in (400, 401)


@pytest.mark.asyncio
async def test_get_categories_without_token(client: AsyncClient):
    response = await client.get("/cosmetology/categories")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_categories_invalid_token(client: AsyncClient):
    response = await client.get(
        "/cosmetology/categories",
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_entry_without_token(client: AsyncClient, entry_data):
    response = await client.post(
        "/cosmetology/new_entry",
        json=entry_data,
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_entry_invalid_time(
    client: AsyncClient,
    admin_tokens,
    procedure,
):
    headers = {
        "Authorization": f"Bearer {admin_tokens['access_token']}"
    }

    response = await client.post(
        "/cosmetology/new_entry",
        json={
            "procedure_id": procedure.id,
            "entry_date": "2030-01-01",
            "entry_time": "23:00",
        },
        headers=headers,
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_entries_without_token(client: AsyncClient):
    response = await client.get("/cosmetology/get_entries")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_entry_not_found(
    client: AsyncClient,
    sample_registration_in,
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

    response = await client.delete(
        "/cosmetology/delete_entries/999999",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 401