from telegram.ext import CommandHandler
from . import handlers


def register_all_handlers(app):
    commands = [
        ("start", handlers.start),
        ("help", handlers.help_command),
        ("about", handlers.about),
        # 继续添加其他命令
    ]
    for cmd, func in commands:
        app.add_handler(CommandHandler(cmd, func))
