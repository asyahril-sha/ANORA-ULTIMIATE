# command/help.py
# -*- coding: utf-8 -*-
from telegram import Update
from telegram.ext import ContextTypes

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 **BANTUAN AMORIA**\n\n"
        "/start - Mulai bot\n"
        "/status - Status hubungan\n"
        "/progress - Progress leveling\n"
        "/help - Bantuan ini",
        parse_mode='HTML'
    )
