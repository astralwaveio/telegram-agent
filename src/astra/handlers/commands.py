from telegram import (
    Update, BotCommand, ReplyKeyboardMarkup
)
from telegram.ext import (
    ContextTypes, ConversationHandler
)

from src.astra.constants import MAIN_KEYBOARD


# =======================
# 机器人常用菜单命令设置
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
    await update.effective_chat.send_message(
        "你好，我是凌云曦(Astra)，你的多AI智能体助理！\n输入 /help 查看功能。",
        reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message(
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
    await update.effective_chat.send_message("🚧 该功能正在开发中，敬请期待！")


async def remind_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("🚧 该功能正在开发中，敬请期待！")


async def tools_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("🚧 该功能正在开发中，敬请期待！")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message(
        "🏠 已返回主菜单。",
        reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
    )
    return ConversationHandler.END


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("🚧 该功能正在开发中，敬请期待！")


async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message(
        "我是 👸凌云曦（Astra），你的AI智能助理。😄\n"
        "支持智能对话、新闻资讯、开发工具、生活服务等多种功能。\n"
        "如需帮助，请发送 /help。"
    )
