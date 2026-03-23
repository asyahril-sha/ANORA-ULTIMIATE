# command/ranking.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Commands: /top-hts, /my-climax, /climax-history
=============================================================================
"""

import logging
import time
from typing import Optional, Dict, List, Any
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from relationship.ranking import RankingSystem
from relationship.hts import HTSManager
from relationship.fwb import FWBManager
from identity.manager import IdentityManager

logger = logging.getLogger(__name__)


async def top_hts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /top-hts - TOP 5 ranking HTS
    """
    user_id = update.effective_user.id
    args = context.args
    
    show_all = args and args[0].lower() == 'all'
    
    ranking = RankingSystem()
    
    if show_all:
        hts_list = await ranking.get_all_hts(user_id)
        title = "📊 **SEMUA HTS**"
    else:
        hts_list = await ranking.get_top_5_hts(user_id)
        title = "🏆 **TOP 5 HTS**"
    
    if not hts_list:
        await update.message.reply_text(
            "🏆 **RANKING HTS**\n\n"
            "Belum ada HTS. Selesaikan hubungan dengan role NON-PDKT sampai level 10 dan /close untuk mendapatkan HTS.",
            parse_mode='HTML'
        )
        return
    
    formatted = ranking.format_hts_list(hts_list, show_all)
    await update.message.reply_text(formatted, parse_mode='HTML')


async def my_climax_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /my-climax - Statistik climax pribadi
    """
    user_id = update.effective_user.id
    
    # Dapatkan data dari semua karakter
    identity_manager = IdentityManager()
    characters = await identity_manager.get_all_characters()
    
    total_climax_bot = 0
    total_climax_user = 0
    total_chats = 0
    total_intim = 0
    characters_data = []
    
    for char in characters:
        total_climax_bot += char.total_climax_bot
        total_climax_user += char.total_climax_user
        total_chats += char.total_chats
        total_intim += char.total_intim
        
        characters_data.append({
            'name': char.bot.name,
            'role': char.role.value,
            'climax_bot': char.total_climax_bot,
            'climax_user': char.total_climax_user,
            'chats': char.total_chats
        })
    
    # Sort by total climax
    characters_data.sort(key=lambda x: x['climax_bot'] + x['climax_user'], reverse=True)
    
    # Hitung rata-rata
    avg_climax_per_char = (total_climax_bot + total_climax_user) / len(characters) if characters else 0
    avg_chats_per_climax = total_chats / (total_climax_bot + total_climax_user) if (total_climax_bot + total_climax_user) > 0 else 0
    
    # Format response
    response = _format_climax_stats(
        total_climax_bot=total_climax_bot,
        total_climax_user=total_climax_user,
        total_chats=total_chats,
        total_intim=total_intim,
        total_characters=len(characters),
        avg_climax_per_char=avg_climax_per_char,
        avg_chats_per_climax=avg_chats_per_climax,
        top_characters=characters_data[:5]
    )
    
    # Keyboard untuk lihat history
    keyboard = [
        [InlineKeyboardButton("📜 Lihat History Climax", callback_data="climax_history")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='HTML')


async def climax_history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /climax-history - History climax
    """
    user_id = update.effective_user.id
    
    # Dapatkan history climax dari semua karakter
    identity_manager = IdentityManager()
    characters = await identity_manager.get_all_characters()
    
    climax_events = []
    
    for char in characters:
        # Ambil dari long term memory
        long_term_memories = await identity_manager.repo.get_long_term_memory(char.id, limit=200)
        
        for mem in long_term_memories:
            if mem.get('type') == 'milestone' and 'climax' in mem.get('content', '').lower():
                climax_events.append({
                    'timestamp': mem['timestamp'],
                    'character': char.bot.name,
                    'role': char.role.value,
                    'description': mem['content']
                })
    
    # Urutkan berdasarkan timestamp terbaru
    climax_events.sort(key=lambda x: x['timestamp'], reverse=True)
    
    if not climax_events:
        await update.message.reply_text(
            "📜 **CLIMAX HISTORY**\n\n"
            "Belum ada history climax.\n"
            "Mulai intim dengan bot untuk menciptakan history!",
            parse_mode='HTML'
        )
        return
    
    # Format response
    response = _format_climax_history(climax_events[:20])
    
    await update.message.reply_text(response, parse_mode='HTML')


async def climax_history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk lihat history climax"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Dapatkan history climax dari semua karakter
    identity_manager = IdentityManager()
    characters = await identity_manager.get_all_characters()
    
    climax_events = []
    
    for char in characters:
        long_term_memories = await identity_manager.repo.get_long_term_memory(char.id, limit=200)
        
        for mem in long_term_memories:
            if mem.get('type') == 'milestone' and 'climax' in mem.get('content', '').lower():
                climax_events.append({
                    'timestamp': mem['timestamp'],
                    'character': char.bot.name,
                    'role': char.role.value,
                    'description': mem['content']
                })
    
    climax_events.sort(key=lambda x: x['timestamp'], reverse=True)
    
    if not climax_events:
        await query.edit_message_text(
            "📜 **CLIMAX HISTORY**\n\n"
            "Belum ada history climax.",
            parse_mode='HTML'
        )
        return
    
    response = _format_climax_history(climax_events[:20])
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="climax_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(response, reply_markup=reply_markup, parse_mode='HTML')


