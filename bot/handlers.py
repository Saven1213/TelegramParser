

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from pyrogram.filters import inline_keyboard

from bot.config import tg_id_list
from db.crud.categories import save_category, get_category_by_id, get_categories, delete_category_from_db, \
    update_category_keywords
from db.crud.groups import insert_group, get_groups, delete_group, change_status, get_group
from db.crud.lavanda_groups import add_target_group

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    tg_id = message.from_user.id

    if tg_id in tg_id_list:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Категории', callback_data='categories')
                ],
                [
                    InlineKeyboardButton(text='Группы', callback_data='groups')
                ],
                [
                    InlineKeyboardButton(text='По каким городам работаем?', callback_data='district_change')
                ]
            ]
        )

        await message.answer(
            "👋 Добро пожаловать в админ-панель!\n\nВыберите действие:\n",
            reply_markup=keyboard)

@router.callback_query(F.data == 'main')
async def menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    tg_id = callback.from_user.id

    if tg_id in tg_id_list:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Категории', callback_data='categories')
                ],
                [
                    InlineKeyboardButton(text='Группы', callback_data='groups')
                ],
                [
                    InlineKeyboardButton(text='По каким городам работаем?', callback_data='district_change')
                ]
            ]
        )

        await callback.message.edit_text(
            "👋 Добро пожаловать в админ-панель!\n\nВыберите действие:\n",
            reply_markup=keyboard)

class AddCategory(StatesGroup):
    name = State()
    keywords = State()


@router.callback_query(F.data == 'add_category')
async def add_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddCategory.name)
    await callback.message.edit_text("📝 Введите название категории:")
    await callback.answer()


@router.callback_query(F.data == 'categories')
async def categories(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='➕ Добавить категорию', callback_data='add_category'),
                InlineKeyboardButton(text='Удалить категорию', callback_data='delete_category')
            ],
            [
                InlineKeyboardButton(text='Изменить категорию', callback_data='change_category')
            ]
        ]
    )

    text = "Выберите действие"

    await callback.message.edit_text(text=text, reply_markup=keyboard)

@router.message(AddCategory.name)
async def process_category_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(AddCategory.keywords)
    await message.answer("🔤 Введите ключевые слова через запятую без пробелов:\n\nПример: `недвижимость,квартира,дом`")


@router.message(AddCategory.keywords)
async def process_category_keywords(message: Message, state: FSMContext):
    data = await state.get_data()
    category_name = data['name']
    keywords = message.text

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏠 В главное меню", callback_data="main")]
        ]
    )



    await save_category(category_name, keywords)

    keywords_list = '\n'.join([keyword.strip() for keyword in keywords.split(',')])

    await message.answer(
        f"✅ Категория '{category_name}' добавлена!\n\n"
        f"<b>Ключевые слова:</b>\n"
        f"<blockquote><code>{keywords_list}</code></blockquote>",
        reply_markup=keyboard
    )
    await state.clear()


@router.callback_query(F.data == 'change_category')
async def change_category(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])

    category_list = await get_categories()

    for category in category_list:
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(text=category.get('name', 'category'), callback_data=f'category_change-{category.get("id", 0)}')
            ]
        )
    keyboard.inline_keyboard.append(
        [
            InlineKeyboardButton(text='🏠 В главное меню', callback_data='main')
        ]
    )

    await callback.message.edit_text(text='Выберите категорию которой хотите добавить ключевые слова: ', reply_markup=keyboard)

class NewKeywords(StatesGroup):
    keywords = State()

@router.callback_query(F.data.split('-')[0] == 'category_change')
async def new_keywords(callback: CallbackQuery, state: FSMContext):
    data = int(callback.data.split('-')[1])

    category = await get_category_by_id(data)
    print(category, '\n\n', category.id, category.keywords)

    await state.update_data(
        old_keywords=str(category.keywords or ""),
        category_id=int(category.id)
    )

    await state.set_state(NewKeywords.keywords)

    await callback.message.edit_text('Введите новые ключевые слова через запятую без пробелов: ')

