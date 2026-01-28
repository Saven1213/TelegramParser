
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from bot.config import tg_id_list
from db.crud.categories import save_category, get_category_by_id, get_categories, delete_category_from_db

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    tg_id = message.from_user.id

    if tg_id in tg_id_list:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='➕ Добавить категорию', callback_data='add_category'),
                    InlineKeyboardButton(text='Удалить категорию', callback_data='delete_category')
                ]
            ]
        )

        await message.answer(
            "👋 Добро пожаловать в админ-панель!\n\nВыберите действие:\n",
            reply_markup=keyboard)

@router.callback_query(F.data == 'main')
async def menu(callback: CallbackQuery):
    tg_id = callback.from_user.id

    if tg_id in tg_id_list:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='➕ Добавить категорию', callback_data='add_category'),
                    InlineKeyboardButton(text='Удалить категорию', callback_data='delete_category')
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

    buttons.append([InlineKeyboardButton(text="❌ Отмена", callback_data="cancel")])

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

