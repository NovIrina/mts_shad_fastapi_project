from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.books import Book
from src.schemas import IncomingBook


async def create_book(book_data: IncomingBook, session: AsyncSession):
    new_book = Book(
        title=book_data.title,
        author=book_data.author,
        year=book_data.year,
        count_pages=book_data.count_pages,
        seller_id=book_data.seller_id
    )
    session.add(new_book)
    await session.flush()
    return new_book


async def get_all_books(session: AsyncSession):
    query = select(Book)
    res = await session.execute(query)
    books = res.scalars().all()
    return {"books": books}


async def get_book(book_id: int, session: AsyncSession):
    res = await session.get(Book, book_id)
    return res


async def delete_book(book_id: int, session: AsyncSession):
    deleted_book = await session.get(Book, book_id)
    if deleted_book:
        await session.delete(deleted_book)
        await session.commit()
    return deleted_book


async def update_book(book_id: int, new_data: IncomingBook, session: AsyncSession):
    updated_book = await session.get(Book, book_id)
    if updated_book:
        updated_book.author = new_data.author
        updated_book.title = new_data.title
        updated_book.year = new_data.year
        updated_book.count_pages = new_data.count_pages
        updated_book.seller_id = new_data.seller_id
        await session.flush()
        return updated_book
    return None
