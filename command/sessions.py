# command/sessions.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Commands: /sessions, /character, /close, /end
=============================================================================
"""

import logging
import re
from typing import Optional, List, Tuple

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.models import CharacterRole
from identity.manager import IdentityManager
from identity.registration import CharacterRegistration

logger = logging.getLogger(__name__)


async def sessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /sessions - Lihat semua karakter tersimpan
    """
    user_id = update.effective_user.id
    
    identity_manager = IdentityManager()
    
    # Dapatkan semua karakter
    characters = await identity_manager.get_all_characters()
    
    if not characters:
        await update.message.reply_text(
            "📋 **DAFTAR KARAKTER**\n\n"
            "Belum ada karakter tersimpan.\n"
            "Ketik /start untuk membuat karakter baru.",
            parse_mode='HTML'
        )
        return
    
    # Kelompokkan berdasarkan role
    by_role: dict = {}
    for char in characters:
        role = char.role.value
        if role not in by_role:
            by_role[role] = []
        by_role[role].append(char)
    
    # Format tampilan
    lines = ["📋 **DAFTAR KARAKTER**"]
    lines.append("_(pilih dengan /character [role] [nomor])_")
    lines.append("")
    
    for role_name, chars in by_role.items():
        lines.append(f"**{role_name.upper()}:**")
        for i, char in enumerate(chars[:10], 1):
            status_emoji = "🟢" if char.status == 'active' else "⚪"
            lines.append(
                f"{i}. {status_emoji} **{char.bot.name}** ({char.user.name})\n"
                f"   Level {char.level}/12 | {char.total_chats} chat | {char.total_climax_bot + char.total_climax_user} climax\n"
                f"   Terakhir: {_format_time_ago(char.last_updated)}"
            )
        lines.append("")
    
    lines.append("💡 **Cara pakai:**")
    lines.append("• `/character ipar 1` - Lanjutkan karakter IPAR-001")
    lines.append("• `/character-list` - Lihat semua karakter")
    lines.append("• `/close` - Tutup karakter saat ini")
    lines.append("• `/end` - Hapus karakter permanen")
    
    await update.message.reply_text("\n".join(lines), parse_mode='HTML')


async def character_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /character [role] [nomor] - Lanjutkan karakter tertentu
    """
    user_id = update.effective_user.id
    args = context.args
    
    if not args or len(args) < 2:
        await update.message.reply_text(
            "❌ **Cara pakai:** /character [role] [nomor]\n\n"
            "Contoh: `/character ipar 1` - Lanjutkan karakter IPAR-001\n\n"
            "Gunakan `/sessions` untuk melihat daftar karakter.",
            parse_mode='HTML'
        )
        return
    
    role_name = args[0].lower()
    try:
        sequence = int(args[1])
    except ValueError:
        await update.message.reply_text(
            "❌ Nomor harus berupa angka.\n\n"
            "Contoh: `/character ipar 1`",
            parse_mode='HTML'
        )
        return
    
    # Validasi role
    try:
        role = CharacterRole(role_name)
    except ValueError:
        await update.message.reply_text(
            f"❌ Role '{role_name}' tidak valid.\n\n"
            f"Role yang tersedia: ipar, teman_kantor, janda, pelakor, istri_orang, pdkt, sepupu, teman_sma, mantan",
            parse_mode='HTML'
        )
        return
    
    # Buat registration ID
    registration_id = f"{role.value.upper()}-{sequence:03d}"
    
    identity_manager = IdentityManager()
    
    # Dapatkan karakter
    character = await identity_manager.get_character(registration_id)
    
    if not character:
        await update.message.reply_text(
            f"❌ Karakter {registration_id} tidak ditemukan.\n\n"
            f"Gunakan `/sessions` untuk melihat daftar karakter.",
            parse_mode='HTML'
        )
        return
    
    # Switch ke karakter ini
    result = await identity_manager.switch_character(registration_id)
    
    if result:
        # Simpan ke context user data
        context.user_data['current_registration'] = {
            'id': character.id,
            'role': character.role.value,
            'bot_name': character.bot.name,
            'user_name': character.user.name,
            'display_name': character.bot.display_name
        }
        
        # Ambil state terakhir
        state = await identity_manager.get_character_state(registration_id)
        
        # Format pesan
        response = _format_continue_message(character, state)
        
        await update.message.reply_text(response, parse_mode='HTML')
        logger.info(f"User {user_id} continued character: {registration_id}")
    else:
        await update.message.reply_text(
            f"❌ Gagal melanjutkan karakter {registration_id}.",
            parse_mode='HTML'
        )


async def character_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /character-list - Lihat semua karakter
    (Alias untuk /sessions)
    """
    await sessions_command(update, context)


