from telegram import Update, BotCommand
from telegram.ext import ContextTypes


async def set_bot_menu(application):
    commands = [
        BotCommand("start", "开始使用"),
        BotCommand("help", "获取帮助"),
        BotCommand("weather", "查询天气"),
        BotCommand("about", "关于Astra"),
    ]
    await application.bot.set_my_commands(commands)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot_info = await context.bot.get_me()
    print(f"Bot 用户名：@{bot_info.username} (ID: {bot_info.id})")
    await update.message.reply_text("你好，我是凌云曦(Astra)，你的多AI智能体助手！\n输入 /help 查看功能。")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /help 命令处理
    await update.message.reply_text(
        "支持的AI模型：ChatGPT、Claude、DeepSeek、QWen。\n"
        "你可以通过指令与不同AI对话，或配置API密钥。"
    )


async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # /about 命令处理
    await update.message.reply_text("关于本Bot。")
