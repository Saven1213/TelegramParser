from aiogram import Router
from bot.handlers import router as h_router

router = Router()

router.include_router(h_router)