# command/cancel.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Command: /cancel - Batalkan Percakapan & Proses yang Sedang Berlangsung
Target Realism 9.9/10
=============================================================================
"""

import logging
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler

from identity.manager import IdentityManager

logger = logging.getLogger(__name__)


# Conversation states
CANCEL_CONFIRM = 1


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handler untuk /cancel - Batalkan percakapan atau proses yang sedang berlangsung
    """
    user_id = update.effective_user.id
    user = update.effective_user
    
    logger.info(f"User {user_id} ({user.first_name}) triggered /cancel")
    
    # Cek apakah ada karakter aktif
    current_reg = context.user_data.get('current_registration')
    
    # Cek apakah ada proses conversation yang sedang berlangsung
    if context.user_data.get('in_conversation'):
        keyboard = [
            [InlineKeyboardButton("✅ Ya, Batalkan", callback_data="cancel_confirm_conv"),
             InlineKeyboardButton("❌ Tidak, Lanjutkan", callback_data="cancel_keep")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "⚠️ **Konfirmasi Pembatalan**\n\n"
            "Ada proses yang sedang berlangsung.\n"
            "Yakin ingin membatalkannya?\n\n"
            "Semua progress yang belum disimpan akan hilang.",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
        return CANCEL_CONFIRM
    
    # Jika ada karakter aktif
    if current_reg:
        bot_name = current_reg.get('bot_name', 'Bot')
        
        keyboard = [
            [InlineKeyboardButton("✅ Ya, Batalkan", callback_data="cancel_confirm_char"),
             InlineKeyboardButton("❌ Tidak", callback_data="cancel_keep")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"⚠️ **Konfirmasi Pembatalan**\n\n"
            f"Kamu sedang dalam percakapan dengan **{bot_name}**.\n\n"
            f"Jika dibatalkan, percakapan saat ini akan dihentikan.\n"
            f"Karakter tetap tersimpan, kamu bisa melanjutkan nanti dengan `/sessions`.\n\n"
            f"**Yakin ingin membatalkan?**",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        
        return CANCEL_CONFIRM
    
    # Tidak ada karakter aktif dan tidak ada conversation
    await update.message.reply_text(
        "❌ **Tidak ada yang dibatalkan**\n\n"
        "Tidak ada percakapan atau proses yang sedang berlangsung.\n\n"
        "Ketik `/start` untuk memulai karakter baru, atau `/sessions` untuk melanjutkan karakter tersimpan.",
        parse_mode='HTML'
    )
    
    return ConversationHandler.END


async def cancel_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Callback untuk konfirmasi pembatalan
    """
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    if data == "cancel_confirm_conv":
        # Batalkan conversation
        context.user_data.pop('in_conversation', None)
        context.user_data.pop('conversation_data', None)
        context.user_data.pop('pending_action', None)
        context.user_data.pop('pending_state', None)
        
        await query.edit_message_text(
            "✅ **Percakapan dibatalkan**\n\n"
            "Proses yang sedang berlangsung telah dibatalkan.\n\n"
            "Ketik pesan untuk memulai lagi.",
            parse_mode='HTML'
        )
        
        logger.info(f"User {user_id} cancelled conversation")
        
    elif data == "cancel_confirm_char":
        # Batalkan karakter aktif (close session)
        current_reg = context.user_data.get('current_registration')
        
        if current_reg:
            bot_name = current_reg.get('bot_name', 'Bot')
            registration_id = current_reg.get('id')
            
            identity_manager = IdentityManager()
            
            # Close session
            await identity_manager.close_current_session()
            
            # Clear context
            context.user_data.pop('current_registration', None)
            context.user_data.pop('pending_action', None)
            context.user_data.pop('pending_state', None)
            
            await query.edit_message_text(
                f"✅ **Percakapan dengan {bot_name} dibatalkan**\n\n"
                f"Karakter telah disimpan.\n"
                f"Ketik `/sessions` untuk melihat karakter tersimpan.\n"
                f"Ketik `/start` untuk membuat karakter baru.",
                parse_mode='HTML'
            )
            
            logger.info(f"User {user_id} cancelled character session: {registration_id}")
        else:
            await query.edit_message_text(
                "❌ **Tidak ada karakter aktif**\n\n"
                "Ketik `/start` untuk memulai.",
                parse_mode='HTML'
            )
    
    elif data == "cancel_keep":
        # Lanjutkan tanpa membatalkan
        await query.edit_message_text(
            "✅ **Dilanjutkan**\n\n"
            "Percakapan tetap berjalan.\n"
            "Ketik pesan untuk melanjutkan.",
            parse_mode='HTML'
        )
    
    elif data == "cancel_back":
        await query.edit_message_text(
            "🔙 **Kembali**\n\n"
            "Ketik pesan untuk melanjutkan.",
            parse_mode='HTML'
        )
    
    return ConversationHandler.END


async def cancel_fallback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Fallback handler untuk cancel conversation
    """
    await update.message.reply_text(
        "❌ **Dibatalkan**\n\n"
        "Percakapan dibatalkan.\n\n"
        "Ketik pesan untuk memulai lagi.",
        parse_mode='HTML'
    )
    
    return ConversationHandler.END


__all__ = [
    'cancel_command',
    'cancel_confirm_callback',
    'cancel_fallback',
    'CANCEL_CONFIRM',
]