@router.message(NewKeywords.keywords)
async def new_keywords(message: Message, state: FSMContext):

    data = await state.get_data()
    old_keywords_raw = data.get("old_keywords", "")
    print(old_keywords_raw)

    # 2️⃣ новые ключевые слова от пользователя
    new_keywords_raw = message.text.strip()

    # защита от пустого ввода
    if not new_keywords_raw:
        await message.answer("❌ Ключевые слова не могут быть пустыми")
        return

    # 3️⃣ превращаем в списки
    old_keywords = [
        k.strip().lower()
        for k in old_keywords_raw.split(",")
        if k.strip()
    ]
    print('\n\nold_keywords', old_keywords)

    new_keywords = [
        k.strip().lower()
        for k in new_keywords_raw.split(",")
        if k.strip()
    ]

    # 4️⃣ объединяем без дубликатов
    merged_keywords = sorted(set(old_keywords + new_keywords))

    # 5️⃣ обратно в строку
    result_keywords = ",".join(merged_keywords)


    category_id = data.get("category_id")

    await update_category_keywords(
        category_id=category_id,
        keywords=result_keywords
    )


    await state.clear()

    await message.answer(
        "✅ Ключевые слова обновлены:\n\n"
        f"<code>{result_keywords}</code>"
    )




class DeleteCategory(StatesGroup):
    confirm = State()


@router.callback_query(F.data == 'delete_category')
async def delete_category_start(callback: CallbackQuery, state: FSMContext):

    categories = await get_categories()  # TODO: функция для получения категорий

    if not categories:
        await callback.message.answer("📭 Категорий нет")
        return


    buttons = []
    for category in categories:
        buttons.append([InlineKeyboardButton(
            text=f"🗑️ {category['name']}",
            callback_data=f"delete_{category['id']}"
        )])

    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="main")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    await callback.message.answer(
        "🗑️ Выберите категорию для удаления:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delete_"))
async def delete_category_confirm(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[1])


    category = await get_category_by_id(category_id)  # TODO: функция для получения категории


    await state.update_data(category_id=category_id, category_name=category.name)


    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data="confirm_delete")],
        [InlineKeyboardButton(text="❌ Нет, отмена", callback_data="cancel_delete")]
    ])

    await callback.message.answer(
        f"⚠️ Вы уверены, что хотите удалить категорию?\n\n"
        f"<b>Название:</b> {category.name}\n"
        f"<b>Ключевые слова:</b> {category.keywords}",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "confirm_delete")
async def delete_category_final(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category_id = data['category_id']
    category_name = data['category_name']


    await delete_category_from_db(category_id)  # TODO: функция удаления


    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В главное меню", callback_data="main")]
    ])

    await callback.message.answer(
        f"✅ Категория '{category_name}' удалена!",
        reply_markup=keyboard
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "cancel_delete")
async def delete_category_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Удаление отменено")
    await state.clear()
    await callback.answer()



#ГРУППЫ


@router.callback_query(F.data == 'groups')
async def groups_handler(callback: CallbackQuery):


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить группу', callback_data='choose_group'),
                InlineKeyboardButton(text='Удалить группу', callback_data='remove_group')
            ],
            [
                InlineKeyboardButton(text='В главное меню', callback_data='main')
            ]
        ]
    )

    await callback.message.edit_text('Выберите действие: ', reply_markup=keyboard)

class AddGroup(StatesGroup):
    id_ = State()
    name = State()
    url = State()
    district = State()
    city = State()

class AddTargetGroup(StatesGroup):
    group_id = State()
    district = State()
    city = State()

@router.callback_query(F.data == 'choose_group')
async def choose_group(callback: CallbackQuery):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить группу города', callback_data='add_target_group')
            ],
            [
                InlineKeyboardButton(text='Добавить группу парсинга', callback_data='add_group')
            ]
        ]
    )

    await callback.message.edit_text('Какую группу добавить?', reply_markup=keyboard)

@router.callback_query(F.data == 'add_target_group')
async def target_group(callback: CallbackQuery, state: FSMContext):

    await callback.message.edit_text('Введите ID группы')

    await state.set_state(AddTargetGroup.group_id)

@router.message(AddTargetGroup.group_id)
async def write_id(message: Message, state: FSMContext):
    text = message.text

    await state.update_data(group_id=text)

    await message.answer('Введите регион\n\nПример: Краснодарский край, Московская область')

    await state.set_state(AddTargetGroup.district)

@router.message(AddTargetGroup.district)
async def write_district(message: Message, state: FSMContext):
    text = message.text

    await state.update_data(district=text)

    await message.answer('Введите город:')

    await state.set_state(AddTargetGroup.city)

@router.message(AddTargetGroup.city)
async def write_city(message: Message, state: FSMContext):
    city = message.text.lower()

    data = await state.get_data()

    group_id = int(data.get('group_id'))

    district = data.get('district')

    await add_target_group(group_id, district, city)

    await message.answer(f'Отлично, вы добавили новую группу в город {city}')

    await state.clear()





