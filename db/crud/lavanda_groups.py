from sqlalchemy import select

from db.models import async_session, LavandaGroup


async def get_target_group(city):
    async with async_session() as session:
        res = await session.execute(select(LavandaGroup).where(LavandaGroup.city == city))

        group = res.scalar_one_or_none()

        return group

