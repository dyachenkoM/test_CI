import pytest
from tests.conftest import async_db_session, async_db_engine


@pytest.mark.asyncio
async def test_create_recipe(client, async_db_engine):
    recipe_data = {
        "name": "Test Recipe",
        "description": "Test Description",
        "cooking_time": 30,
        "ingredients": ""
    }
    response = await client.post("/recipes/", json=recipe_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Recipe"
    assert "id" in data


@pytest.mark.asyncio
async def test_read_recipe(client, async_db_engine):
    recipe_data = {
        "name": "Test Recipe",
        "description": "Test Description",
        "cooking_time": 30,
        "ingredients": ""
    }
    response = await client.post("/recipes/", json=recipe_data)
    recipe_id = response.json()["id"]

    response = await client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == recipe_id
    assert data["name"] == "Test Recipe"
