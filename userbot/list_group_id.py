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
    # Пример:
    # -1001234567891: {
    #     "name": "Обычный канал",
    #     "username": "simple_channel",
    #     "link": "https://t.me/simple_channel",
    #     "has_topics": False
    # }
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