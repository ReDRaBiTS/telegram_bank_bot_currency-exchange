from aiogram import Bot
from aiogram.types import BotCommand,BotCommandScopeDefault

async def set_commands(bot:Bot):
    commands =[
        BotCommand(
            command='start',
            description='🕐 Початок роботи з ботом'
        ),
        BotCommand(
            command='show',
            description='💶 Показати вибраний метод обміну валюти'
        ),
        BotCommand(
            command='change',
            description='🔁 Змінити вибраний метод обміну валюти'
        )
    ]

    await bot.set_my_commands(commands,BotCommandScopeDefault())