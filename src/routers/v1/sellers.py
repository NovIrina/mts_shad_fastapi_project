from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.configurations.database import get_async_session
from src.schemas.sellers import ReturnedAllSellers, ReturnedSeller, SellerCreate, SellerUpdate
import src.services.sellers as seller_service


sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")
DBSession = Annotated[AsyncSession, Depends(get_async_session)]


@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)
async def create_seller(seller: SellerCreate, session: DBSession):
    fetched_seller = await seller_service.create_seller(seller, session)
    return fetched_seller


@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):
    sellers = await seller_service.get_all_sellers(session)
    return sellers


@sellers_router.get("/{seller_id}", response_model=ReturnedSeller)
async def get_seller(seller_id: int, session: DBSession):
    seller = await seller_service.get_seller(seller_id, session)
    if not seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    return seller


@sellers_router.put("/{seller_id}", response_model=ReturnedSeller)
async def update_seller(seller_id: int, seller_data: SellerUpdate, session: DBSession):
    fetched_seller = await seller_service.update_seller(seller_id, seller_data, session)
    if not fetched_seller:
        raise HTTPException(status_code=404, detail="Seller not found")
    return fetched_seller


@sellers_router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_seller(seller_id: int, session: DBSession):
    success = await seller_service.delete_seller(seller_id, session)
    if not success:
        raise HTTPException(status_code=404, detail="Seller not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
