from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.schemas.sellers import ReturnedAllSellers, ReturnedSeller, SellerCreate, SellerUpdate

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(seller: SellerCreate, session: DBSession):
    new_seller = Seller(**seller.dict())
    session.add(new_seller)
    await session.commit()

    stmt = select(Seller).options(joinedload(Seller.books)).filter(Seller.id == new_seller.id)
    result = await session.execute(stmt)
    fetched_seller = result.unique().scalar_one()

    return fetched_seller


@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    query = select(Seller).options(joinedload(Seller.books))
    result = await session.execute(query)
    sellers = result.scalars().unique().all()
    return {"sellers": sellers}


@sellers_router.get("/{seller_id}", response_model=ReturnedSeller)
async def get_seller(seller_id: int, session: DBSession):
    query = select(Seller).options(joinedload(Seller.books)).where(Seller.id == seller_id)
    result = await session.execute(query)
    seller = result.scalars().first()
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    return seller


@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, seller_data: SellerUpdate, session: DBSession):
    seller = await session.get(Seller, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    for var, value in vars(seller_data).items():
        setattr(seller, var, value) if value else None
    await session.commit()

    stmt = select(Seller).options(joinedload(Seller.books)).filter(Seller.id == seller.id)
    result = await session.execute(stmt)
    fetched_seller = result.unique().scalar_one()

    return fetched_seller


@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    seller = await session.get(Seller, seller_id)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    await session.delete(seller)
    await session.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
