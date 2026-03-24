# bot/handlers.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Main Message Handler
=============================================================================
"""

import time
import logging
import random
import asyncio
from typing import Dict

from telegram import Update
from telegram.ext import ContextTypes

from identity.manager import IdentityManager
from core.ai_engine import AIEngine
from intimacy.leveling import LevelingSystem
from intimacy.stamina import StaminaSystem
from utils.logger import logger

_active_engines: Dict[str, AIEngine] = {}

# =============================================================================
# CONSTANTS
# =============================================================================
MAX_MESSAGE_LENGTH = 3000  # Telegram limit is 4096, use 4000 for safety


# =============================================================================
# HELPER: SEND LONG MESSAGE
# =============================================================================

async def send_long_message(update: Update, text: str, parse_mode: str = 'HTML'):
    """
    Kirim pesan panjang dengan split jika melebihi batas Telegram
    
    Args:
        update: Update object dari Telegram
        text: Teks pesan
        parse_mode: Mode parsing ('HTML' atau 'Markdown')
    """
    if len(text) <= MAX_MESSAGE_LENGTH:
        await update.message.reply_text(text, parse_mode=parse_mode)
        return
    
    # Split menjadi beberapa pesan
    parts = []
    remaining = text
    
    while len(remaining) > MAX_MESSAGE_LENGTH:
        # Cari posisi terakhir newline atau spasi untuk split yang rapi
        split_pos = remaining[:MAX_MESSAGE_LENGTH].rfind('\n')
        if split_pos == -1:
            split_pos = remaining[:MAX_MESSAGE_LENGTH].rfind(' ')
        if split_pos == -1:
            split_pos = MAX_MESSAGE_LENGTH
        
        parts.append(remaining[:split_pos])
        remaining = remaining[split_pos:]
    
    parts.append(remaining)
    
    # Kirim per bagian
    for i, part in enumerate(parts, 1):
        prefix = f"📄 Bagian {i}/{len(parts)}:\n\n" if len(parts) > 1 else ""
        await update.message.reply_text(prefix + part, parse_mode=parse_mode)


# =============================================================================
# MESSAGE HANDLER
# =============================================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk semua pesan teks"""
    try:
        user = update.effective_user
        user_message = update.message.text
        user_id = user.id
        
        current_reg = context.user_data.get('current_registration')
        
        if not current_reg:
            await update.message.reply_text(
                "❌ **Tidak ada karakter aktif**\n\n"
                "Ketik `/start` untuk memilih karakter.",
                parse_mode='HTML'
            )
            return
        
        registration_id = current_reg.get('id')
        
        if context.user_data.get('paused', False):
            await update.message.reply_text(
                "⏸️ **Sesi dijeda**\n\nKetik `/unpause` untuk melanjutkan.",
                parse_mode='HTML'
            )
            return
        
        if registration_id not in _active_engines:
            identity_manager = IdentityManager()
            character = await identity_manager.get_character(registration_id)
            
            if not character:
                await update.message.reply_text(
                    "❌ **Karakter tidak ditemukan**\n\nKetik `/sessions` untuk melihat karakter.",
                    parse_mode='HTML'
                )
                return
            
            _active_engines[registration_id] = AIEngine(character)
            logger.info(f"✅ AI Engine created for {registration_id}")
        
        ai_engine = _active_engines[registration_id]
        
        # Dapatkan state (hanya lokasi, posisi, pakaian)
        identity_manager = IdentityManager()
        state = await identity_manager.get_character_state(registration_id)
        
        # Update waktu typing
        await update.message.chat.send_action(action="typing")
        
        # Simulasi delay natural (1-3 detik)
        await asyncio.sleep(random.uniform(1, 3))
        
        # Proses pesan dengan AI
        response = await ai_engine.process_message(
            user_message=user_message,
            context={
                'state': state,
                'user_name': current_reg.get('user_name', 'User'),
                'bot_name': current_reg.get('bot_name', 'Amoria'),
                'role': current_reg.get('role', 'pdkt'),
                'level': current_reg.get('level', 1)
            }
        )
        
        # Kirim respons dengan fungsi split jika terlalu panjang
        await send_long_message(update, response, parse_mode='HTML')
        
        # Update progress setelah chat
        await _update_progress(registration_id, ai_engine)
        
        # Update context
        context.user_data['last_message_time'] = time.time()
        context.user_data['last_message'] = user_message
        context.user_data['last_response'] = response
        
    except Exception as e:
        logger.error(f"Error in message_handler: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(
            "❌ **Terjadi kesalahan**\n\nMaaf, aku mengalami gangguan. Coba lagi nanti.",
            parse_mode='HTML'
        )


# =============================================================================
# UPDATE PROGRESS
# =============================================================================

