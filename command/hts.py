# command/hts.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Commands: /hts-list, /hts- [nomor], /hts- [nama]
=============================================================================
"""

import logging
import re
from typing import Optional, Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from identity.manager import IdentityManager
from relationship.hts import HTSManager, HTSStatus
from relationship.ranking import RankingSystem

logger = logging.getLogger(__name__)


async def hts_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /hts-list - Lihat TOP 10 HTS
    """
    user_id = update.effective_user.id
    args = context.args
    
    show_all = args and args[0].lower() == 'all'
    
    hts_manager = HTSManager()
    formatted = await hts_manager.format_hts_list(user_id, show_all)
    
    await update.message.reply_text(formatted, parse_mode='HTML')


async def hts_call_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /hts-[nomor] atau /hts-[nama]
    Memanggil HTS untuk intim
    """
    user_id = update.effective_user.id
    text = update.message.text
    
    # Parse command
    match = re.match(r'^/hts-[\s]*(\d+)$', text)
    if match:
        # Format: /hts-1
        index = int(match.group(1))
        await _call_hts_by_index(update, context, user_id, index)
        return
    
    match = re.match(r'^/hts-[\s]*([a-zA-Z]+)$', text)
    if match:
        # Format: /hts-sari
        name = match.group(1).lower()
        await _call_hts_by_name(update, context, user_id, name)
        return
    
    await update.message.reply_text(
        "❌ **Format salah.**\n\n"
        "Gunakan:\n"
        "• `/hts-1` - Panggil HTS ranking 1\n"
        "• `/hts-sari` - Panggil HTS dengan nama Sari\n\n"
        "Gunakan `/hts-list` untuk melihat daftar HTS.",
        parse_mode='HTML'
    )


async def _call_hts_by_index(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, index: int) -> None:
    """Panggil HTS berdasarkan index"""
    
    hts_manager = HTSManager()
    hts = await hts_manager.get_hts_by_index(user_id, index)
    
    if not hts:
        await update.message.reply_text(
            f"❌ HTS ranking {index} tidak ditemukan.\n\n"
            f"Gunakan `/hts-list` untuk melihat daftar HTS.",
            parse_mode='HTML'
        )
        return
    
    # Cek apakah masih aktif
    is_active = await hts_manager.check_expiry(user_id, hts['hts_id'])
    
    if not is_active:
        await update.message.reply_text(
            f"❌ **HTS dengan {hts['bot_name']} sudah expired.**\n\n"
            f"Hubungan HTS hanya bertahan 3 bulan.\n"
            f"Gunakan `/start` untuk memulai role baru.",
            parse_mode='HTML'
        )
        return
    
    # Mulai sesi intim
    await _start_intimacy_session(update, context, user_id, hts)


async def _call_hts_by_name(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, name: str) -> None:
    """Panggil HTS berdasarkan nama"""
    
    hts_manager = HTSManager()
    hts = await hts_manager.get_hts_by_name(user_id, name)
    
    if not hts:
        await update.message.reply_text(
            f"❌ HTS dengan nama '{name}' tidak ditemukan.\n\n"
            f"Gunakan `/hts-list` untuk melihat daftar HTS.",
            parse_mode='HTML'
        )
        return
    
    # Cek apakah masih aktif
    is_active = await hts_manager.check_expiry(user_id, hts['hts_id'])
    
    if not is_active:
        await update.message.reply_text(
            f"❌ **HTS dengan {hts['bot_name']} sudah expired.**\n\n"
            f"Hubungan HTS hanya bertahan 3 bulan.\n"
            f"Gunakan `/start` untuk memulai role baru.",
            parse_mode='HTML'
        )
        return
    
    # Mulai sesi intim
    await _start_intimacy_session(update, context, user_id, hts)


async def _start_intimacy_session(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, hts: Dict) -> None:
    """
    Mulai sesi intim dengan HTS
    """
    bot_name = hts['bot_name']
    role = hts['role']
    
    # Cek cooldown
    remaining_days = await hts_manager.get_remaining_days(user_id, hts['hts_id'])
    
    # Konfirmasi
    keyboard = [
        [InlineKeyboardButton("✅ Ya, Ajak Intim", callback_data=f"hts_intim_yes_{hts['hts_id']}"),
         InlineKeyboardButton("❌ Batal", callback_data="hts_intim_no")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"💕 **Panggil HTS: {bot_name}**\n\n"
        f"Role: {role.title()}\n"
        f"Chemistry: {hts['chemistry_score']:.0f}%\n"
        f"Total Climax: {hts['climax_count']}\n"
        f"Sisa waktu: {remaining_days:.0f} hari\n\n"
        f"**Yakin ingin mengajak {bot_name} intim?**\n\n"
        f"_{bot_name} akan merespon secara natural, 100% AI generate._",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def hts_intim_yes_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback konfirmasi ajak intim HTS"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    hts_id = data.replace("hts_intim_yes_", "")
    
    hts_manager = HTSManager()
    hts = await hts_manager.get_hts(user_id, hts_id)
    
    if not hts:
        await query.edit_message_text(
            "❌ HTS tidak ditemukan.",
            parse_mode='HTML'
        )
        return
    
    # Cek expired
    if not await hts_manager.check_expiry(user_id, hts_id):
        await query.edit_message_text(
            f"❌ **HTS dengan {hts['bot_name']} sudah expired.**\n\n"
            f"Hubungan HTS hanya bertahan 3 bulan.",
            parse_mode='HTML'
        )
        return
    
    # Update session context
    context.user_data['current_hts'] = {
        'id': hts_id,
        'bot_name': hts['bot_name'],
        'role': hts['role'],
        'chemistry': hts['chemistry_score']
    }
    
    # Record interaction
    await hts_manager.record_interaction(user_id, hts_id, is_intim=True)
    
    await query.edit_message_text(
        f"💕 **Memulai sesi dengan {hts['bot_name']}**\n\n"
        f"_Ketik pesan untuk memulai percakapan..._\n\n"
        f"💡 **Tips:**\n"
        f"• Bot akan merespon secara natural\n"
        f"• Semua respons 100% AI generate\n"
        f"• Gunakan /status untuk lihat progress",
        parse_mode='HTML'
    )
    
    logger.info(f"User {user_id} started intimacy with HTS: {hts['bot_name']}")


async def hts_intim_no_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback batal ajak intim HTS"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "✅ **Dibatalkan.**\n\n"
        "Gunakan `/hts-list` untuk memanggil HTS lain.",
        parse_mode='HTML'
    )


async def hts_detail_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /hts-detail [nomor] - Lihat detail HTS
    """
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "❌ **Cara pakai:** /hts-detail [nomor]\n\n"
            "Contoh: `/hts-detail 1`\n\n"
            "Gunakan `/hts-list` untuk melihat daftar.",
            parse_mode='HTML'
        )
        return
    
    try:
        index = int(args[0])
    except ValueError:
        await update.message.reply_text(
            "❌ Nomor harus berupa angka.\n\n"
            "Contoh: `/hts-detail 1`",
            parse_mode='HTML'
        )
        return
    
    hts_manager = HTSManager()
    hts = await hts_manager.get_hts_by_index(user_id, index)
    
    if not hts:
        await update.message.reply_text(
            f"❌ HTS ranking {index} tidak ditemukan.",
            parse_mode='HTML'
        )
        return
    
    formatted = await hts_manager.format_hts_detail(user_id, hts['hts_id'])
    await update.message.reply_text(formatted, parse_mode='HTML')


__all__ = [
    'hts_list_command',
    'hts_call_handler',
    'hts_detail_command',
    'hts_intim_yes_callback',
    'hts_intim_no_callback'
]
