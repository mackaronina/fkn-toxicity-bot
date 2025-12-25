from aiogram import Dispatcher, Bot
from aiogram.types import Update
from fastapi import APIRouter, Depends
from fastapi.requests import Request
from fastapi.responses import HTMLResponse

from app.config import SETTINGS
from app.utils.depends import get_bot, get_dp

router = APIRouter()


@router.post(f'/{SETTINGS.BOT_TOKEN.get_secret_value()}', include_in_schema=False)
async def webhook(request: Request, bot: Bot = Depends(get_bot), dp: Dispatcher = Depends(get_dp)) -> None:
    update = Update.model_validate(await request.json(), context={'bot': bot})
    await dp.feed_update(bot, update)


@router.get('/')
async def read_root() -> HTMLResponse:
    return HTMLResponse(content='Main page')
