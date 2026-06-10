from telegram import Bot
import asyncio


TOKEN = "8621613099:AAHGN-ogOOBYgOiApjdU4bKfeWvRi4OLpg8"

CHAT_ID = "8538679635"


async def send_message():

    bot = Bot(token=TOKEN)

    await bot.send_message(
        chat_id=CHAT_ID,
        text="🔥 Telegram Alert Working!"
    )


asyncio.run(send_message())