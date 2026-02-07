from sqlalchemy import select

from db.models import async_session, LavandaGroup


async def get_target_group(city):
    async with async_session() as session:
        res = await session.execute(select(LavandaGroup).where(LavandaGroup.city == city))

        group = res.scalar_one_or_none()

        return group


async def add_target_group(group_id: int, district: str, city: str):
    async with async_session() as session:

        result = await session.execute(
            select(LavandaGroup).where(LavandaGroup.group_id == group_id)
        )
        l_group = result.scalar_one_or_none()

        if l_group:

            l_group.district = district
            l_group.city = city
        else:

            group = LavandaGroup(
                group_id=group_id,
                district=district,
                city=city
            )
            session.add(group)

        await session.commit()

