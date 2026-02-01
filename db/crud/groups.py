from datetime import datetime
from db.models import async_session, Group
from sqlalchemy import select


async def insert_group(data: dict):
    async with async_session() as session:
        group = Group(
            group_id=data.get('group_id'),
            name=data.get('name'),
            username=data.get('username'),
            url=data.get('url')
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
            select(Group.group_id)
        )
        ids = [row[0] for row in result.all()]
    return ids

