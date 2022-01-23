import configs

from aiogram import types


async def start_menu_handler(m: types.Message):
    if configs.collusers.count_documents({"_id": m.from_user.id}) == 0:
        # Adding new user DB
        configs.collusers.insert_one({"_id": m.from_user.id,
                                      "username": m.from_user.username,
                                      "first_name": m.from_user.first_name,
                                      "last_name": m.from_user.last_name})
    elif configs.collusers.count_documents(
            {"_id": m.from_user.id, "status": False}) == 1:
        configs.collusers.update_one(
            {"_id": m.from_user.id}, {"$set": {"status": True}})
    else:
        configs.collusers.update_one(
            {"_id": m.from_user.id}, {"$set": {"status": True}})
    await m.answer("🏠 Main menu")


async def some_text_handler(message: types.Message):
    await message.answer("I'll answer for u")
