from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.schemas import IncomingBook, ReturnedAllBooks, ReturnedBook
import src.services.books as book_service


books_router = APIRouter(tags=["books"], prefix="/books")
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@books_router.post("/", response_model=ReturnedBook, status_code=status.HTTP_201_CREATED)
async def create_book(book: IncomingBook, session: DBSession):
    new_book = await book_service.create_book(book, session)
    return new_book


@books_router.get("/", response_model=ReturnedAllBooks)
async def get_all_books(session: DBSession):
    books = await book_service.get_all_books(session)
    return books


@books_router.get("/{book_id}", response_model=ReturnedBook)
async def get_book(book_id: int, session: DBSession):
    book = await book_service.get_book(book_id, session)
    if not book:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return book


@books_router.delete("/{book_id}")
async def delete_book(book_id: int, session: DBSession):
    deleted_book = await book_service.delete_book(book_id, session)
    if not deleted_book:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@books_router.put("/{book_id}", response_model=ReturnedBook)
async def update_book(book_id: int, new_data: IncomingBook, session: DBSession):
    updated_book = await book_service.update_book(book_id, new_data, session)
    if not updated_book:
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    return updated_book
