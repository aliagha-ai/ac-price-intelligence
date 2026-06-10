from telegram import Bot

from config.settings import (
    TOKEN,
    CHAT_ID
)


async def send_telegram_alert(message):

    bot = Bot(token=TOKEN)

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )