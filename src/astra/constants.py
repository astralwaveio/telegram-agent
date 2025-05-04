# 常量定义
from telegram import ReplyKeyboardMarkup, KeyboardButton

from src.astra.config import settings

SUPPORTED_MODELS = ["openai", "claude", "deepseek", "qwen"]

# =======================
# 底部按钮
# =======================
(
    CHAT_INPUT, WEATHER_INPUT, WEATHER_RESULT, EXPRESS_INPUT,
    NEWS_INPUT, TOOLS_INPUT, REMIND_INPUT
) = range(7)

keyboards = settings.get("keyboards.rows", default=[[]])
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton(text) for text in row] for row in keyboards],
    resize_keyboard=True
)

# =======================
# 菜单命令
# =======================
KNOWN_COMMANDS = {
    "start", "help", "news", "remind", "tools", "cancel", "settings", "about"
}