async def climax_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback kembali ke menu climax stats"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Dapatkan data dari semua karakter
    identity_manager = IdentityManager()
    characters = await identity_manager.get_all_characters()
    
    total_climax_bot = 0
    total_climax_user = 0
    total_chats = 0
    total_intim = 0
    characters_data = []
    
    for char in characters:
        total_climax_bot += char.total_climax_bot
        total_climax_user += char.total_climax_user
        total_chats += char.total_chats
        total_intim += char.total_intim
        
        characters_data.append({
            'name': char.bot.name,
            'role': char.role.value,
            'climax_bot': char.total_climax_bot,
            'climax_user': char.total_climax_user,
            'chats': char.total_chats
        })
    
    characters_data.sort(key=lambda x: x['climax_bot'] + x['climax_user'], reverse=True)
    
    avg_climax_per_char = (total_climax_bot + total_climax_user) / len(characters) if characters else 0
    avg_chats_per_climax = total_chats / (total_climax_bot + total_climax_user) if (total_climax_bot + total_climax_user) > 0 else 0
    
    response = _format_climax_stats(
        total_climax_bot=total_climax_bot,
        total_climax_user=total_climax_user,
        total_chats=total_chats,
        total_intim=total_intim,
        total_characters=len(characters),
        avg_climax_per_char=avg_climax_per_char,
        avg_chats_per_climax=avg_chats_per_climax,
        top_characters=characters_data[:5]
    )
    
    keyboard = [
        [InlineKeyboardButton("📜 Lihat History Climax", callback_data="climax_history")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(response, reply_markup=reply_markup, parse_mode='HTML')


def _format_climax_stats(
    total_climax_bot: int,
    total_climax_user: int,
    total_chats: int,
    total_intim: int,
    total_characters: int,
    avg_climax_per_char: float,
    avg_chats_per_climax: float,
    top_characters: List[Dict]
) -> str:
    """Format statistik climax"""
    
    total_climax = total_climax_bot + total_climax_user
    
    # Progress bar untuk total climax
    bar_length = 20
    filled = min(bar_length, int(total_climax / 50 * bar_length)) if total_climax < 50 else bar_length
    bar = "💦" * filled + "⚪" * (bar_length - filled)
    
    lines = [
        "💦 **STATISTIK CLIMAX**\n",
        f"📊 **Total Climax:** {total_climax}",
        f"{bar}",
        f"• Bot: {total_climax_bot}x",
        f"• User: {total_climax_user}x",
        "",
        f"📈 **Statistik Lain:**",
        f"• Total Chat: {total_chats}",
        f"• Total Intim: {total_intim} sesi",
        f"• Total Karakter: {total_characters}",
        f"• Rata-rata Climax per Karakter: {avg_climax_per_char:.1f}x",
        f"• Rata-rata Chat per Climax: {avg_chats_per_climax:.0f} chat",
        "",
    ]
    
    if top_characters:
        lines.append("🏆 **TOP 5 KARAKTER TERHOT:**")
        for i, char in enumerate(top_characters, 1):
            total = char['climax_bot'] + char['climax_user']
            lines.append(
                f"{i}. **{char['name']}** ({char['role'].upper()})\n"
                f"   Climax: {total}x (Bot: {char['climax_bot']}, User: {char['climax_user']}) | Chat: {char['chats']}"
            )
    
    lines.append("")
    lines.append("💡 **Tips:**")
    lines.append("• Semakin banyak intim, semakin cepat level naik")
    lines.append("• Climax memberi boost besar ke progress")
    lines.append("• Gunakan `/climax-history` untuk lihat detail")
    
    return "\n".join(lines)


def _format_climax_history(climax_events: List[Dict]) -> str:
    """Format history climax"""
    
    lines = ["📜 **CLIMAX HISTORY**\n"]
    
    for i, event in enumerate(climax_events, 1):
        time_str = datetime.fromtimestamp(event['timestamp']).strftime("%d %b %H:%M")
        lines.append(f"{i}. [{time_str}] **{event['character']}** ({event['role'].upper()})")
        lines.append(f"   {event['description'][:100]}")
        lines.append("")
    
    if len(climax_events) >= 20:
        lines.append("_Menampilkan 20 climax terakhir_")
    
    lines.append("")
    lines.append("💡 **Gunakan `/my-climax` untuk lihat statistik lengkap**")
    
    return "\n".join(lines)


__all__ = [
    'top_hts_command',
    'my_climax_command',
    'climax_history_command',
    'climax_history_callback',
    'climax_back_callback'
]
