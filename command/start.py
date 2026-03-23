# command/start.py
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from database.models import CharacterRole
from identity.manager import IdentityManager

logger = logging.getLogger(__name__)
SELECTING_ROLE = 1


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("START_COMMAND CALLED")
    
    keyboard = [
        [InlineKeyboardButton("👩 Ipar", callback_data="role_ipar"),
         InlineKeyboardButton("👩‍💼 Teman Kantor", callback_data="role_teman_kantor")],
        [InlineKeyboardButton("👩 Janda", callback_data="role_janda"),
         InlineKeyboardButton("💃 Pelakor", callback_data="role_pelakor")],
        [InlineKeyboardButton("👰 Istri Orang", callback_data="role_istri_orang"),
         InlineKeyboardButton("💕 PDKT", callback_data="role_pdkt")],
        [InlineKeyboardButton("👧 Sepupu", callback_data="role_sepupu"),
         InlineKeyboardButton("👩‍🎓 Teman SMA", callback_data="role_teman_sma")],
        [InlineKeyboardButton("💔 Mantan", callback_data="role_mantan")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💕 **Pilih Karakter:**",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    return SELECTING_ROLE


async def role_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    role_name = query.data.replace("role_", "")
    role = CharacterRole(role_name)
    
    manager = IdentityManager()
    registration = await manager.create_character(role)
    
    context.user_data['current_registration'] = {
        'id': registration.id,
        'role': registration.role.value,
        'bot_name': registration.bot.name,
        'user_name': registration.user.name,
    }
    
    await query.edit_message_text(
        f"💕 **Halo {registration.user.name}!**\n\n"
        f"Aku **{registration.bot.name}**, {registration.role.value.upper()} mu.\n\n"
        f"💬 Ayo mulai ngobrol!",
        parse_mode='HTML'
    )
    return ConversationHandler.END


async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("❌ Dibatalkan.")
    return ConversationHandler.END


__all__ = ['start_command', 'SELECTING_ROLE', 'role_callback', 'cancel_callback']
