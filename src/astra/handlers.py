import os

import httpx
from telegram import (
    Update, BotCommand, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ContextTypes, ConversationHandler
)

from src.astra.config import settings
from src.astra.modules.errors import CityNotFoundError, CityAmbiguousError
from src.astra.modules.weather import WeatherCityResolver
from src.astra.register import KNOWN_COMMANDS

# =======================
# 状态常量
# =======================
(
    CHAT_INPUT, WEATHER_INPUT, EXPRESS_INPUT,
    NEWS_INPUT, TOOLS_INPUT, REMIND_INPUT
) = range(6)

# =======================
# 主界面自定义键盘
# =======================
keyboards = settings.get("keyboards.rows", default=[["💬 聊天", "🌤️ 天气", "📦 快递"], ["📰 新闻", "🛠️ 工具", "⏰ 提醒"]])
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    [[KeyboardButton(text) for text in row] for row in keyboards],
    resize_keyboard=True
)


# =======================
# 机器人命令设置
# =======================
async def set_commands(application):
    commands = [
        BotCommand("start", "开始"),
        BotCommand("help", "帮助"),
        BotCommand("news", "新闻资讯"),
        BotCommand("remind", "任务管理"),
        BotCommand("tools", "开发工具箱"),
        BotCommand("cancel", "取消当前操作"),
        BotCommand("settings", "系统设置"),
        BotCommand("about", "关于Astra"),
    ]
    await application.bot.set_my_commands(commands)


# =======================
# 命令 Handler
# =======================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_info = await context.bot.get_me()
    print(f"当前用户名：@{bot_info.username} (ID: {bot_info.id})")
    await update.message.reply_text(
        "你好，我是凌云曦(Astra)，你的多AI智能体助理！\n输入 /help 查看功能。",
        reply_markup=MAIN_KEYBOARD
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 欢迎使用凌云曦（Astra）多AI智能体助手！\n\n"
        "🔹 你可以通过底部按钮或命令快速访问各项服务：\n"
        "【主菜单命令】\n"
        "  /start   - 进入主菜单\n"
        "  /help    - 查看帮助信息\n"
        "  /about   - 关于Astra\n"
        "  /settings- 系统设置\n\n"
        "【功能命令】\n"
        "  /news    - 获取新闻资讯\n"
        "  /remind  - 设置任务提醒\n"
        "  /tools   - 开发工具箱\n"
        "  /cancel  - 取消当前操作\n\n"
        "【常用按钮】\n"
        "  💬 聊天   - 智能对话（即将上线）\n"
        "  🌤️ 天气   - 查询天气\n"
        "  📦 快递   - 快递查询\n"
        "  📰 新闻   - 新闻资讯\n"
        "  🛠️ 工具   - 开发工具箱\n"
        "  ⏰ 提醒   - 任务提醒\n\n"
        "【使用示例】\n"
        "  - 查询天气：点击“🌤️ 天气”或直接发送“查天气 北京”\n"
        "  - 查快递：点击“📦 快递”并输入快递单号\n"
        "  - 设置提醒：点击“⏰ 提醒”或使用 /remind\n\n"
        "【常见问题FAQ】\n"
        "  Q: 如何返回主菜单？\n"
        "     A: 发送 /start 或 /cancel\n"
        "  Q: 如何取消当前操作？\n"
        "     A: 发送 /cancel\n"
        "  Q: 机器人有哪些能力？\n"
        "     A: 智能对话、天气、快递、新闻、工具箱等，更多功能持续开发中！\n\n"
        "如有更多问题或建议，请随时发送消息反馈！"
    )


async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 该功能正在开发中，敬请期待！")


async def remind_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 该功能正在开发中，敬请期待！")


async def tools_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 该功能正在开发中，敬请期待！")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ 当前操作已取消，已返回主菜单。",
        reply_markup=MAIN_KEYBOARD
    )
    return ConversationHandler.END


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 该功能正在开发中，敬请期待！")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "我是 👸凌云曦（Astra），你的AI智能助理。😄\n"
        "支持智能对话、新闻资讯、开发工具、生活服务等多种功能。\n"
        "如需帮助，请发送 /help。"
    )


