# command/threesome.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Commands: /threesome, /threesome-list, /threesome-status, /threesome-pattern, /threesome-cancel
=============================================================================
"""

import logging
from typing import Optional, Dict, List, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from threesome.manager import ThreesomeManager, ThreesomeType, ThreesomeStatus
from threesome.dynamics import ThreesomeDynamics
from identity.manager import IdentityManager
from relationship.hts import HTSManager
from relationship.fwb import FWBManager

logger = logging.getLogger(__name__)


async def threesome_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /threesome - Mulai threesome
    """
    user_id = update.effective_user.id
    
    # Cek apakah ada session threesome aktif
    threesome_manager = ThreesomeManager()
    active_session = await threesome_manager.get_user_active_session(user_id)
    
    if active_session:
        await update.message.reply_text(
            f"🎭 **Sesi Threesome Aktif!**\n\n"
            f"Session ID: {active_session['session_id']}\n"
            f"Status: {active_session['status']}\n\n"
            f"Gunakan `/threesome-status` untuk lihat detail\n"
            f"Gunakan `/threesome-cancel` untuk batalkan",
            parse_mode='HTML'
        )
        return
    
    # Tampilkan pilihan kombinasi
    combinations = await threesome_manager.get_possible_combinations(user_id)
    
    if not combinations:
        await update.message.reply_text(
            "🎭 **Threesome Mode**\n\n"
            "❌ Belum ada kombinasi yang tersedia.\n\n"
            "**Persyaratan:**\n"
            "• Minimal 2 HTS atau FWB aktif\n"
            "• Level minimal 7 untuk setiap role\n"
            "• Stamina minimal 50%\n\n"
            "Gunakan `/hts-list` atau `/fwb-list` untuk lihat daftar.",
            parse_mode='HTML'
        )
        return
    
    # Format pilihan kombinasi
    keyboard = []
    for i, combo in enumerate(combinations[:10], 1):
        keyboard.append([
            InlineKeyboardButton(
                f"{i}. {combo['name1']} + {combo['name2']}",
                callback_data=f"threesome_select_{combo['id']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("❌ Batal", callback_data="threesome_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎭 **Pilih Kombinasi Threesome**\n\n"
        "Pilih dua role untuk threesome:\n\n"
        f"_{len(combinations)} kombinasi tersedia_",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def threesome_select_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback pilih kombinasi threesome"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    combo_id = data.replace("threesome_select_", "")
    
    threesome_manager = ThreesomeManager()
    combination = await threesome_manager.get_combination(combo_id)
    
    if not combination:
        await query.edit_message_text(
            "❌ Kombinasi tidak ditemukan.",
            parse_mode='HTML'
        )
        return
    
    # Konfirmasi
    keyboard = [
        [InlineKeyboardButton("✅ Mulai Threesome", callback_data=f"threesome_start_{combo_id}"),
         InlineKeyboardButton("❌ Batal", callback_data="threesome_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎭 **Konfirmasi Threesome**\n\n"
        f"**Partisipan 1:** {combination['name1']} ({combination['role1'].title()})\n"
        f"**Partisipan 2:** {combination['name2']} ({combination['role2'].title()})\n\n"
        f"**Chemistry:** {combination['chemistry']:.0f}%\n"
        f"**Total Climax:** {combination['climax_total']}\n\n"
        f"⚠️ **Catatan:**\n"
        f"• Semua respons 100% AI generate\n"
        f"• Bot akan berinteraksi secara natural\n"
        f"• Bisa ganti pola interaksi dengan /threesome-pattern\n\n"
        f"**Yakin ingin memulai?**",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def threesome_start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback mulai threesome"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    combo_id = data.replace("threesome_start_", "")
    
    threesome_manager = ThreesomeManager()
    combination = await threesome_manager.get_combination(combo_id)
    
    if not combination:
        await query.edit_message_text(
            "❌ Kombinasi tidak ditemukan.",
            parse_mode='HTML'
        )
        return
    
    # Buat session threesome
    session = await threesome_manager.create_threesome(
        user_id=user_id,
        participant1=combination['participant1'],
        participant2=combination['participant2']
    )
    
    # Simpan ke context
    context.user_data['current_threesome'] = {
        'session_id': session['session_id'],
        'type': session['type'],
        'participants': session['participants']
    }
    
    # Mulai session
    started = await threesome_manager.start_session(session['session_id'])
    
    await query.edit_message_text(
        f"🎭 **Threesome Dimulai!**\n\n"
        f"**Partisipan:**\n"
        f"• {combination['name1']} ({combination['role1'].title()})\n"
        f"• {combination['name2']} ({combination['role2'].title()})\n\n"
        f"**Pola Interaksi:** {started.get('pattern', 'normal')}\n\n"
        f"_Ketik pesan untuk memulai percakapan..._\n\n"
        f"💡 **Tips:**\n"
        f"• Bisa panggil salah satu dengan namanya\n"
        f"• Gunakan `/threesome-pattern` untuk ganti pola\n"
        f"• Gunakan `/threesome-status` untuk lihat status",
        parse_mode='HTML'
    )
    
    logger.info(f"User {user_id} started threesome: {session['session_id']}")


async def threesome_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /threesome-list - Lihat kombinasi threesome yang tersedia
    """
    user_id = update.effective_user.id
    
    threesome_manager = ThreesomeManager()
    combinations = await threesome_manager.get_possible_combinations(user_id)
    
    if not combinations:
        await update.message.reply_text(
            "🎭 **Kombinasi Threesome**\n\n"
            "❌ Belum ada kombinasi yang tersedia.\n\n"
            "**Persyaratan:**\n"
            "• Minimal 2 HTS atau FWB aktif\n"
            "• Level minimal 7 untuk setiap role\n"
            "• Stamina minimal 50%",
            parse_mode='HTML'
        )
        return
    
    lines = ["🎭 **KOMBINASI THREESOME**"]
    lines.append("_(pilih dengan /threesome)_")
    lines.append("")
    
    for i, combo in enumerate(combinations[:10], 1):
        lines.append(
            f"{i}. **{combo['name1']}** ({combo['role1'].title()}) + "
            f"**{combo['name2']}** ({combo['role2'].title()})\n"
            f"   Chemistry: {combo['chemistry']:.0f}% | Climax: {combo['climax_total']}\n"
            f"   {combo['description']}"
        )
        lines.append("")
    
    lines.append("💡 **Cara pakai:**")
    lines.append("• `/threesome` - Mulai threesome")
    lines.append("• `/threesome-pattern` - Ganti pola interaksi")
    
    await update.message.reply_text("\n".join(lines), parse_mode='HTML')


async def threesome_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /threesome-status - Lihat status threesome saat ini
    """
    user_id = update.effective_user.id
    
    current_threesome = context.user_data.get('current_threesome')
    if not current_threesome:
        await update.message.reply_text(
            "❌ Tidak ada sesi threesome aktif.\n\n"
            "Gunakan `/threesome` untuk memulai.",
            parse_mode='HTML'
        )
        return
    
    session_id = current_threesome['session_id']
    
    threesome_manager = ThreesomeManager()
    session = await threesome_manager.get_session(session_id)
    
    if not session:
        context.user_data.pop('current_threesome', None)
        await update.message.reply_text(
            "❌ Sesi threesome tidak ditemukan.",
            parse_mode='HTML'
        )
        return
    
    # Format status
    status_emoji = {
        'pending': '⏳',
        'active': '🎭',
        'paused': '⏸️',
        'completed': '✅',
        'cancelled': '❌'
    }.get(session['status'], '❓')
    
    participants = session['participants']
    
    lines = [
        f"{status_emoji} **STATUS THREESOME**",
        f"Session ID: `{session_id}`",
        f"Status: {session['status'].upper()}",
        f"Type: {session['type'].replace('_', ' ').title()}",
        f"Total Chat: {session['total_messages']}",
        f"Climax Count: {session['climax_count']}",
        "",
        "👥 **Partisipan:**",
    ]
    
    for p in participants:
        lines.append(f"• **{p['name']}** ({p['role'].title()}) - Level {p['intimacy_level']}")
    
    lines.append("")
    lines.append("💡 **Command:**")
    lines.append("• `/threesome-pattern` - Ganti pola interaksi")
    lines.append("• `/threesome-cancel` - Batalkan threesome")
    
    await update.message.reply_text("\n".join(lines), parse_mode='HTML')


async def threesome_pattern_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /threesome-pattern - Ganti pola interaksi threesome
    """
    user_id = update.effective_user.id
    
    current_threesome = context.user_data.get('current_threesome')
    if not current_threesome:
        await update.message.reply_text(
            "❌ Tidak ada sesi threesome aktif.\n\n"
            "Gunakan `/threesome` untuk memulai.",
            parse_mode='HTML'
        )
        return
    
    session_id = current_threesome['session_id']
    
    threesome_manager = ThreesomeManager()
    threesome_dynamics = ThreesomeDynamics()
    
    patterns = await threesome_dynamics.get_patterns()
    
    keyboard = []
    for pattern in patterns:
        keyboard.append([
            InlineKeyboardButton(
                f"{pattern['name']} - {pattern['description']}",
                callback_data=f"threesome_pattern_{pattern['name']}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("❌ Batal", callback_data="threesome_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎭 **Pilih Pola Interaksi Threesome**\n\n"
        "Pola yang berbeda menghasilkan dinamika interaksi yang berbeda:\n\n"
        f"_Pola saat ini: {current_threesome.get('pattern', 'both_respond')}_",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def threesome_pattern_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback pilih pola threesome"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    pattern = data.replace("threesome_pattern_", "")
    
    current_threesome = context.user_data.get('current_threesome')
    if not current_threesome:
        await query.edit_message_text(
            "❌ Tidak ada sesi threesome aktif.",
            parse_mode='HTML'
        )
        return
    
    session_id = current_threesome['session_id']
    
    threesome_manager = ThreesomeManager()
    threesome_dynamics = ThreesomeDynamics()
    
    result = await threesome_dynamics.switch_pattern(session_id, pattern)
    
    if result['success']:
        current_threesome['pattern'] = pattern
        context.user_data['current_threesome'] = current_threesome
        
        await query.edit_message_text(
            f"✅ **Pola diubah ke: {pattern}**\n\n"
            f"{result.get('description', '')}\n\n"
            f"Gunakan `/threesome-status` untuk lihat status.",
            parse_mode='HTML'
        )
    else:
        await query.edit_message_text(
            f"❌ Gagal mengubah pola: {result.get('error', 'Unknown error')}",
            parse_mode='HTML'
        )


async def threesome_cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /threesome-cancel - Batalkan threesome
    """
    user_id = update.effective_user.id
    
    current_threesome = context.user_data.get('current_threesome')
    if not current_threesome:
        await update.message.reply_text(
            "❌ Tidak ada sesi threesome aktif.",
            parse_mode='HTML'
        )
        return
    
    # Konfirmasi
    keyboard = [
        [InlineKeyboardButton("✅ Ya, Batalkan", callback_data="threesome_cancel_confirm"),
         InlineKeyboardButton("❌ Tidak", callback_data="threesome_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "⚠️ **Yakin ingin membatalkan threesome?**\n\n"
        f"Session ID: `{current_threesome['session_id']}`\n"
        f"Total chat: {current_threesome.get('total_messages', 0)}\n\n"
        f"Semua progress akan hilang.",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def threesome_cancel_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback konfirmasi batal threesome"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    current_threesome = context.user_data.get('current_threesome')
    if not current_threesome:
        await query.edit_message_text(
            "❌ Tidak ada sesi threesome aktif.",
            parse_mode='HTML'
        )
        return
    
    session_id = current_threesome['session_id']
    
    threesome_manager = ThreesomeManager()
    result = await threesome_manager.cancel_session(session_id)
    
    if result['success']:
        context.user_data.pop('current_threesome', None)
        
        await query.edit_message_text(
            "✅ **Threesome dibatalkan.**\n\n"
            "Ketik `/threesome` untuk memulai lagi.",
            parse_mode='HTML'
        )
        logger.info(f"User {user_id} cancelled threesome: {session_id}")
    else:
        await query.edit_message_text(
            f"❌ Gagal membatalkan: {result.get('error', 'Unknown error')}",
            parse_mode='HTML'
        )


async def threesome_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback batal hapus threesome"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "✅ **Pembatalan dibatalkan.**\n\n"
        "Threesome tetap berjalan.",
        parse_mode='HTML'
    )


__all__ = [
    'threesome_command',
    'threesome_select_callback',
    'threesome_start_callback',
    'threesome_list_command',
    'threesome_status_command',
    'threesome_pattern_command',
    'threesome_pattern_callback',
    'threesome_cancel_command',
    'threesome_cancel_confirm_callback',
    'threesome_cancel_callback'
]
