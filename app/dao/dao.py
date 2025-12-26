import html
import logging
from typing import Sequence

from aiogram import types
from aiogram.types import ReactionType, ReactionTypeEmoji
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.dao.base import BaseDAO
from app.database import User, Chat, connection


class UserDAO(BaseDAO[User]):
    model = User

    @classmethod
    @connection
    async def update_data(cls, tg_user: types.User, toxicity_percent: float, text: str, session: AsyncSession) -> None:
        user_name = html.escape(tg_user.full_name)
        text = html.escape(text.replace('\n', ''))[:500]
        logging.info(f'Toxic message from user {user_name} with id {tg_user.id}. Text: {text}')
        user = await cls.find_one_or_none_by_id(tg_user.id, session=session)
        if user is None:
            await cls.add(id=tg_user.id, name=user_name, max_toxic_percent=toxicity_percent, max_toxic_text=text,
                          session=session)
        else:
            user.name = user_name
            user.toxic_level += 1
            user.today_toxic_level += 1
            if toxicity_percent > user.max_toxic_percent:
                user.max_toxic_percent = toxicity_percent
                user.max_toxic_text = text

    @classmethod
    @connection
    async def update_reactions(cls, tg_user: types.User, new_reactions: list[ReactionType],
                               session: AsyncSession) -> None:
        user = await cls.find_one_or_none_by_id(tg_user.id, session=session)
        if user is None:
            return
        if len(new_reactions) < 1 or not isinstance(new_reactions[0], ReactionTypeEmoji):
            return
        reaction = new_reactions[0].emoji
        if reaction in user.reactions_count:
            user.reactions_count[reaction] += 1
        else:
            user.reactions_count[reaction] = 1

    @classmethod
    @connection
    async def get_random_text(cls, session: AsyncSession) -> str | None:
        result = await session.execute(
            select(User).where(User.max_toxic_text.is_not(None)).order_by(func.random()).limit(1)
        )
        user = result.scalars().one_or_none()
        if user is not None:
            return user.max_toxic_text
        return None

    @classmethod
    @connection
    async def get_top(cls, session: AsyncSession) -> Sequence[User]:
        result = await session.execute(
            select(User).where(User.toxic_level > 0).order_by(User.toxic_level.desc()).limit(10)
        )
        return result.scalars().all()

    @classmethod
    @connection
    async def get_best_today(cls, session: AsyncSession) -> User | None:
        result = await session.execute(
            select(User).where(User.today_toxic_level > 0).order_by(User.today_toxic_level.desc()).limit(1)
        )
        return result.scalars().one_or_none()

    @classmethod
    @connection
    async def update_today_to_zero(cls, session: AsyncSession) -> None:
        await session.execute(update(User).values(today_toxic_level=0))


class ChatDAO(BaseDAO[Chat]):
    model = Chat

    @classmethod
    @connection
    async def update_data(cls, tg_chat: types.Chat, session: AsyncSession) -> None:
        chat_name = html.escape(tg_chat.title)
        logging.info(f'Toxic message in chat {chat_name} with id {tg_chat.id}')
        chat = await cls.find_one_or_none_by_id(tg_chat.id, session=session)
        if chat is None:
            await cls.add(id=tg_chat.id, name=chat_name, session=session)
        else:
            chat.name = chat_name
            chat.toxic_level += 1

    @classmethod
    @connection
    async def get_best(cls, session: AsyncSession) -> Chat | None:
        result = await session.execute(
            select(Chat).where(Chat.toxic_level > 0).order_by(Chat.toxic_level.desc()).limit(1)
        )
        return result.scalars().one_or_none()