# =======================
# 按钮/消息 Handler
# =======================
async def chat_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚧 智能对话功能正在开发中，敬请期待！")
    return CHAT_INPUT


async def weather_entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    popular_cities = ["杭州富阳", "杭州西湖", "上海", "漯河市"]

    keyboard = [[InlineKeyboardButton(city, callback_data=f"weather_{city}")] for city in popular_cities]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("点击热门城市 OR 手动输入：", reply_markup=reply_markup
                                    )
    return WEATHER_INPUT


async def weather_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city_code = update.message.text.strip()
    try:
        city_code = WeatherCityResolver().resolve(city_code)
    except (CityNotFoundError, CityAmbiguousError) as e:
        await update.message.reply_text(f'{e.message}')
        return WEATHER_INPUT
    city_code_prefixes = (
        "WX", "WW", "WQ", "WR", "Y8", "YB", "Y9", "WP", "WZ", "YC", "WT", "WS", "WM", "WK", "WE",
        "W7", "W6", "W9", "WD", "WJ", "WH", "W5", "TV", "TU", "TY", "WN", "TZ", "VB", "TX", "TW", "Y0"
    )
    if not city_code.startswith(city_code_prefixes):
        await update.message.reply_text("暂不支持该城市，请重新输入。")
        return WEATHER_INPUT

    # 构造请求URL（根据知心天气文档）
    base_url = "https://api.seniverse.com/v3/weather/"

    async with httpx.AsyncClient() as client:
        private_key = os.getenv("XINZHI_PRI_KEY")
        # 查询实时天气
        now_response = await client.get(
            f"{base_url}now.json",
            params={
                "key": private_key,
                "location": city_code,
                "language": "zh-Hans",
                "unit": "c"
            }
        )

        # 查询未来三天天气
        forecast_response = await client.get(
            f"{base_url}daily.json",
            params={
                "key": private_key,
                "location": city_code,
                "language": "zh-Hans",
                "unit": "c",
                "start": 0,
                "days": 3
            }
        )

    # 检查响应状态码
    if now_response.status_code != 200 or forecast_response.status_code != 200:
        await update.message.reply_text("无法获取天气数据，请稍后再试。")
        return ConversationHandler.END

    now_data = now_response.json()["results"][0]["now"]
    forecast_data = forecast_response.json()["results"][0]["daily"]

    # 构建回复内容
    reply_text = (
        f"🌤️ {update.message.text.strip()} 实时天气：\n"
        f"温度：{now_data['temperature']}°C\n"
        f"天气：{now_data['text_day']}\n"
        f"湿度：{now_data['humidity']}%\n"
        f"风速：{now_data['wind_scale']}级 风力：{now_data['wind_direction']}\n\n"

        f"📅 未来三天天气预报：\n"
        f"1. {forecast_data[0]['date']}：{forecast_data[0]['text_day']} / {forecast_data[0]['text_night']}，"
        f"{forecast_data[0]['low']}°C ~ {forecast_data[0]['high']}°C\n"
        f"2. {forecast_data[1]['date']}：{forecast_data[1]['text_day']} / {forecast_data[1]['text_night']}，"
        f"{forecast_data[1]['low']}°C ~ {forecast_data[1]['high']}°C\n"
        f"3. {forecast_data[2]['date']}：{forecast_data[2]['text_day']} / {forecast_data[2]['text_night']}，"
        f"{forecast_data[2]['low']}°C ~ {forecast_data[2]['high']}°C\n"
    )

    await update.message.reply_text(reply_text, reply_markup=MAIN_KEYBOARD)
    return ConversationHandler.END


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


# =======================
# 未知输入 Handler
# =======================
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 获取用户输入的命令名
    text = update.message.text
    command = extract_command(text)
    if command in KNOWN_COMMANDS:
        return
    await update.message.reply_text("⚠️输入有误，请按照提示操作，点击 /help 查看帮助。")


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
