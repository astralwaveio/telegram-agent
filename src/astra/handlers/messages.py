import logging

from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup)
from telegram.ext import (ContextTypes, CallbackContext)

from src.astra.constants import AICHAT_INPUT, EXPRESS_INPUT, NEWS_INPUT, TOOLS_INPUT, REMIND_INPUT, WEATHER_INPUT

logger = logging.getLogger("message")


# =======================
# 按钮 / 消息处理器
# =======================
async def aichat_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 回复用户，提示发送位置或输入城市名
    type_keyboard = [
        [
            KeyboardButton("🤖选择服务"),
        ],
    ]
    reply_markup = ReplyKeyboardMarkup(type_keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.effective_chat.send_message(
        "请选择对话类型：",
        reply_markup=reply_markup
    )
    return AICHAT_INPUT


# 天气入口
async def weather_entry(update: Update, context: CallbackContext):
    # 回复用户，提示发送位置或输入城市名
    keyboard = [
        [
            KeyboardButton("发送当前位置", request_location=True),
            KeyboardButton("杭州市西湖区"),
            KeyboardButton("杭州市富阳区"),
        ],
        [
            KeyboardButton("河南省漯河市"),
            KeyboardButton("香港特别行政区"),
            KeyboardButton("取消天气查询"),
        ],
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.effective_chat.send_message(
        "请发送你的位置，或直接输入城市/区县名称（如“杭州市西湖区”）：",
        reply_markup=reply_markup
    )
    return WEATHER_INPUT


async def express_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("🚧 快递查询功能正在开发中，敬请期待！")
    return EXPRESS_INPUT


# 新闻入口
async def news_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("返回主菜单", callback_data="news_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.effective_chat.send_message(
        "📰 <b>新闻资讯</b>\n\n🚧 该功能正在开发中，敬请期待！",
        parse_mode="HTML",
        reply_markup=reply_markup
    )
    return NEWS_INPUT


async def tools_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("🚧 工具箱功能正在开发中，敬请期待！")
    return TOOLS_INPUT


async def remind_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("🚧 任务提醒功能正在开发中，敬请期待！")
    return REMIND_INPUT
