import asyncio
import logging

import uvicorn
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import webhook, paint
from app.commands import set_commands
from app.config import SETTINGS, BASE_DIR
from app.handlers import toxic_commands, commands, reactions, chat_members, errors, messages
from app.utils.jobs import job_day
from database import create_tables


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    await create_tables()

    bot = Bot(token=SETTINGS.BOT_TOKEN.get_secret_value(),
              default=DefaultBotProperties(parse_mode=ParseMode.HTML, link_preview_is_disabled=True))
    dp = Dispatcher()
    dp.include_routers(commands.router, toxic_commands.router, chat_members.router, errors.router,
                       messages.router, reactions.router)
    await set_commands(bot)

    app = FastAPI()
    app.mount('static', StaticFiles(directory=f'{BASE_DIR}/app/static'), 'static')
    app.include_router(webhook.router)
    app.include_router(paint.router)
    app.state.bot = bot
    app.state.dp = dp

    scheduler = AsyncIOScheduler(timezone=SETTINGS.TIME_ZONE)
    scheduler.add_job(job_day, 'cron', (bot,), hour=1, minute=1)
    scheduler.start()

    await bot.delete_webhook()
    # Uncomment for polling
    # await dp.start_polling(bot)
    await bot.set_webhook(url=f'{SETTINGS.WEBHOOK_DOMAIN}/{SETTINGS.BOT_TOKEN.get_secret_value()}',
                          drop_pending_updates=True)
    logging.info('Bot started')
    await uvicorn.Server(uvicorn.Config(app, host=SETTINGS.HOST, port=SETTINGS.PORT)).serve()


if __name__ == '__main__':
    asyncio.run(main())
