from telegram import ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ConversationHandler

from src.astra.constants import AICHAT_INPUT


async def aichat_input(update, context):
    return ConversationHandler.END


async def aichat_chatgpt_input(update, context):
    # 构建 ChatGPT 模型选择键盘
    models_keyboard = [
        [
            KeyboardButton("🤖4.1"),
            KeyboardButton("🤖4o"),
            KeyboardButton("🤖o3"),
            KeyboardButton("返回主菜单"),
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(models_keyboard, one_time_keyboard=True, resize_keyboard=True)
    # 发送模型选择消息
    await update.effective_chat.send_message(
        "<b>您选择了 ChatGPT 聊天类型，请选择支持的模型：</b>", parse_mode="HTML",
        reply_markup=reply_markup
    )
    return AICHAT_INPUT


async def aichat_claude_input(update, context):
    models_keyboard = [
        [
            KeyboardButton("🤖3-7-sonnet"),
            KeyboardButton("🤖3-5-haiku"),
            KeyboardButton("返回主菜单"),
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(models_keyboard, one_time_keyboard=True, resize_keyboard=True)
    # 发送模型选择消息
    await update.effective_chat.send_message(
        "<b>您选择了 Claude 聊天类型，请选择支持的模型：</b>", parse_mode="HTML",
        reply_markup=reply_markup
    )
    return AICHAT_INPUT


async def aichat_deepseek_input(update, context):
    # 构建 DeepSeek 模型选择键盘
    models_keyboard = [
        [
            KeyboardButton("🤖DeepSeek-V1"),
            KeyboardButton("🤖DeepSeek-V2"),
            KeyboardButton("返回主菜单"),
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(models_keyboard, one_time_keyboard=True, resize_keyboard=True)
    # 发送模型选择消息
    await update.effective_chat.send_message(
        "<b>您选择了 DeepSeek 聊天类型，请选择支持的模型：</b>", parse_mode="HTML",
        reply_markup=reply_markup
    )
    return AICHAT_INPUT


async def aichat_qwen_input(update, context):
    # 构建 Qwen 模型选择键盘
    models_keyboard = [
        [
            KeyboardButton("🤖Qwen-7B"),
            KeyboardButton("🤖Qwen-14B"),
            KeyboardButton("返回主菜单"),
        ]
    ]
    reply_markup = ReplyKeyboardMarkup(models_keyboard, one_time_keyboard=True, resize_keyboard=True)
    # 发送模型选择消息
    await update.effective_chat.send_message(
        "<b>您选择了 Qwen 聊天类型，请选择支持的模型：</b>", parse_mode="HTML",
        reply_markup=reply_markup
    )
    return AICHAT_INPUT
