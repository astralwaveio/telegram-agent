from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler, ContextTypes

from src.astra.constants import MAIN_KEYBOARD


async def aichat_input(update, context):
    return ConversationHandler.END


async def aichat_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.effective_chat.send_message("<b>已取消AI聊天</b>，期待下次为您服务！", parse_mode="HTML",
                                             reply_markup=ReplyKeyboardMarkup(MAIN_KEYBOARD, resize_keyboard=True))
    return ConversationHandler.END
