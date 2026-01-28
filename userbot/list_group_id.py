GROUPS = {
    -1001803559312: {
        "name": "Краснодар Объявления",
        "username": "krasnodar_ads",
        "link": "https://t.me/krasnodar_ads"
    },

    -5058839083: {
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
    -1001234567890: {
        "name": "Краснодар Чат",
        "username": "krasnodar_krd_chat",
        "link": "https://t.me/krasnodar_krd_chat",
        "allowed_topics": [10790, 10797, 10795, 10800, 10804, 20189, 10802, 10806, 10816, 10812, 10814, 10808, 10810, 19177, 16785]
    }
}


SUPERGROUPS_WITH_TOPICS = {
    # Пример супергруппы с топиками:
    # -1001234567890: {
    #     "name": "Супергруппа с темами",
    #     "username": "supergroup_with_topics",
    #     "link": "https://t.me/supergroup_with_topics",
    #     "has_topics": True,
    #     "topics": [
    #         {"id": 123, "name": "Объявления"},
    #         {"id": 124, "name": "Обсуждения"},
    #         {"id": 125, "name": "Вопросы"}
    #     ]
    # }
}

SUPERGROUPS = {
    -1001234567890: {
        "name": "Краснодар Чат",
        "username": "krasnodar_krd_chat",
        "link": "https://t.me/krasnodar_krd_chat",
        "allowed_topics": [10790, 10797, 10795, 10800, 10804, 20189, 10802, 10806, 10816, 10812, 10814, 10808, 10810, 19177, 16785]
    }
}

ALL_CHANNELS = {**GROUPS, **SUPERGROUPS_WITH_TOPICS, **SUPERGROUPS}
ALL_CHANNEL_IDS = list(ALL_CHANNELS.keys())


CHANNELS_WITH_TOPICS_IDS = [
    channel_id for channel_id, info in ALL_CHANNELS.items()
    if info.get("has_topics", False)
]

def get_channel_info(channel_id: int) -> dict:
    """Получить информацию о канале по его ID"""
    return ALL_CHANNELS.get(channel_id, {
        "name": "Неизвестный канал",
        "username": None,
        "link": None,
        "has_topics": False,
        "topics": []
    })