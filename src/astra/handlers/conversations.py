from warnings import filterwarnings

from telegram.ext import (
    ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
)
from telegram.warnings import PTBUserWarning

from src.astra.handlers.messages import weather_entry, WEATHER_INPUT
from src.astra.modules.weather import weather_button, cancel, weather_query

filterwarnings(action="ignore", message=r".*CallbackQueryHandler", category=PTBUserWarning)

# 天气查询对话状态
weather_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("weather", weather_entry),  # 传统命令入口
        MessageHandler(filters.Regex(r"^🌤️\s*天气$"), weather_entry),  # 支持“🌤️ 天气”文本入口
    ],
    states={
        WEATHER_INPUT: [
            CallbackQueryHandler(weather_button, pattern=r".*"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, weather_query),
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
    per_message=True,

)