async def _update_progress(registration_id: str, ai_engine: AIEngine) -> None:
    """Update progress setelah chat"""
    try:
        identity_manager = IdentityManager()
        character = await identity_manager.get_character(registration_id)
        
        if not character:
            return
        
        # Update total chats
        character.total_chats += 1
        character.last_updated = time.time()
        
        # Leveling system
        leveling = LevelingSystem()
        old_level = character.level
        level_info = leveling.calculate_level(character.total_chats, character.in_intimacy_cycle)
        new_level = level_info.level
        
        if new_level > old_level:
            character.level = new_level
            logger.info(f"Level up for {registration_id}: {old_level} → {new_level}")
        
        # Stamina recovery (gunakan bot dan user object)
        stamina = StaminaSystem()
        stamina.check_recovery()
        
        # Update stamina ke bot dan user object
        character.bot.stamina = stamina.bot_stamina.current
        character.user.stamina = stamina.user_stamina.current
        
        # Save to database
        db_reg = character.to_db_registration()
        await identity_manager.repo.update_registration(db_reg)
        
        # Save state (tanpa emotion/arousal)
        state = await identity_manager.get_character_state(registration_id)
        if state:
            state.updated_at = time.time()
            await identity_manager.repo.save_state(state)
        
    except Exception as e:
        logger.error(f"Error updating progress: {e}")


# =============================================================================
# OTHER HANDLERS
# =============================================================================

async def continue_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk melanjutkan session (internal)"""
    await update.message.reply_text(
        "🔄 **Melanjutkan session...**\n\n"
        "Gunakan `/sessions` untuk melihat daftar session yang tersimpan.",
        parse_mode='HTML'
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk /help - Bantuan lengkap"""
    user_id = update.effective_user.id
    is_admin = (user_id == 6792300623)  # Admin ID
    
    help_text = (
        "📚 **BANTUAN AMORIA 9.9**\n\n"
        "<b>Basic Commands:</b>\n"
        "/start - Mulai bot & pilih karakter\n"
        "/help - Bantuan lengkap\n"
        "/status - Status hubungan saat ini\n"
        "/progress - Progress leveling\n"
        "/cancel - Batalkan percakapan\n\n"
        "<b>Session Commands:</b>\n"
        "/close - Tutup & simpan karakter\n"
        "/end - Akhiri karakter total\n"
        "/sessions - Lihat semua karakter tersimpan\n"
        "/character [role] [nomor] - Lanjutkan karakter\n\n"
        "<b>Character Commands:</b>\n"
        "/character_list - Lihat semua karakter\n"
        "/character_pause - Jeda karakter\n"
        "/character_resume - Lanjutkan karakter\n"
        "/character_stop - Hentikan karakter\n\n"
        "<b>Ex & FWB Commands:</b>\n"
        "/ex_list - Lihat daftar mantan\n"
        "/ex [nomor] - Detail mantan\n"
        "/fwb_request [nomor] - Request jadi FWB\n"
        "/fwb_list - Lihat daftar FWB\n"
        "/fwb_pause [nomor] - Jeda FWB\n"
        "/fwb_resume [nomor] - Lanjutkan FWB\n"
        "/fwb_end [nomor] - Akhiri FWB\n\n"
        "<b>HTS Commands:</b>\n"
        "/hts_list - Lihat TOP 10 HTS\n"
        "/hts_[nomor] - Panggil HTS untuk intim\n\n"
        "<b>Public Area Commands:</b>\n"
        "/explore - Cari lokasi random\n"
        "/locations - Lihat semua lokasi\n"
        "/risk - Cek risk lokasi saat ini\n"
        "/go [lokasi] - Pindah ke lokasi\n\n"
        "<b>Memory Commands:</b>\n"
        "/memory - Ringkasan memory\n"
        "/flashback - Flashback random\n\n"
        "<b>Ranking Commands:</b>\n"
        "/top_hts - TOP 5 ranking HTS\n"
        "/my_climax - Statistik climax pribadi\n"
        "/climax_history - History climax"
    )
    
    if is_admin:
        help_text += (
            "\n\n<b>Admin Commands:</b>\n"
            "/admin - Panel admin\n"
            "/stats - Statistik bot\n"
            "/db_stats - Statistik database\n"
            "/backup - Backup manual\n"
            "/recover - Restore dari backup\n"
            "/debug - Info debug"
        )
    
    await update.message.reply_text(help_text, parse_mode='HTML')


async def status_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk /status - Alias ke status_command di command/status.py"""
    from command.status import status_command
    await status_command(update, context)


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk /cancel - Batalkan percakapan"""
    context.user_data.pop('pending_action', None)
    
    await update.message.reply_text(
        "❌ **Dibatalkan**\n\n"
        "Percakapan dibatalkan. Ketik pesan untuk memulai lagi.",
        parse_mode='HTML'
    )


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler untuk semua error di bot"""
    logger.error(f"Update {update} caused error {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ **Terjadi error internal**\n\n"
                "Maaf, terjadi kesalahan. Silakan coba lagi nanti, Mas.\n\n"
                "_Jika error berlanjut, laporkan ke admin._",
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Error sending error message: {e}")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    'message_handler',
    'continue_handler',
    'help_command',
    'status_command_handler',
    'cancel_command',
    'error_handler',
    '_active_engines',
    'send_long_message',
]
