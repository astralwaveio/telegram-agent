# 常量定义

from src.astra.config import settings

SUPPORTED_MODELS = ["openai", "claude", "deepseek", "qwen"]

# =======================
# 底部按钮配置
# =======================
MAIN_KEYBOARD = settings.get("bot.keyboards")
WEATHER_INPUT, AICHAT_INPUT, EXPRESS_INPUT, NEWS_INPUT, TOOLS_INPUT, REMIND_INPUT = range(6)

# 主菜单按钮

# =======================
# 菜单命令
# =======================
KNOWN_COMMANDS = {"start", "help", "news", "remind", "tools", "cancel", "settings", "about"}

# =======================
# 其他
# =======================
