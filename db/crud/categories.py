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