import logging
import os
import sys

from dotenv import load_dotenv
from telegram.ext import Application

from .config import settings
from .handlers import set_commands
from .register import register_all_handlers, register_all_messages


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
        application = Application.builder().token(token).post_init(set_commands).build()

        # 设置命令菜单
        application.post_init(set_commands)

        # 注册命令
        register_all_handlers(application)

        # 注册消息
        register_all_messages(application)

        # 启动Bot
        logger.info(f"{settings.get("bot.nick_name")} 正在等待消息... 按 Ctrl+C 退出。")
        application.run_polling()
    except Exception as e:
        logger.error(f"Bot 启动失败: {e}")
        sys.exit(2)
    finally:
        logger.info("Bot 已关闭。")
