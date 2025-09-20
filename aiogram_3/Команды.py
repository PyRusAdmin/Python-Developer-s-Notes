from aiogram.filters import Command
from aiogram.types import Message

from system.system import api_key, api_secret, router


@router.message(Command("balance"))
async def balance(message: Message):
    """Отвечает на команду /balance"""
    await message.answer("⏳ Получаю информацию о балансе с Binance...")


def register_commands_handler():
    """"Регистрирует команды в боте"""
    router.message.register(balance)