@router.callback_query(F.data == 'add_group')
async def add_group(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Введите ID группы')

    await state.set_state(AddGroup.id_)

@router.message(AddGroup.id_)
async def add_group_id(message: Message, state: FSMContext):
    group_id = message.text

    await state.update_data(group_id=group_id)

    await state.set_state(AddGroup.name)

    await message.answer("Введите название группы")

@router.message(AddGroup.name)
async def add_group_name(message: Message, state: FSMContext):
    group_name = message.text

    await state.update_data(group_name=group_name)

    await state.set_state(AddGroup.district)

    await message.answer("Введите край/область\n\nпример: Московская область, Краснодарский край")

@router.message(AddGroup.district)
async def add_district(message: Message, state: FSMContext):
    district = message.text

    await state.update_data(district=district)

    await message.answer("Введите город")

    await state.set_state(AddGroup.city)

@router.message(AddGroup.city)
async def add_city(message: Message, state: FSMContext):
    city = message.text.lower()

    await state.update_data(city=city)



    await message.answer("Введите ссылку группы")

    await state.set_state(AddGroup.url)



@router.message(AddGroup.url)
async def add_group_url(message: Message, state: FSMContext):
    group_url = message.text

    data = await state.get_data()

    group_id = data['group_id']
    group_name = data['group_name']
    group_username = group_url.split('/')[-1]
    if group_url.startswith('t'):
        group_url = 'https://' + group_url

    group_district = data.get('district')
    city = data.get('city').lower()


    group_info = {
        'group_id': int(group_id),
        'name': str(group_name),
        'username': str(group_username),
        'url': str(group_url),
        'district': group_district,
        'city': city
    }

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='В главное меню', callback_data='main')
            ]
        ]
    )

    await insert_group(group_info)

    await state.clear()

    await message.answer('Группа успешно добавлена!', reply_markup=keyboard)




@router.callback_query(F.data == 'remove_group')
async def remove_group(callback: CallbackQuery):
    groups = await get_groups()


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[]
    )

    for group in groups:
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(text=group.name, callback_data=f'group_for_remove-{group.id}')
            ]
        )

    keyboard.inline_keyboard.append(
        [
            InlineKeyboardButton(text='В главное меню', callback_data='main')
        ]
    )

    await callback.message.edit_text('Выберите группу для удаления', reply_markup=keyboard)

@router.callback_query(F.data.startswith("group_for_remove"))
async def delete_category_confirm(callback: CallbackQuery, state: FSMContext):
    group_id = int(callback.data.split("-")[1])








    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"group_confirm_delete-{group_id}")],
        [InlineKeyboardButton(text="❌ Нет, отмена", callback_data=f"group_cancel_delete")]
    ])

    await callback.message.answer(
        f"⚠️ Вы уверены, что хотите удалить группу??\n\n",
        reply_markup=keyboard,
    )
    await callback.answer()


@router.callback_query(F.data.split('-')[0] == "group_confirm_delete")
async def delete_category_final(callback: CallbackQuery, state: FSMContext):
    group_id = callback.data.split('-')[1]


    await delete_group(int(group_id))


    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 В главное меню", callback_data="main")]
    ])

    await callback.message.answer(
        f"✅ Группа удалена!",
        reply_markup=keyboard
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data.split('-')[0] == "group_cancel_delete")
async def delete_category_cancel(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("❌ Удаление отменено")
    await state.clear()
    await callback.answer()


# РЕГИОНЫ ПАРСЕР

@router.callback_query(F.data == 'district_change')
async def district_change(callback: CallbackQuery):
    districts = []

    groups = await get_groups()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[

        ]
    )
    if groups:
        for group in groups:
            if not group.district in districts:
                districts.append(group.district)

                keyboard.inline_keyboard.append(
                    [
                        InlineKeyboardButton(text=group.district, callback_data=f'district_parse!{group.group_id}')
                    ]
                )
        keyboard.inline_keyboard.append(
            [
                InlineKeyboardButton(text='В главное меню', callback_data='main')
            ]
        )

        await callback.message.edit_text('Выберите область', reply_markup=keyboard)

    else:
        await callback.message.edit_text('Пока ничего нет')

@router.callback_query(F.data.split('!')[0] == 'district_parse')
async def active_districts(callback: CallbackQuery):
    data = callback.data.split('!')[1]


    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Парсить", callback_data=f'groups_on!{data}')
            ],
            [
                InlineKeyboardButton(text='В меню', callback_data='main')
            ]
        ]
    )

    await callback.message.edit_text('Тут вы можете включить группу для парсинга', reply_markup=keyboard)

@router.callback_query(F.data.split('!')[0] == 'groups_on')
async def groups_on(callback: CallbackQuery):
    data = callback.data.split('!')[1]

    group = await get_group(int(data))
    district = group.district

    await change_status(district)

    await callback.message.edit_text(f'Отлично, будем парсить {district}, Капитан!')






