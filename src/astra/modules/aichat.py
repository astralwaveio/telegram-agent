import asyncio
import os
import re

import aiohttp
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ConversationHandler, ContextTypes

from src.astra.constants import AICHAT_INPUT, MODEL_CONFIG, MODEL_PROMPTS, MAIN_KEYBOARD


def build_chat_type_keyboard():
    keyboard = [
        [KeyboardButton("ChatGPT"), KeyboardButton("Claude")],
        [KeyboardButton("DeepSeek"), KeyboardButton("Qwen")],
        [KeyboardButton("主菜单")]
    ]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def build_model_keyboard(model_type):
    models = MODEL_CONFIG.get(model_type, [])
    keyboard = []
    row = []
    for idx, (model, desc) in enumerate(models):
        # 按钮内容：模型名（简短描述）
        btn_text = f"{model}（{desc.split('：')[0]}）" if '：' in desc else f"{model}（{desc}）"
        row.append(KeyboardButton(btn_text))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    # 最后一行加返回主菜单
    keyboard.append([KeyboardButton("主菜单")])
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


def extract_model_name(btn_text):
    # 匹配“模型名（描述）”
    m = re.match(r"^([^（(]+)", btn_text)
    return m.group(1).strip() if m else btn_text


# 只包含返回主菜单的键盘
def build_back_keyboard():
    return ReplyKeyboardMarkup([[KeyboardButton("主菜单")]], resize_keyboard=True, one_time_keyboard=False)


# 统一的模型选择入口

async def aichat_type_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message(
        "请选择聊天类型：",
        reply_markup=build_chat_type_keyboard()
    )
    return AICHAT_INPUT


async def aichat_type_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = update.message.text
    if chat_type == "返回主菜单":
        await update.effective_chat.send_message("已返回主菜单。",
                                                 reply_markup=ReplyKeyboardMarkup([[]], resize_keyboard=True))
        return ConversationHandler.END
    if chat_type not in MODEL_CONFIG:
        await update.effective_chat.send_message(
            "请选择有效的聊天类型。",
            reply_markup=build_chat_type_keyboard(),
        )
        return AICHAT_INPUT
    context.user_data['chat_type'] = chat_type
    # 进入模型选择
    reply_markup = build_model_keyboard(chat_type)
    await update.effective_chat.send_message(
        f"<b>您选择了 {chat_type} 聊天类型，请选择支持的模型：</b>", parse_mode="HTML",
        reply_markup=reply_markup
    )
    return AICHAT_INPUT


async def aichat_model_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_type = context.user_data.get("chat_type")
    if not chat_type or chat_type not in MODEL_CONFIG:
        await update.effective_chat.send_message(
            "请选择有效的聊天类型!",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
        )
        return ConversationHandler.END
    reply_markup = build_model_keyboard(chat_type)
    await update.effective_chat.send_message(
        f"<b>您选择了 {chat_type} 聊天类型，请选择支持的模型：</b>", parse_mode="HTML",
        reply_markup=reply_markup
    )
    return AICHAT_INPUT


async def aichat_model_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btn_text = update.message.text
    model = extract_model_name(btn_text)
    chat_type = context.user_data.get("chat_type")
    valid_models = [m[0] for m in MODEL_CONFIG.get(chat_type, [])]
    if model == "主菜单":
        await update.effective_chat.send_message(
            "已返回主菜单。",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
        )
        return ConversationHandler.END
    if model not in valid_models:
        await update.effective_chat.send_message("请选择列表中的模型。", reply_markup=build_model_keyboard(chat_type))
        return AICHAT_INPUT
    context.user_data['selected_model'] = model
    await update.effective_chat.send_message(
        f"您已选择模型：<b>{model}</b>，请输入您的问题：",
        parse_mode="HTML",
        reply_markup=build_back_keyboard()
    )
    return AICHAT_INPUT


# 处理用户输入问题
async def aichat_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text.strip()
    model = context.user_data.get('selected_model')
    chat_type = context.user_data.get('chat_type')

    # 支持随时返回主菜单
    if user_question == "主菜单":
        await update.effective_chat.send_message(
            "已返回主菜单。",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
        )
        return ConversationHandler.END

    # 支持随时取消
    if user_question.lower() in ["/cancel", "取消"]:
        await update.effective_chat.send_message(
            "会话已取消。",
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True)
        )
        return ConversationHandler.END

    if not model:
        await update.effective_chat.send_message("请先选择模型。", reply_markup=build_model_keyboard(chat_type))
        return AICHAT_INPUT

    # 调用实际AI接口（伪代码，需替换为你自己的API调用）
    try:
        ai_reply = await call_ai_api(model, user_question, context)
    except Exception as e:
        await update.effective_chat.send_message(f"AI接口调用失败：{e}", reply_markup=build_back_keyboard())
        return AICHAT_INPUT

    # 回复用户
    await update.effective_chat.send_message(ai_reply, reply_markup=build_back_keyboard())

    # 继续保持在AICHAT_INPUT状态，允许继续提问或切换模型
    return AICHAT_INPUT


# AI接口调用函数
async def call_ai_api(model, user_question, context):
    history = context.user_data.get('history', [])
    system_prompt = MODEL_PROMPTS.get(model, "请用中文回答用户问题。")
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_question})
    if model in ["gpt-4.1", "gpt-4.1-mini", "o3", "o4-mini"]:
        ai_reply = await call_openai_azure(model, user_question, history)
    elif model in ["deepseek-chat", "deepseek-reasoner"]:
        ai_reply = await call_deepseek(model, user_question, history)
    else:
        ai_reply = f"暂不支持该模型：{model}，你的问题是：{user_question}"
    # 更新历史
    history.append({"role": "user", "content": user_question})
    history.append({"role": "assistant", "content": ai_reply})
    context.user_data['history'] = history
    return ai_reply


# 初始化Azure OpenAI客户端
async def call_openai_azure(model, user_question, history=None):
    api_key = os.getenv("AZURE_INFERENCE_CREDENTIAL", '')
    endpoint = f"https://astralwave.openai.azure.com/openai/deployments/{model}"
    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(api_key),
    )
    system_prompt = MODEL_PROMPTS.get(model, "请用中文回答用户问题。")
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_question})

    payload = {
        "messages": messages,
        "temperature": 1,
        "top_p": 1,
        "stop": [],
        "frequency_penalty": 0,
        "presence_penalty": 0
    }
    response = await asyncio.to_thread(client.complete, payload)
    return response.choices[0].message.content


async def call_deepseek(model, user_question, history=None):
    system_prompt = MODEL_PROMPTS.get(model, "请用中文回答用户问题。")
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_question})

    url = f"https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY', '')}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 1,
        "top_p": 1,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            data = await resp.json()
            return data["choices"][0]["message"]["content"]
