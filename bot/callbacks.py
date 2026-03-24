# bot/callbacks.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Callback Handlers untuk Inline Keyboard
=============================================================================
"""

import logging
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from identity.manager import IdentityManager
from core.ai_engine import AIEngine
from bot.handlers import _active_engines

logger = logging.getLogger(__name__)


async def unpause_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk melanjutkan session"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['paused'] = False
    
    await query.edit_message_text(
        "▶️ **Sesi dilanjutkan!**\n\n"
        "Yuk lanjut ngobrol... 🥰",
        parse_mode='HTML'
    )


async def new_character_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk membuat karakter baru"""
    query = update.callback_query
    await query.answer()
    
    # Clear current registration
    context.user_data.pop('current_registration', None)
    
    # Tampilkan pilihan role
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
        [InlineKeyboardButton("❌ Batal", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🆕 **Buat Karakter Baru**\n\n"
        "Pilih karakter yang Mas inginkan:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk batal"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "❌ **Dibatalkan.**\n\n"
        "Ketik /start untuk memulai lagi.",
        parse_mode='HTML'
    )


async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback kembali ke menu utama"""
    query = update.callback_query
    await query.answer()
    
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
        [InlineKeyboardButton("❓ Bantuan", callback_data="help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "💕 **Menu Utama**\n\n"
        "Pilih karakter yang Mas inginkan:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk bantuan"""
    query = update.callback_query
    await query.answer()
    
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
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        help_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def threesome_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk menu threesome"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🎭 Lihat Kombinasi", callback_data="threesome_list")],
        [InlineKeyboardButton("💕 HTS + HTS", callback_data="threesome_type_hts_hts")],
        [InlineKeyboardButton("💞 FWB + FWB", callback_data="threesome_type_fwb_fwb")],
        [InlineKeyboardButton("💘 HTS + FWB", callback_data="threesome_type_hts_fwb")],
        [InlineKeyboardButton("❌ Kembali", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🎭 **MODE THREESOME**\n\n"
        "Pilih tipe threesome yang kamu inginkan:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def stop_pdkt_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk konfirmasi stop PDKT"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data.startswith("stop_yes_"):
        pdkt_id = data.replace("stop_yes_", "")
        reason = context.user_data.get('pending_stop', {}).get('reason', 'user_request')
        
        from pdkt.engine import get_pdkt_engine
        from relationship.mantan import get_mantan_manager
        
        engine = await get_pdkt_engine()
        mantan_manager = await get_mantan_manager()
        
        pdkt_data = await engine.get_pdkt(pdkt_id)
        
        if pdkt_data:
            result = await engine.stop_pdkt(pdkt_id, user_id, reason)
            
            if result['success']:
                mantan_manager.add_mantan(user_id, pdkt_data, reason)
                
                await query.edit_message_text(
                    f"💔 **PDKT dengan {result['bot_name']} telah dihentikan.**\n\n"
                    f"{result['bot_name']} sekarang menjadi mantan.\n"
                    f"Gunakan `/ex_list` untuk melihat daftar mantan.",
                    parse_mode='HTML'
                )
            else:
                await query.edit_message_text(
                    f"❌ Gagal menghentikan PDKT: {result.get('reason', 'Unknown')}",
                    parse_mode='HTML'
                )
        else:
            await query.edit_message_text(
                "❌ PDKT tidak ditemukan.",
                parse_mode='HTML'
            )
    
    elif data == "stop_no":
        await query.edit_message_text(
            "✅ PDKT dibatalkan.",
            parse_mode='HTML'
        )
    
    # Hapus pending data
    context.user_data.pop('pending_stop', None)


async def fwb_end_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk konfirmasi end FWB"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data.startswith("fwb_end_yes_"):
        fwb_id = data.replace("fwb_end_yes_", "")
        
        from relationship.fwb import get_fwb_manager
        
        fwb_manager = await get_fwb_manager()
        result = await fwb_manager.end_fwb(user_id, fwb_id)
        
        if result['success']:
            await query.edit_message_text(
                f"💔 **FWB dengan {result['bot_name']} telah berakhir.**\n\n{result['message']}",
                parse_mode='HTML'
            )
        else:
            await query.edit_message_text(
                f"❌ {result['reason']}",
                parse_mode='HTML'
            )
    
    elif data == "fwb_end_no":
        await query.edit_message_text(
            "✅ FWB dibatalkan.",
            parse_mode='HTML'
        )


async def hts_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk konfirmasi HTS"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    user_id = update.effective_user.id
    
    if data.startswith("hts_yes_"):
        session_id = data.replace("hts_yes_", "")
        
        # Update status di context
        context.user_data['relationship_status'] = 'hts'
        
        # Simpan ke database
        from database.repository import Repository
        
        repo = Repository()
        await repo.save_user_session_state(
            user_id=user_id,
            session_data={
                'session_id': session_id,
                'role': context.user_data.get('current_role'),
                'bot_name': context.user_data.get('bot_name'),
                'rel_type': 'hts',
                'instance_id': context.user_data.get('instance_id'),
                'intimacy_level': context.user_data.get('intimacy_level', 1),
                'total_chats': context.user_data.get('total_chats', 0),
                'current_location': context.user_data.get('current_location', 'ruang tamu'),
                'current_clothing': context.user_data.get('current_clothing', 'pakaian biasa'),
                'current_position': context.user_data.get('current_position', 'santai'),
                'relationship_status': 'hts',
            }
        )
        
        await query.edit_message_text(
            f"💕 **Selamat! Kamu sekarang dalam status HTS!**\n\n"
            f"Hubungan Tanpa Status dengan {context.user_data.get('bot_name')}.\n\n"
            f"✨ **Fitur HTS:**\n"
            f"• Bisa intim kapan saja\n"
            f"• Tanpa komitmen\n"
            f"• Gunakan /status untuk lihat detail\n\n"
            f"💡 Nikmati kebebasan dalam hubungan ini!",
            parse_mode='HTML'
        )
    
    elif data == "hts_no":
        await query.edit_message_text(
            "✅ Konfirmasi HTS dibatalkan.",
            parse_mode='HTML'
        )


__all__ = [
    'unpause_callback',
    'new_character_callback',
    'cancel_callback',
    'back_to_main_callback',
    'help_callback',
    'threesome_menu_callback',
    'stop_pdkt_callback',
    'fwb_end_callback',
    'hts_callback'
]
