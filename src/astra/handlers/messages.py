from telegram import (
    Update, InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes
)

from src.astra.constants import CHAT_INPUT, EXPRESS_INPUT, NEWS_INPUT, TOOLS_INPUT, REMIND_INPUT, WEATHER_INPUT


# =======================
# 按钮 / 消息处理器
# =======================
async def chat_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 智能对话功能正在开发中，敬请期待！")
    return CHAT_INPUT


async def weather_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    popular_cities = ["杭州富阳", "杭州西湖", "上海", "漯河市"]
    keyboard = [[InlineKeyboardButton(city, callback_data=f"weather_{city}")] for city in popular_cities]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("点击热门城市 / 手动输入：", reply_markup=reply_markup)
    return WEATHER_INPUT


async def express_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 快递查询功能正在开发中，敬请期待！")
    return EXPRESS_INPUT


async def news_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 新闻资讯功能正在开发中，敬请期待！")
    return NEWS_INPUT


async def tools_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 工具箱功能正在开发中，敬请期待！")
    return TOOLS_INPUT


async def remind_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 任务提醒功能正在开发中，敬请期待！")
    return REMIND_INPUT
