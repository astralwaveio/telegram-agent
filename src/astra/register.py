import re
from telegram.ext import CommandHandler, MessageHandler, filters

from . import handlers


# =======================
# Handler 注册函数
# =======================

def register_all_handlers(application):
    # 1. 注册具体命令 handler
    commands = [
        ("start", handlers.start_command),
        ("help", handlers.help_command),
        ("news", handlers.news_command),
        ("remind", handlers.remind_command),
        ("tools", handlers.tools_command),
        ("cancel", handlers.cancel_command),
        ("settings", handlers.settings_command),
        ("about", handlers.about_command),
        # 继续添加其他命令
    ]
    for cmd, func in commands:
        application.add_handler(CommandHandler(cmd, func))

    # 2. 注册未知命令处理器
    application.add_handler(MessageHandler(filters.COMMAND, handlers.unknown), group=999)


def register_all_messages(application):
    # 1. 注册具体消息文本 handler
    button_map = [
        ("💬 聊天", handlers.chat_entry),
        ("🌤️ 天气", handlers.weather_entry),
        ("📦 快递", handlers.express_entry),
        ("📰 新闻", handlers.news_entry),
        ("🛠️ 工具", handlers.tools_entry),
        ("⏰ 提醒", handlers.remind_entry),
        # 继续添加其他按钮
    ]
    for msg, func in button_map:
        pattern = r"^" + re.escape(msg) + r"$"
        application.add_handler(MessageHandler(filters.TEXT & filters.Regex(pattern), func))

    # 2. 注册未知文本消息处理器
    application.add_handler(MessageHandler(filters.TEXT, handlers.unknown), group=999)
