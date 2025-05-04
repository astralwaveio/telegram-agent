import logging
import os
import sys

from dotenv import load_dotenv
from telegram.ext import Application

from src.astra.handlers.register import register_all_handlers
from .config import settings
from .handlers.commands import set_commands
from .modules.tasks import start_background_tasks


def main():
    # 配置日志
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(message)s",
        level=logging.INFO
    )
    logger = logging.getLogger("astra")

    # 加载环境变量
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    if not token or token.strip() == "" or "your-telegram-bot-token" in token:
        logger.error(
            "未检测到有效的 TELEGRAM_TOKEN！\n"
            "请在项目根目录下的 .env 文件中正确填写 TELEGRAM_TOKEN=你的BotToken。\n"
            "你可以在 https://t.me/BotFather 创建并获取 Bot Token。"
        )
        sys.exit(1)

    try:

        # 创建Bot应用并设置命令菜单
        application = Application.builder().token(token).post_init(set_commands).build()

        # 注册处理器
        register_all_handlers(application)

        # 启动所有后台线程任务
        start_background_tasks(application)

        # 启动Bot
        logger.info(f"✅ Successful! {settings.get("bot.nick_name")} Bot 正在等待消息...")
        application.run_polling()
    except Exception as e:
        logger.error(f"Telegram Bot 启动失败！错误信息：{e}")
        sys.exit(2)
    finally:
        logger.info("Telegram Bot 停止运行。")
