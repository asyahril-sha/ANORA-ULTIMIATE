# command/status.py
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await update.message.reply_text("❌ Tidak ada karakter aktif. Ketik /start")
        return
    
    await update.message.reply_text(
        f"📊 **STATUS**\n\n"
        f"Karakter: {current_reg.get('bot_name')}\n"
        f"Role: {current_reg.get('role')}\n"
        f"User: {current_reg.get('user_name')}",
        parse_mode='HTML'
    )
