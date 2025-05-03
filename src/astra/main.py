import logging
import os
import sys

from dotenv import load_dotenv
from telegram.ext import Application

from .handlers import set_bot_menu
from .register import register_all_handlers


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
        # 创建Bot应用
        app = Application.builder().token(token).post_init(set_bot_menu).build()

        # 注册命令
        register_all_handlers(app)

        # 启动Bot
        logger.info("凌云曦(Astra) Telegram Bot 正在等待消息... 按 Ctrl+C 退出。")
        app.run_polling()
    except Exception as e:
        logger.error(f"Bot 启动失败: {e}")
        sys.exit(2)
    finally:
        logger.info("Bot 已关闭。")
