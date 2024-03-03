from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from src.models.sellers import Seller
from src.schemas.sellers import SellerCreate, SellerUpdate


async def create_seller(seller_data: SellerCreate, session: AsyncSession):
    new_seller = Seller(**seller_data.dict())
    session.add(new_seller)
    await session.commit()

    stmt = select(Seller).options(joinedload(Seller.books)).filter(Seller.id == new_seller.id)
    result = await session.execute(stmt)
    fetched_seller = result.unique().scalar_one()

    return fetched_seller


async def get_all_sellers(session: AsyncSession):
    query = select(Seller).options(joinedload(Seller.books))
    result = await session.execute(query)
    sellers = result.scalars().unique().all()
    return {"sellers": sellers}


async def get_seller(seller_id: int, session: AsyncSession):
    query = select(Seller).options(joinedload(Seller.books)).where(Seller.id == seller_id)
    result = await session.execute(query)
    seller = result.scalars().first()
    return seller


async def update_seller(seller_id: int, seller_data: SellerUpdate, session: AsyncSession):
    seller = await session.get(Seller, seller_id)
    if not seller:
        return None
    for var, value in vars(seller_data).items():
        setattr(seller, var, value) if value else None
    await session.commit()

    stmt = select(Seller).options(joinedload(Seller.books)).filter(Seller.id == seller.id)
    result = await session.execute(stmt)
    fetched_seller = result.unique().scalar_one()

    return fetched_seller


async def delete_seller(seller_id: int, session: AsyncSession):
    seller = await session.get(Seller, seller_id)
    if not seller:
        return None
    await session.delete(seller)
    await session.commit()
    return True
