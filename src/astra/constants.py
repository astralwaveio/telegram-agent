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
# AI模型配置
# =======================
# src/astra/constants.py
MODEL_CONFIG = {
    "ChatGPT": [
        # (模型名, 描述)
        ("gpt-4.1", "全能旗舰：高精度复杂任务（长文档分析、代码生成、专业问答）"),
        ("gpt-4.1-mini", "高效经济：日常任务（客服、文案、快速响应需求）"),
        ("o3", "推理+多模态：数学/科学/图像分析（科研、商业决策）"),
        ("o4-mini", "数学专精：计算密集型任务（数学竞赛、数据分析）"),
    ],
    "Claude": [
        ("claude-3-7-sonnet-latest", "最智能的模型"),
        ("claude-3-5-haiku-latest", "最快的模型"),
    ],
    "DeepSeek": [
        ("deepseek-chat", "通用对话"),
        ("deepseek-reasoner", "推理专长"),
    ],
    "Qwen": [
        ("qwen-max-latest", "全能旗舰：复杂多步骤任务（高精度需求，如深度分析、代码生成）"),
        ("qwen-turbo-latest", "极速低成本：高频轻量任务（客服、简单问答、实时响应）"),
        ("qwen-long-latest", "长文本均衡：超长上下文处理（文档总结、法律/科研文本分析）"),
        ("qwen-omni-turbo-latest", "多模态：图文混合任务（图像理解、跨模态生成）"),
    ],
}

MODEL_PROMPTS = {
    "gpt-4.1": "你是一个全能旗舰AI助手，擅长高精度复杂任务（如长文档分析、代码生成、专业问答）。请用中文详细、专业地回答用户问题。",
    "gpt-4.1-mini": "你是一个高效经济的AI助手，适合日常任务（如客服、文案、快速响应需求）。请用中文简明扼要地回答用户问题。",
    "o3": "你是一个推理和多模态能力强的AI助手，擅长数学、科学和图像分析。请用中文专业地解答用户的推理和分析类问题。",
    "o4-mini": "你是一个数学专精的AI助手，适合计算密集型任务（如数学竞赛、数据分析）。请用中文详细解答数学相关问题。",
    "claude-3-7-sonnet-latest": "你是最智能的AI助手，请用中文详细、智能地回答用户问题。",
    "claude-3-5-haiku-latest": "你是最快的AI助手，请用中文快速、简明地回答用户问题。",
    "deepseek-chat": "你是一个通用对话AI助手，请用中文自然、友好地与用户交流。",
    "deepseek-reasoner": "你是一个推理专长的AI助手，请用中文逻辑清晰地解答用户的推理类问题。",
    "qwen-max-latest": "你是一个全能旗舰AI助手，擅长复杂多步骤任务（如深度分析、代码生成）。请用中文详细、专业地回答用户问题。",
    "qwen-turbo-latest": "你是一个极速低成本AI助手，适合高频轻量任务（如客服、简单问答、实时响应）。请用中文简明扼要地回答用户问题。",
    "qwen-long-latest": "你是一个长文本均衡AI助手，擅长超长上下文处理（如文档总结、法律/科研文本分析）。请用中文对长文本问题进行总结和分析。",
    "qwen-omni-turbo-latest": "你是一个多模态AI助手，擅长图文混合任务（如图像理解、跨模态生成）。请用中文对多模态问题进行解答。",
}

# =======================
# 其他
# =======================
