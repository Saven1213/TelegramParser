from datetime import datetime
from db.models import async_session, Group
from sqlalchemy import select


async def insert_group(data: dict):
    async with async_session() as session:
        group = Group(
            group_id=data.get('group_id'),
            name=data.get('name'),
            username=data.get('username'),
            url=data.get('url'),
            district=data.get('district'),
            status='deactive',
            city=data.get('city')
        )

        session.add(group)

        await session.commit()

async def get_groups():
    async with async_session() as session:
        result = await session.execute(select(Group))
        groups = result.scalars().all()

        return groups

async def delete_group(group_id: int):
    async with async_session() as session:
        group = await session.get(Group, group_id)
        if group:
            await session.delete(group)
            await session.commit()

async def get_group_ids():
    async with async_session() as session:
        result = await session.execute(
            select(Group.group_id).where(Group.status == "active")
        )
        return set(result.scalars().all())

async def change_status(district: str):
    async with async_session() as session:
        res = await session.execute(select(Group))
        all_groups = res.scalars().all()

        target_groups = []
        other_groups = []

        for group in all_groups:
            if group.district == district:
                target_groups.append(group)
            else:
                other_groups.append(group)

        for group in target_groups:
            group.status = 'active'

        for group in other_groups:
            group.status = 'deactive'

        await session.commit()

async def get_group(id_):
    async with async_session() as session:
        res = await session.execute(select(Group).where(Group.id == id_))

        group = res.scalar_one_or_none()

        if group:
            return group


