import pytest
from fastapi import status
from sqlalchemy import select

from src.models.books import Book
from src.models.sellers import Seller


async def create_seller(first_name: str, last_name: str, email: str, password: str,
                        db_session) -> int:
    new_seller = Seller(first_name=first_name, last_name=last_name, email=email, password=password)
    db_session.add(new_seller)
    await db_session.commit()
    await db_session.refresh(new_seller)
    return new_seller.id


async def create_book(author: str, title: str, year: int, count_pages: int,
                      seller_id: int, db_session) -> None:
    new_book = Book(author=author, title=title, year=year, count_pages=count_pages,
                    seller_id=seller_id)
    db_session.add(new_book)
    await db_session.commit()
    await db_session.refresh(new_book)
    return new_book.id


@pytest.mark.asyncio
async def test_create_seller(async_client):
    seller_data = {
        "first_name": "Asya",
        "last_name": "Smirnova",
        "email": "asya@example.com",
        "password": "password123"
    }
    response = await async_client.post("/api/v1/sellers/", json=seller_data)

    assert response.status_code == status.HTTP_201_CREATED
    result_data = response.json()

    assert result_data["first_name"] == seller_data["first_name"]
    assert result_data["last_name"] == seller_data["last_name"]
    assert result_data["email"] == seller_data["email"]

    assert "id" in result_data
    assert "books" in result_data


@pytest.mark.asyncio
async def test_get_all_sellers(async_client, db_session):
    seller1 = await create_seller("Ivan", "Ivanov", "ivan@example.com", "password123",
                                  db_session)
    await create_book(author="Pushkin", title="Evgeniy Onegin", year=2001,
                      count_pages=104, seller_id=seller1, db_session=db_session)
    seller2 = await create_seller("Zhenya", "Ivanov", "zhenya@example.com", "password456",
                                  db_session)

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK
    sellers = response.json().get("sellers", [])

    assert len(sellers) >= 2

    expected_sellers_emails = ["ivan@example.com", "zhenya@example.com"]

    sellers_emails = [seller.get("email") for seller in sellers]

    for email in expected_sellers_emails:
        assert email in sellers_emails

    ivan = next((seller for seller in sellers if seller["email"] == "ivan@example.com"), None)
    zhenya = next((seller for seller in sellers if seller["email"] == "zhenya@example.com"), None)

    assert ivan is not None
    assert ivan["id"] == seller1
    assert ivan["first_name"] == "Ivan"
    assert ivan["last_name"] == "Ivanov"
    assert len(ivan["books"]) == 1
    assert ivan["books"][0]["title"] == "Evgeniy Onegin"
    assert ivan["books"][0]["author"] == "Pushkin"
    assert ivan["books"][0]["year"] == 2001
    assert ivan["books"][0]["count_pages"] == 104

    assert zhenya is not None
    assert zhenya["id"] == seller2
    assert zhenya["first_name"] == "Zhenya"
    assert zhenya["last_name"] == "Ivanov"
    assert len(zhenya["books"]) == 0


@pytest.mark.asyncio
async def test_get_seller(async_client, db_session):
    seller_id = await create_seller("Vlad", "Petrov", "vlad@example.com",
                                    "password789", db_session)

    response = await async_client.get(f"/api/v1/sellers/{seller_id}")

    assert response.status_code == status.HTTP_200_OK
    seller = response.json()
    assert seller["id"] == seller_id
    assert seller["first_name"] == "Vlad"
    assert seller["last_name"] == "Petrov"


@pytest.mark.asyncio
async def test_get_seller_security(async_client, db_session):
    seller_id = await create_seller("Asya", "Bulochkina", "secret_asya@example.com",
                                    "secretpassword789", db_session)

    response = await async_client.get(f"/api/v1/sellers/{seller_id}")

    assert response.status_code == status.HTTP_200_OK
    seller = response.json()
    assert "password" not in seller


@pytest.mark.asyncio
async def test_get_seller_books(async_client, db_session):
    seller_id = await create_seller("Egor", "Smirnov", "egor@example.com",
                                    "password982", db_session)
    await create_book("Bulgakov", "Master and Margarita", 1990, 200, seller_id, db_session)

    response = await async_client.get(f"/api/v1/sellers/{seller_id}")

    assert response.status_code == status.HTTP_200_OK
    seller = response.json()
    assert len(seller["books"]) == 1
    assert seller["books"][0]["author"] == "Bulgakov"
    assert seller["books"][0]["title"] == "Master and Margarita"
    assert seller["books"][0]["year"] == 1990
    assert seller["books"][0]["count_pages"] == 200
    assert seller["books"][0]["seller_id"] == seller_id


@pytest.mark.asyncio
async def test_update_seller(async_client, db_session):
    seller_id = await create_seller("Maxim", "Developer", "max@example.com",
                                    "password101", db_session)

    update_data = {
        "first_name": "Max",
        "last_name": "DevOps",
        "email": "max.devops@example.com"
    }
    response = await async_client.put(f"/api/v1/sellers/{seller_id}", json=update_data)

    assert response.status_code == status.HTTP_200_OK
    updated_seller = response.json()
    assert updated_seller["email"] == "max.devops@example.com"
    assert updated_seller["first_name"] == "Max"
    assert updated_seller["last_name"] == "DevOps"


@pytest.mark.asyncio
async def test_delete_seller(async_client, db_session):
    seller_id = await create_seller("Petya", "Petrov", "petya@example.com",
                                    "password303", db_session)
    await create_book(author="Lermontov", title="A Hero of Our Time", year=1840,
                      count_pages=221, seller_id=seller_id, db_session=db_session)

    response = await async_client.delete(f"/api/v1/sellers/{seller_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Verifying that the seller is actually removed from the database
    result = await db_session.execute(select(Seller).where(Seller.id == seller_id))
    seller = result.scalars().first()
    assert seller is None

    # Verifying that all books related to this seller are also removed
    result = await db_session.execute(select(Book).where(Book.seller_id == seller_id))
    assert len(result.scalars().all()) == 0
