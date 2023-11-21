import asyncio
import logging
import os
import sys
import requests
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold

from functions import RocketChat


load_dotenv()

# Bot token can be obtained via https://t.me/BotFather
TOKEN = os.environ.get("BOT_TOKEN")

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()
rocket_chat = RocketChat('http://192.168.0.133:3000')


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`

    await message.answer(f"Hello, {hbold(message.from_user.full_name)}!")


@dp.message()
async def echo_handler(message: types.Message) -> None:
    """
    Handler will forward receive a message back to the sender

    By default, message handler will handle all message types (like a text, photo, sticker etc.)
    """
    # Login to rocket chat as admin
    rocket_chat.login_as_admin()

    # Generate channel name
    channel_name = f'Telegram_{message.from_user.username}'

    # Get or crate channel
    rocket_chat.get_or_create_channel(channel_name=channel_name, members=['Quat'])

    # Get or create income rocket chat integration
    income_integration = rocket_chat.get_or_create_income_integration(
        username='TelegramBot',
        channel=channel_name,
    )
    # Send message from telegram to rocket chat by integration
    # print(message.audio)
    # print(message.video)
    # print(message.document)
    # print(message.photo)

    requests.post(income_integration, json={'text': message.text})

    # Create API url to send message to particular telegram chat
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={message.chat.id}'

    # Get or create outcome rocket chat integration
    rocket_chat.get_or_create_outcome_integration(
        username='TelegramBot',
        event='sendMessage',
        channel=channel_name,
        urls=[url],
        token=str(message.chat.id),
    )


async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
