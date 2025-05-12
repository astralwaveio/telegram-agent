import re
from functools import partial
from warnings import filterwarnings

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from telegram.warnings import PTBUserWarning

from src.astra.constants import KNOWN_COMMANDS, WEATHER_INPUT, AICHAT_INPUT
from src.astra.handlers.commands import start_command, help_command, tools_command, \
    settings_command, about_command, cancel_service
from src.astra.handlers.messages import aichat_entry, weather_entry, express_entry, news_entry, tools_entry, \
    remind_entry
from src.astra.modules.aichat import aichat_model_selected, aichat_user_input, aichat_type_input
from src.astra.modules.weather import weather_input

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)


chat_type_regex = r"^(ChatGPT|Claude|DeepSeek|Qwen)$"


def register_all_handlers(application):
    """
    注册所有处理器
    """
    register_all_conversations(application)
    register_all_commands(application)
    register_all_messages(application)


def register_all_conversations(application):
    """
    注册「对话」处理器
    :param application:
    """
    # 天气查询对话处理器
    weather_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r"^🌤️\s*天气$"), weather_entry)],
        states={
            WEATHER_INPUT: [
                MessageHandler(filters.LOCATION, weather_input),
                MessageHandler(filters.TEXT & ~filters.COMMAND, weather_input)
            ]
        },
        fallbacks=[CommandHandler('cancel', partial(cancel_service, service_name="天气查询服务"))],
        allow_reentry=True
    )
    application.add_handler(weather_handler)

    # AI对话处理器
    aichat_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex(r"^💬\s*AI对话$"), aichat_entry)],
        states={
            AICHAT_INPUT: [
                MessageHandler(filters.Regex(r"^🤖选择服务$") & ~filters.COMMAND, aichat_type_input),
                MessageHandler(filters.Regex(chat_type_regex) & ~filters.COMMAND, aichat_type_selected),
                MessageHandler(filters.Regex(r"^🤖取消$") & ~filters.COMMAND,
                               partial(cancel_service, service_name="AI对话服务")),
                MessageHandler(filters.TEXT & ~filters.COMMAND, aichat_model_selected),
                MessageHandler(filters.TEXT & ~filters.COMMAND, aichat_user_input),
            ]
        },

        fallbacks=[CommandHandler('cancel', partial(cancel_service, service_name="AI对话服务"))],
        allow_reentry=True
    )
    application.add_handler(aichat_handler)


def register_all_commands(application):
    """
    注册「命令」处理器
    :param application:
    :return:
    """
    # 注册已知命令
    commands = [
        ("start", start_command),
        ("cancel", cancel_service),
        ("tools", tools_command),
        ("help", help_command),
        ("settings", settings_command),
        ("about", about_command),
        # 继续添加其他命令
    ]
    for cmd, func in commands:
        application.add_handler(CommandHandler(cmd, func))

    # 未知命令处理器
    application.add_handler(
        MessageHandler(filters.COMMAND, unknown), group=999
    )


def register_all_messages(application):
    """
    注册「消息」处理器
    :param application:
    """
    button_map = [
        ("📦 快递", express_entry),
        ("📰 新闻", news_entry),
        ("🛠️ 工具", tools_entry),
        ("⏰ 提醒", remind_entry),
    ]
    for msg, func in button_map:
        pattern = r"^" + re.escape(msg) + r"$"
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND & filters.Regex(pattern), func)
        )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    处理未知命令或消息
    """
    # 获取用户输入的命令名
    text = update.message.text
    command = extract_command(text)
    if command in KNOWN_COMMANDS:
        return
    await update.effective_chat.send_message("⚠️输入有误，请按照提示操作，点击 /help 查看帮助。")


def extract_command(text):
    """
    从消息文本中提取命令名，兼容 /cmd、/cmd@botname、/cmd@botname 参数、/cmd 参数
    """
    if not text.startswith("/"):
        return None
    # 取第一个单词（防止有参数）
    first_word = text.split()[0]
    # 去掉开头的 /
    command = first_word[1:]
    # 去掉 @botname
    command = command.split("@")[0]
    return command
