from sqlalchemy import select
from db.models import async_session, Category

async def get_categories():
    async with async_session() as session:
        result = await session.execute(select(Category))
        categories = result.scalars().all()

        category_data = []
        for cat in categories:
            keywords = [k.strip().lower() for k in cat.keywords.split(",") if k.strip()]
            category_data.append({
                "id": cat.id,
                "name": cat.name,
                "keywords": keywords
            })
        print(category_data)

        return category_data

async def save_category(name: str, keywords: str):
    async with async_session() as session:
        cat = Category(
            name=name,
            keywords=keywords
        )

        session.add(cat)

        await session.commit()

async def get_category_by_id(category_id: int):
    async with async_session() as session:
        result = await session.execute(select(Category).where(Category.id == category_id))
        return result.scalar_one_or_none()

async def delete_category_from_db(category_id: int):
    async with async_session() as session:
        category = await session.get(Category, category_id)
        if category:
            await session.delete(category)
            await session.commit()

async def update_category_keywords(
    category_id: int,
    keywords: str
) -> None:
    async with async_session() as session:

        result = await session.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()

        if not category:
            raise ValueError(f"Category with id={category_id} not found")

        category.keywords = keywords

        await session.commit()