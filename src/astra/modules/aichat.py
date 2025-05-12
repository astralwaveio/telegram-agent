import asyncio
import os

import aiohttp
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ConversationHandler, ContextTypes

from src.astra.constants import AICHAT_INPUT, MODEL_CONFIG, MODEL_PROMPTS

# 聊天类型与模型映射
MODEL_TYPE_MAP = {
    "ChatGPT": "ChatGPT",
    "Claude": "Claude",
    "DeepSeek": "DeepSeek",
    "Qwen": "Qwen",
}


# 生成模型选择键盘
def build_model_keyboard(model_type):
    models = MODEL_CONFIG.get(model_type, [])
    keyboard = []
    row = []
    for idx, (model, desc) in enumerate(models):
        row.append(KeyboardButton(model))
        # 每行最多2个按钮
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    keyboard.append([KeyboardButton("返回主菜单")])
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)


# 聊天类型入口函数
async def aichat_type_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 这里假设你有主菜单选择不同聊天类型的入口
    # 用户选择后会调用对应的模型选择函数
    pass  # 由你的主菜单逻辑决定


# 统一的模型选择入口
async def aichat_model_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 获取用户选择的聊天类型
    chat_type = context.user_data.get("chat_type")
    if not chat_type or chat_type not in MODEL_CONFIG:
        await update.effective_chat.send_message("请选择有效的聊天类型。")
        return ConversationHandler.END
    reply_markup = build_model_keyboard(chat_type)
    await update.effective_chat.send_message(
        f"<b>您选择了 {chat_type} 聊天类型，请选择支持的模型：</b>", parse_mode="HTML",
        reply_markup=reply_markup
    )
    return AICHAT_INPUT


# 处理模型选择
async def aichat_model_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    model = update.message.text
    chat_type = context.user_data.get("chat_type")
    valid_models = [m[0] for m in MODEL_CONFIG.get(chat_type, [])]
    if model == "返回主菜单":
        await update.effective_chat.send_message("已返回主菜单。")
        return ConversationHandler.END
    if model not in valid_models:
        await update.effective_chat.send_message("请选择列表中的模型。")
        return AICHAT_INPUT
    context.user_data['selected_model'] = model
    await update.effective_chat.send_message(
        f"您已选择模型：<b>{model}</b>，请输入您的问题：", parse_mode="HTML"
    )
    # 进入用户输入问题的状态
    return AICHAT_INPUT


# 处理用户输入问题
async def aichat_user_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_question = update.message.text.strip()
    model = context.user_data.get('selected_model')
    chat_type = context.user_data.get('chat_type')

    # 支持随时返回主菜单
    if user_question == "返回主菜单":
        await update.effective_chat.send_message("已返回主菜单。")
        return ConversationHandler.END

    # 支持随时取消
    if user_question.lower() in ["/cancel", "取消"]:
        await update.effective_chat.send_message("会话已取消。")
        return ConversationHandler.END

    if not model:
        await update.effective_chat.send_message("请先选择模型。")
        return AICHAT_INPUT

    # 调用实际AI接口（伪代码，需替换为你自己的API调用）
    try:
        # 这里假设你有一个异步函数 call_ai_api(model, user_question, context)
        ai_reply = await call_ai_api(model, user_question, context)
    except Exception as e:
        await update.effective_chat.send_message(f"AI接口调用失败：{e}")
        return AICHAT_INPUT

    # 回复用户
    await update.effective_chat.send_message(ai_reply)

    # 继续保持在AICHAT_INPUT状态，允许继续提问或切换模型
    return AICHAT_INPUT


# 示例AI接口调用函数（你需要实现自己的逻辑）
async def call_ai_api(model, user_question, context):
    """
    通用AI接口调用方法，根据模型名称自动路由到不同的后端API。
    自动加上合适的中文system prompt。
    """
    # 获取历史对话（如有）
    history = context.user_data.get('history', [])
    system_prompt = MODEL_PROMPTS.get(model, "请用中文回答用户问题。")
    # 构造消息格式
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_question})
    # 根据模型名称路由
    if model in ["gpt-4.1", "gpt-4.1-mini", "o3", "o4-mini"]:
        # Azure OpenAI
        ai_reply = await call_openai_azure(model, user_question, history)
    elif model in ["deepseek-chat", "deepseek-reasoner"]:
        # DeepSeek
        ai_reply = await call_deepseek(model, user_question, history)
    # elif model in ["claude-3-7-sonnet-latest", "claude-3-5-haiku-latest"]:
    #     # Claude
    #     ai_reply = await call_claude(model, user_question, history)
    # elif model.startswith("qwen"):
    #     # Qwen
    #     ai_reply = await call_qwen(model, user_question, history)
    else:
        # 未知模型，返回默认提示
        ai_reply = f"暂不支持该模型：{model}，你的问题是：{user_question}"
    # 更新历史
    history.append({"role": "user", "content": user_question})
    history.append({"role": "assistant", "content": ai_reply})
    context.user_data['history'] = history
    return ai_reply


# 初始化Azure OpenAI客户端
async def call_openai_azure(model, user_question, history=None):
    """
    调用Azure OpenAI接口，返回中文回复
    """
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
    # 由于SDK为同步，需用asyncio.to_thread
    response = await asyncio.to_thread(client.complete, payload)
    return response.choices[0].message.content


async def call_deepseek(model, user_question, history=None):
    """
    调用DeepSeek接口，返回中文回复
    """
    system_prompt = MODEL_PROMPTS.get(model, "请用中文回答用户问题。")
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_question})

    # 假设DeepSeek API为POST接口，需根据实际API文档调整
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
