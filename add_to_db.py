import asyncio

from sqlalchemy import select
from db.models import async_session, Group, LavandaGroup

GROUPS = {
    -1001803559312: {
        "name": "Краснодар Объявления",
        "username": "krasnodar_ads",
        "link": "https://t.me/krasnodar_ads"
    },

    -1003730216520: {
        "name": "Тестовая",
        'username': 'ss',
        "link": "sds"

    },
    -1001854398226: {
        "name": "ВСЕ ОБЪЯВЛЕНИЯ КРАСНОДАРА",
        "username": "vse_obyavleniya_krasnodara23",
        "link": "https://t.me/vse_obyavleniya_krasnodara23"
    },
    -1002647897800: {
        "name": "Объявления | Барахолка | Краснодар",
        "username": "krasnodar_chatru",
        "link": "https://t.me/krasnodar_chatru"
    },
    -1001263253104: {
        "name": "Краснодар Объявления Реклама",
        "username": "krasnodarskayareklama",
        "link": "https://t.me/krasnodarskayareklama"
    },
    -1002370374751: {
        "name": "Барахолка | ЖК Самолет | Краснодар ",
        "username": "baraholka_samolet_ZO",
        "link": "https://t.me/baraholka_samolet_ZO"
    },
    -1001922970337: {
        "name": "ЖК Самолёт Краснодар | Соседи",
        "username": "sosedi_samolet_krd",
        "link": "https://t.me/sosedi_samolet_krd",
    },
    -1002596577488: {
        "name": "Краснодар Чат",
        "username": "krasnodar_krd_chat",
        "link": "https://t.me/krasnodar_krd_chat",
        "allowed_topics": [10790, 10797, 10795, 10800, 10804, 20189, 10802, 10806, 10816, 10812, 10814, 10808, 10810, 19177, 16785]
    }
}



async def import_groups_from_dict(groups_dict: dict):
    async with async_session() as session:

        for group_id, data in groups_dict.items():


            result = await session.execute(
                select(Group).where(Group.group_id == group_id)
            )
            exists = result.scalar_one_or_none()

            if exists:
                print(f"⚠️ group {group_id} already exists, skip")
                continue

            group = Group(
                group_id=group_id,
                name=data.get("name"),
                username=data.get("username"),
                url=data.get("link"),
                district='Краснодарский край',
                status='deactive',
                city='краснодар'

            )

            session.add(group)
            print(f"✅ added group: {group_id} | {data.get('name')}")

        await session.commit()

async def add_target_group():
    async with async_session() as session:

        group = LavandaGroup(
            group_id=-1003730216520,
            district='Краснодарский край',
            city='краснодар'
        )

        session.add(group)
        await session.commit()

asyncio.run(import_groups_from_dict(GROUPS))
asyncio.run(add_target_group())


