import asyncio
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aiogram import Bot, Dispatcher
from handlers import router

TOKEN = "8697907546:AAEykJRRhqzaekp-7e0l-xn5TJZvpIDqLuE"

async def main():
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    
    logging.basicConfig(level=logging.INFO)
    print("🤖 ტელეგრამ ბოტი გაშვებულია...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
