import re
from re import search

from aiogram import Router, F
from aiogram.types import Message, ReactionTypeEmoji
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import SETTINGS
from app.middlewares.db import DbSessionMiddleware
from app.utils.analize_toxicity import analize_toxicity
from app.utils.update_db_info import update_chat_info, update_user_info

router = Router()
router.message.middleware(DbSessionMiddleware())


@router.message(F.text | F.caption, F.chat.type != 'private')
async def msg_text(message: Message, session: AsyncSession) -> None:
    text = message.text or message.caption
    toxicity = await analize_toxicity(text)
    if toxicity > SETTINGS.TOXIC.THRESHOLD and message.forward_from is None:
        await message.react([ReactionTypeEmoji(emoji=SETTINGS.TOXIC.REACTION)])
        await update_chat_info(message.chat, session)
        await update_user_info(message.from_user, session, toxicity, text)
    if search(r'\bсбу\b', text, re.IGNORECASE):
        await message.reply_sticker(SETTINGS.STICKERS.SBU_FILE_ID)
    elif search(r'\bпоро[хш]', text, re.IGNORECASE) or search(r'\bрошен', text, re.IGNORECASE):
        await message.reply_sticker(SETTINGS.STICKERS.POROHOBOT_FILE_ID)
    elif search(r'\bзеленс', text, re.IGNORECASE) or search(r'\bзелебоб', text, re.IGNORECASE):
        await message.reply_sticker(SETTINGS.STICKERS.ZELEBOT_FILE_ID)
