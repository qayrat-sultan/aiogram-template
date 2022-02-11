import datetime
import logging
import os

from pathlib import Path
from typing import Tuple, Any

from aiogram import types
from aiogram.utils.exceptions import BotBlocked, BotKicked, UserDeactivated
from aiogram.contrib.middlewares.i18n import I18nMiddleware
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Main telegram bot configs
BOT_TOKEN = os.getenv("BOT_TOKEN")


# Telegram chats
ADMIN_IDS = tuple(os.getenv("ADMIN_IDS").split(","))
GROUP_ID = int(os.getenv("GROUP_ID"))


# Language
LANG_STORAGE = {}
LANGS = ["ru", "en", "uz"]
I18N_DOMAIN = "mybot"
BASE_DIR = Path(__file__).parent
LOCALES_DIR = BASE_DIR / "locales"


# Database
MONGO_URL = os.getenv("MONGO_URL")
cluster = MongoClient(MONGO_URL)
collusers = cluster.chatbot.users
collreports = cluster.chatbot.reports


# Telegam supported types
all_content_types = ["text", "sticker", "photo",
                     "voice", "document", "video", "video_note"]


# Logging
if not os.getenv("DEBUG"):
    formatter = '[%(asctime)s] %(levelname)8s --- %(message)s (%(filename)s:%(lineno)s)'
    logging.basicConfig(
        filename=f'logs/bot-from-{datetime.datetime.now().date()}.log',
        filemode='w',
        format=formatter,
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.WARNING
    )


class Localization(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]) -> str:
        """
        User locale getter
        You can override the method if you want to use different way of getting user language.
        :param action: event name
        :param args: event arguments
        :return: locale name
        """
        user: types.User = types.User.get_current()

        if LANG_STORAGE.get(user.id) is None:
            LANG_STORAGE[user.id] = "en"
        *_, data = args
        language = data['locale'] = LANG_STORAGE[user.id]
        return language


# On start polling telegram this function running
async def on_startup(dp):
    users_lang = collusers.find({}, {"_id": 1, "lang": 1})
    for i in users_lang:
        LANG_STORAGE[i.get("_id")] = i.get("lang", "uz")
    for i in ADMIN_IDS:
        try:
            await dp.bot.send_message(i, "Bot are start!")
        except (BotKicked, BotBlocked, UserDeactivated):
            pass


# On stop polling Telegram, this function running and stopping polling's
async def on_shutdown(dp):
    logging.warning("Shutting down..")
    for i in ADMIN_IDS:
        try:
            await dp.bot.send_message(i, "Bot are shutting down!")
        except (BotKicked, BotBlocked, UserDeactivated):
            pass
    await dp.storage.close()
    await dp.storage.wait_closed()
    logging.warning("Bye!")
