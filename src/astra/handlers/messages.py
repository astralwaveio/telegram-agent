import logging

from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup)
from telegram.ext import (ContextTypes, CallbackContext)

from src.astra.constants import CHAT_INPUT, EXPRESS_INPUT, NEWS_INPUT, TOOLS_INPUT, REMIND_INPUT, WEATHER_INPUT
from src.astra.modules.weather import caiyun_client

logger = logging.getLogger("message")


def location_handler(update: Update, context: CallbackContext):
    if update.message.location:
        lat = update.message.location.latitude
        lng = update.message.location.longitude
        # 这里调用你的天气查询服务
        weather = caiyun_client.query("weather", (lng, lat))
        update.message.reply_text(f"你当前位置的天气：{weather}")
    else:
        update.message.reply_text("请发送你的位置。")


# =======================
# 按钮 / 消息处理器
# =======================
async def aichat_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("🚧 智能对话功能正在开发中，敬请期待！")
    return CHAT_INPUT


# 天气入口
async def weather_entry(update: Update, context: CallbackContext):
    # 回复用户，提示发送位置或输入城市名
    keyboard = [
        [
            KeyboardButton("取消天气查询"),
            KeyboardButton("发送当前位置", request_location=True),
            KeyboardButton("杭州市西湖区"),
        ],
        [
            KeyboardButton("杭州市富阳区"),
            KeyboardButton("河南省漯河市"),
            KeyboardButton("香港特别行政区"),
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
