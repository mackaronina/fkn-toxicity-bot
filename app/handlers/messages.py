import re
from re import search

from aiogram import Router, F
from aiogram.types import Message, ReactionTypeEmoji

from app.config import SETTINGS
from app.dao.dao import ChatDAO, UserDAO
from app.utils.analize_toxicity import analize_toxicity

router = Router()


@router.message(F.text | F.caption, F.chat.type != 'private')
async def msg_text(message: Message) -> None:
    text = message.text or message.caption
    toxicity_percent = await analize_toxicity(text)
    if toxicity_percent > SETTINGS.TOXIC.THRESHOLD and message.forward_from is None:
        await message.react([ReactionTypeEmoji(emoji=SETTINGS.TOXIC.REACTION)])
        await ChatDAO.update_data(message.chat)
        await UserDAO.update_data(message.from_user, toxicity_percent, text)
    if search(r'\bсбу\b', text, re.IGNORECASE):
        await message.reply_sticker(SETTINGS.STICKERS.SBU_FILE_ID)
    elif search(r'\bпоро[хш]', text, re.IGNORECASE) or search(r'\bрошен', text, re.IGNORECASE):
        await message.reply_sticker(SETTINGS.STICKERS.POROHOBOT_FILE_ID)
    elif search(r'\bзеленс', text, re.IGNORECASE) or search(r'\bзелебоб', text, re.IGNORECASE):
        await message.reply_sticker(SETTINGS.STICKERS.ZELEBOT_FILE_ID)
