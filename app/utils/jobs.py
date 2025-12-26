import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import ChatMemberAdministrator

from app.config import SETTINGS
from app.dao.dao import UserDAO, ChatDAO


async def job_day(bot: Bot) -> None:
    user = await UserDAO.get_best_today()
    if user is not None:
        text = f'Сегодня {user.name} перевыполнил норму токсичности'
        logging.info(f'Toxic of the day is {user.name} with id {user.id}. Today toxic level: {user.today_toxic_level}')
    else:
        text = 'Сегодня обошлось без токсиков'
        logging.info('Today without toxic users')
    await UserDAO.update_today_to_zero()
    bot_id = (await bot.get_me()).id
    chats = await ChatDAO.find_all()
    for chat in chats:
        try:
            await bot.send_sticker(chat.id, SETTINGS.STICKERS.NIGHT_FILE_ID)
            await bot.send_message(chat.id, text)
            member = await bot.get_chat_member(chat.id, bot_id)
            if not isinstance(member, ChatMemberAdministrator):
                logging.warning(f"Bot doesn't have administrator rights in chat {chat.id}")
                await bot.send_message(chat.id, 'У бота нет админки в этом чате, а должна быть сука')
        except TelegramAPIError:
            logging.warning(f'Message to chat with id {chat.id} not sent')
