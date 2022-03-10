import admin_commands
import configs
import handlers

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.contrib.fsm_storage.memory import MemoryStorage


BOT_TOKEN = configs.BOT_TOKEN


# Setup bot Dispatcher
bot = Bot(BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


# Setup i18n middleware
i18n = configs.Localization(configs.I18N_DOMAIN,
                            configs.LOCALES_DIR)
dp.middleware.setup(i18n)


# Alias for gettext method
_ = i18n.lazy_gettext


class SetReport(StatesGroup):
    report = State()


START_KEYBOARD = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(_("One"))],
        [types.KeyboardButton(_("Two"))],
        [types.KeyboardButton(_("Three"))],
    ],
    resize_keyboard=True,
)


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message, locale):
    print(locale)
    await message.answer(
        _("Hello, <b>{user}</b>!", locale=locale).format(user=message.from_user.full_name),
        reply_markup=START_KEYBOARD,
    )


@dp.message_handler(commands="lang")
async def cmd_lang(message: types.Message, locale):
    await message.answer(
        _("Your current language: <i>{language}</i>").format(language=locale)
    )


@dp.message_handler(commands="setlang")
async def cmd_setlang(message: types.Message):
    lang = message.get_args()

    if not lang:
        return await message.answer(_("Specify your language.\nExample: /setlang en"))
    if lang not in configs.LANGS:
        return await message.answer(_("This language is not available. Use en or ru"))

    configs.LANG_STORAGE[message.from_user.id] = lang
    configs.collusers.update_one({"_id": int(message.from_user.id)}, {
        "$set": {"lang": lang}})

    await message.answer(_("Language set.", locale=lang))
    await cmd_start(message, lang)


@dp.message_handler(text=_("One"))
async def text_one(message: types.Message):
    await message.answer(_("Really one"))


@dp.message_handler(text=_("Two"))
async def text_two(message: types.Message):
    await message.answer(_("Really two"))


@dp.message_handler(text=_("Three"))
async def text_three(message: types.Message):
    await message.answer(_("Really three"))


@dp.message_handler(commands='lang')
async def cmd_lang(message: types.Message, locale):
    # print(locale)
    # For setting custom lang you have to modify i18n middleware
    await message.reply(_('Your current language: <i>{language}</i>').format(language=locale))


@dp.message_handler(commands=["main"])
async def menu(message: types.Message):
    print("LOW", message)
    await handlers.menu_handler(message)


@dp.message_handler(commands=['post'])
async def post(message: types.Message):
    print("PRONTO", message)
    data = {'type': 'text', 'text': 'text', 'entities': None}
    users = 390736292,
    await admin_commands.send_post_all_users(data, users, bot)


@dp.message_handler(commands=["report"])
async def report(message: types.Message):
    await SetReport.report.set()
    await message.answer("Bizga o'z takliflaringizni yuboring!")


@dp.message_handler(state=SetReport.report,
                    content_types=configs.all_content_types)
async def report_process(message: types.Message, state: FSMContext):
    await handlers.report_process_handler(message, state, bot)


@dp.edited_message_handler()
async def msg_handler(message: types.Message):
    print(message)


@dp.pre_checkout_query_handler()
async def pre():
    print("PRE")


@dp.my_chat_member_handler()
async def some_handler(my_chat_member: types.ChatMemberUpdated):
    print(my_chat_member)


@dp.chat_member_handler()
async def some_handler(chat_member: types.ChatMemberUpdated):
    print("BAOBAB", chat_member)


@dp.message_handler(content_types=configs.all_content_types)
async def some_text(message: types.Message):
    print("DADA", message)
    print(configs.LANG_STORAGE)
    await handlers.some_text_handler(message, bot)


@dp.pre_checkout_query_handler(lambda shipping_query: True)
async def some_pre_checkout_query_handler(shipping_query: types.ShippingQuery):
    print("shipping", shipping_query)


@dp.shipping_query_handler(lambda shipping_query: True)
async def some_shipping_query_handler(shipping_query: types.ShippingQuery):
    print("EEE", shipping_query)


@dp.errors_handler()
async def some_error(baba, error):
    print("error", baba, error)


if __name__ == '__main__':
    executor.start_polling(dp,
                           on_startup=configs.on_startup,
                           on_shutdown=configs.on_shutdown, skip_updates=True)
