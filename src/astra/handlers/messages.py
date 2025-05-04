import logging

from telegram import (
    Update, InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes
)

from src.astra.constants import CHAT_INPUT, EXPRESS_INPUT, NEWS_INPUT, TOOLS_INPUT, REMIND_INPUT, WEATHER_INPUT, \
    WEATHER_DEFAULT_CITIES

logger = logging.getLogger("message")


# =======================
# 按钮 / 消息处理器
# =======================
async def chat_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("🚧 智能对话功能正在开发中，敬请期待！")
    return CHAT_INPUT


async def weather_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """对话入口，提示用户输入城市或选择常用城市"""
    city_buttons = [InlineKeyboardButton(name, callback_data=cb) for name, cb in WEATHER_DEFAULT_CITIES]
    keyboard = [city_buttons[i:i + 3] for i in range(0, len(city_buttons), 3)]
    keyboard.append([InlineKeyboardButton("🔙 返回", callback_data="weather_cancel")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = (
        "🌤️ <b>欢迎使用天气查询助手</b>\n\n"
        "📖 请输入你想查询的 <b>城市名</b>，或直接点击下方常用城市按钮。⏬\n\n"
        "如需退出，请点击下方 “🔙 返回” 按钮即可。"
    )
    await update.effective_chat.send_message(
        msg,
        reply_markup=reply_markup,
        parse_mode="HTML"
    )
    return WEATHER_INPUT


async def express_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("🚧 快递查询功能正在开发中，敬请期待！")
    return EXPRESS_INPUT


async def news_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("🚧 新闻资讯功能正在开发中，敬请期待！")
    return NEWS_INPUT


async def tools_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("🚧 工具箱功能正在开发中，敬请期待！")
    return TOOLS_INPUT


async def remind_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("🚧 任务提醒功能正在开发中，敬请期待！")
    return REMIND_INPUT
