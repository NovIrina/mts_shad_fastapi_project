from typing import List

from pydantic import BaseModel, EmailStr

from .books import ReturnedBook

__all__ = ["SellerCreate", "SellerUpdate", "ReturnedSeller", "ReturnedAllSellers"]


class SellerBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class SellerCreate(SellerBase):
    password: str


class SellerUpdate(SellerBase):
    pass


class ReturnedSeller(SellerBase):
    id: int
    books: List[ReturnedBook] = []

    class Config:
        orm_mode = True


class ReturnedAllSellers(BaseModel):
    sellers: list[ReturnedSeller]

    class Config:
        orm_mode = True
