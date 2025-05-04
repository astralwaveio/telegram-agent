import re

from telegram.ext import CommandHandler, MessageHandler, filters

from . import handlers


# =======================
# Handler 注册函数
# =======================

def register_all_handlers(application):
    # 注册已知命令
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
        # CommandHandler 只会匹配 /xxx 命令
        application.add_handler(CommandHandler(command=cmd, callback=func, block=True))

    # 未知命令处理器，优先级低（group=999）
    application.add_handler(
        MessageHandler(filters=filters.COMMAND, callback=handlers.unknown, block=True), group=999
    )


def register_all_messages(application):
    # 注册已知按钮文本（非/开头文本）
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
        # 只处理非命令文本
        application.add_handler(
            MessageHandler(filters=filters.TEXT & ~filters.COMMAND & filters.Regex(pattern), callback=func, block=True)
        )

    # 未知文本消息处理器，优先级低（group=999）
    application.add_handler(
        MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=handlers.unknown, block=True), group=999
    )
