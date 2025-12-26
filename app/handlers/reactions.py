from aiogram import Router, types, F

from app.dao.dao import UserDAO

router = Router()


@router.message_reaction(F.chat.type != 'private')
async def msg_reaction(event: types.MessageReactionUpdated) -> None:
    await UserDAO.update_reactions(event.user, event.new_reaction)