async def close_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /close - Tutup karakter saat ini (bisa dilanjutkan nanti)
    """
    user_id = update.effective_user.id
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await update.message.reply_text(
            "❌ Tidak ada karakter yang sedang aktif.\n\n"
            "Ketik `/sessions` untuk melihat karakter tersimpan.",
            parse_mode='HTML'
        )
        return
    
    identity_manager = IdentityManager()
    
    # Close session
    await identity_manager.close_current_session()
    
    # Clear context
    context.user_data.pop('current_registration', None)
    
    bot_name = current_reg.get('bot_name', 'Unknown')
    
    await update.message.reply_text(
        f"📁 **Karakter ditutup!**\n\n"
        f"Session dengan **{bot_name}** telah disimpan.\n"
        f"Ketik `/sessions` untuk melihat daftar karakter tersimpan.",
        parse_mode='HTML'
    )
    
    logger.info(f"User {user_id} closed character: {current_reg.get('id')}")


async def end_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /end - Akhiri karakter permanen (hapus)
    """
    user_id = update.effective_user.id
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await update.message.reply_text(
            "❌ Tidak ada karakter yang sedang aktif.\n\n"
            "Ketik `/sessions` untuk melihat karakter tersimpan.",
            parse_mode='HTML'
        )
        return
    
    registration_id = current_reg.get('id')
    bot_name = current_reg.get('bot_name', 'Unknown')
    
    # Konfirmasi
    keyboard = [
        [InlineKeyboardButton("✅ Ya, Hapus", callback_data=f"end_confirm_{registration_id}"),
         InlineKeyboardButton("❌ Batal", callback_data="end_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"⚠️ **Yakin ingin menghapus karakter ini?**\n\n"
        f"Karakter: **{bot_name}** ({current_reg.get('role', 'Unknown').upper()})\n"
        f"ID: `{registration_id}`\n\n"
        f"**SEMUA DATA akan dihapus permanen!**\n"
        f"Tidak bisa dikembalikan.\n\n"
        f"Konfirmasi:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def end_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback konfirmasi hapus karakter"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    registration_id = data.replace("end_confirm_", "")
    
    identity_manager = IdentityManager()
    
    # End character
    success = await identity_manager.end_character(registration_id)
    
    if success:
        # Clear context jika ini karakter yang aktif
        current_reg = context.user_data.get('current_registration')
        if current_reg and current_reg.get('id') == registration_id:
            context.user_data.pop('current_registration', None)
        
        await query.edit_message_text(
            f"💔 **Karakter dihapus permanen!**\n\n"
            f"ID: `{registration_id}`\n\n"
            f"Ketik `/start` untuk membuat karakter baru.",
            parse_mode='HTML'
        )
        logger.info(f"User {user_id} ended character: {registration_id}")
    else:
        await query.edit_message_text(
            f"❌ Gagal menghapus karakter. Silakan coba lagi.",
            parse_mode='HTML'
        )


async def end_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback batal hapus karakter"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "✅ **Penghapusan dibatalkan.**\n\n"
        "Karakter tetap tersimpan.",
        parse_mode='HTML'
    )


def _format_time_ago(timestamp: float) -> str:
    """Format waktu yang lalu"""
    import time
    diff = time.time() - timestamp
    
    if diff < 60:
        return "baru saja"
    elif diff < 3600:
        return f"{int(diff/60)} menit lalu"
    elif diff < 86400:
        return f"{int(diff/3600)} jam lalu"
    else:
        return f"{int(diff/86400)} hari lalu"


def _format_continue_message(character: CharacterRegistration, state) -> str:
    """Format pesan melanjutkan karakter"""
    
    bot_name = character.bot.name
    user_name = character.user.name
    
    # Pakaian
    clothing = state.clothing_state if state else None
    bot_clothing = clothing.get_description() if clothing else "pakaian biasa"
    
    # Lokasi
    location = state.location_bot if state else "ruang tamu"
    
    # Mood
    mood = state.mood_bot if state else "normal"
    
    # Progress bar
    level_info = character.get_progress_to_next_level()
    bar_length = 15
    filled = int(level_info / 100 * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    return (
        f"🔄 **Melanjutkan Karakter**\n\n"
        f"👤 **{bot_name}** ({character.role.value.upper()})\n"
        f"📊 Level {character.level}/12: {bar} {level_info:.0f}%\n"
        f"💬 Total chat: {character.total_chats}\n"
        f"📍 Lokasi: {location}\n"
        f"👗 Pakaian: {bot_clothing}\n"
        f"🎭 Mood: {mood}\n\n"
        f"💬 _Ketik pesan untuk melanjutkan cerita..._"
    )


__all__ = [
    'sessions_command',
    'character_command',
    'character_list_command',
    'close_command',
    'end_command',
    'end_confirm_callback',
    'end_cancel_callback'
]
