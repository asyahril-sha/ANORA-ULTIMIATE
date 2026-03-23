# command/memory.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Commands: /memory, /flashback - Ringkasan Memory & Flashback
Target Realism 9.9/10
=============================================================================
"""

import logging
import random
from typing import Dict, List, Any
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from identity.manager import IdentityManager

logger = logging.getLogger(__name__)


# =============================================================================
# MEMORY COMMAND
# =============================================================================

async def memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /memory - Ringkasan memory karakter dengan weighted stats
    """
    user_id = update.effective_user.id
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await update.message.reply_text(
            "❌ **Tidak ada karakter aktif**\n\n"
            "Ketik `/start` untuk memilih karakter, atau `/sessions` untuk melanjutkan karakter tersimpan.",
            parse_mode='HTML'
        )
        return
    
    registration_id = current_reg.get('id')
    bot_name = current_reg.get('bot_name')
    
    identity_manager = IdentityManager()
    
    # Dapatkan memory
    working_memories = await identity_manager.repo.get_working_memory(registration_id, limit=1000)
    long_term_memories = await identity_manager.repo.get_long_term_memory(registration_id, limit=200)
    
    # Hitung weighted stats
    weighted_stats = await _calculate_weighted_stats(working_memories)
    
    # Kelompokkan long term memory
    milestones = [m for m in long_term_memories if m.get('type') == 'milestone']
    promises = [m for m in long_term_memories if m.get('type') == 'promise' and m.get('status') == 'pending']
    plans = [m for m in long_term_memories if m.get('type') == 'plan' and m.get('status') == 'pending']
    preferences = [m for m in long_term_memories if m.get('type') == 'preference']
    
    response = _format_memory_summary_99(
        bot_name=bot_name,
        total_chats=current_reg.get('total_chats', 0),
        weighted_stats=weighted_stats,
        milestones=milestones,
        promises=promises,
        plans=plans,
        preferences=preferences
    )
    
    keyboard = [
        [InlineKeyboardButton("📜 Chat Terakhir", callback_data="memory_chat"),
         InlineKeyboardButton("🏆 Milestone", callback_data="memory_milestone")],
        [InlineKeyboardButton("📝 Janji & Rencana", callback_data="memory_promises"),
         InlineKeyboardButton("💖 Preferensi", callback_data="memory_preferences")],
        [InlineKeyboardButton("📊 Weighted Stats", callback_data="memory_weighted"),
         InlineKeyboardButton("🎭 Flashback", callback_data="flashback_random")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='HTML')


# =============================================================================
# FLASHBACK COMMAND
# =============================================================================

async def flashback_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /flashback - Flashback random dari memory
    """
    user_id = update.effective_user.id
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await update.message.reply_text(
            "❌ **Tidak ada karakter aktif**\n\n"
            "Ketik `/start` untuk memilih karakter, atau `/sessions` untuk melanjutkan karakter tersimpan.",
            parse_mode='HTML'
        )
        return
    
    registration_id = current_reg.get('id')
    bot_name = current_reg.get('bot_name')
    
    identity_manager = IdentityManager()
    
    # Dapatkan memory
    working_memories = await identity_manager.repo.get_working_memory(registration_id, limit=1000)
    long_term_memories = await identity_manager.repo.get_long_term_memory(registration_id, limit=200)
    
    # Kumpulkan momen penting dari working memory (importance > 0.7)
    important_moments = []
    for mem in working_memories:
        if mem.get('importance', 0) >= 0.7:
            important_moments.append({
                'type': 'working',
                'user': mem['user'],
                'bot': mem['bot'],
                'timestamp': mem['timestamp'],
                'importance': mem.get('importance', 0)
            })
    
    # Kumpulkan milestone dari long term memory
    milestones = [m for m in long_term_memories if m.get('type') == 'milestone']
    for m in milestones:
        important_moments.append({
            'type': 'milestone',
            'content': m.get('content', ''),
            'timestamp': m.get('timestamp', 0),
            'importance': 0.8
        })
    
    # Kumpulkan janji dan rencana
    promises = [p for p in long_term_memories if p.get('type') == 'promise' and p.get('status') == 'pending']
    plans = [p for p in long_term_memories if p.get('type') == 'plan' and p.get('status') == 'pending']
    
    for p in promises:
        important_moments.append({
            'type': 'promise',
            'content': p.get('content', ''),
            'timestamp': p.get('timestamp', 0),
            'importance': 0.75
        })
    
    for p in plans:
        important_moments.append({
            'type': 'plan',
            'content': p.get('content', ''),
            'timestamp': p.get('timestamp', 0),
            'importance': 0.7
        })
    
    if not important_moments:
        await update.message.reply_text(
            f"🎭 **FLASHBACK**\n\n"
            f"Belum ada kenangan yang cukup berarti dengan {bot_name}.\n\n"
            f"Buat lebih banyak momen spesial agar bisa flashback!",
            parse_mode='HTML'
        )
        return
    
    # Urutkan berdasarkan importance dan timestamp
    important_moments.sort(key=lambda x: (x['importance'], x['timestamp']), reverse=True)
    
    # Pilih flashback random dari top 20
    top_moments = important_moments[:20]
    selected = random.choice(top_moments)
    
    # Format flashback
    time_str = datetime.fromtimestamp(selected['timestamp']).strftime("%d %b %Y, %H:%M")
    
    if selected['type'] == 'milestone':
        flashback_text = f"""
🏆 **FLASHBACK: MOMEN SPESIAL** 🏆

*{time_str}*

{selected.get('content', '')}

💭 Kenangan indah bersama {bot_name}...
"""
    elif selected['type'] == 'promise':
        flashback_text = f"""
📝 **FLASHBACK: JANJI** 📝

*{time_str}*

"{selected.get('content', '')}"

💭 Masih ingat janji ini? Belum ditepati nih...
"""
    elif selected['type'] == 'plan':
        flashback_text = f"""
📅 **FLASHBACK: RENCANA** 📅

*{time_str}*

"{selected.get('content', '')}"

💭 Rencana ini masih pending. Kapan kita realisasikan?
"""
    else:
        user_snippet = selected.get('user', '')[:100]
        bot_snippet = selected.get('bot', '')[:100]
        flashback_text = f"""
💭 **FLASHBACK** 💭

*{time_str}*

👤 Kamu: "{user_snippet}"

🤖 {bot_name}: "{bot_snippet}"

💌 Kenangan ini masih teringat sampai sekarang...
"""
    
    # Keyboard untuk lihat flashback lain
    keyboard = [[InlineKeyboardButton("🎭 Flashback Lain", callback_data="flashback_random")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(flashback_text, reply_markup=reply_markup, parse_mode='HTML')


# =============================================================================
# CALLBACK HANDLERS
# =============================================================================

async def memory_chat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk lihat chat terakhir"""
    query = update.callback_query
    await query.answer()
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await query.edit_message_text("❌ Tidak ada karakter aktif.", parse_mode='HTML')
        return
    
    registration_id = current_reg.get('id')
    
    identity_manager = IdentityManager()
    working_memories = await identity_manager.repo.get_working_memory(registration_id, limit=20)
    
    if not working_memories:
        await query.edit_message_text("📜 **CHAT TERAKHIR**\n\nBelum ada percakapan.", parse_mode='HTML')
        return
    
    lines = ["📜 **CHAT TERAKHIR**\n"]
    for mem in reversed(working_memories[-10:]):
        time_str = datetime.fromtimestamp(mem['timestamp']).strftime("%H:%M")
        lines.append(f"*[{time_str}]* 👤 {mem['user'][:80]}")
        lines.append(f"   🤖 {mem['bot'][:80]}\n")
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="memory_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("\n".join(lines), reply_markup=reply_markup, parse_mode='HTML')


async def memory_milestone_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk lihat milestone"""
    query = update.callback_query
    await query.answer()
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await query.edit_message_text("❌ Tidak ada karakter aktif.", parse_mode='HTML')
        return
    
    registration_id = current_reg.get('id')
    
    identity_manager = IdentityManager()
    long_term_memories = await identity_manager.repo.get_long_term_memory(registration_id, limit=200)
    
    milestones = [m for m in long_term_memories if m.get('type') == 'milestone']
    
    if not milestones:
        await query.edit_message_text("🏆 **MILESTONE**\n\nBelum ada milestone.", parse_mode='HTML')
        return
    
    lines = ["🏆 **MILESTONE**\n"]
    for m in milestones[-10:]:
        time_str = datetime.fromtimestamp(m['timestamp']).strftime("%d %b %Y")
        lines.append(f"*[{time_str}]* {m.get('content', '')[:80]}")
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="memory_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("\n".join(lines), reply_markup=reply_markup, parse_mode='HTML')


async def memory_promises_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk lihat janji dan rencana"""
    query = update.callback_query
    await query.answer()
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await query.edit_message_text("❌ Tidak ada karakter aktif.", parse_mode='HTML')
        return
    
    registration_id = current_reg.get('id')
    
    identity_manager = IdentityManager()
    long_term_memories = await identity_manager.repo.get_long_term_memory(registration_id, limit=200)
    
    promises = [p for p in long_term_memories if p.get('type') == 'promise' and p.get('status') == 'pending']
    plans = [p for p in long_term_memories if p.get('type') == 'plan' and p.get('status') == 'pending']
    
    lines = []
    
    if promises:
        lines.append("📝 **JANJI YANG BELUM DITEPATI:**\n")
        for p in promises[:5]:
            time_str = datetime.fromtimestamp(p['timestamp']).strftime("%d %b")
            lines.append(f"• [{time_str}] {p.get('content', '')[:80]}")
    
    if plans:
        lines.append("\n📅 **RENCANA:**\n")
        for p in plans[:5]:
            time_str = datetime.fromtimestamp(p['timestamp']).strftime("%d %b")
            lines.append(f"• [{time_str}] {p.get('content', '')[:80]}")
    
    if not promises and not plans:
        lines.append("📝 **JANJI & RENCANA**\n\nBelum ada janji atau rencana.")
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="memory_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("\n".join(lines), reply_markup=reply_markup, parse_mode='HTML')


async def memory_preferences_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk lihat preferensi"""
    query = update.callback_query
    await query.answer()
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await query.edit_message_text("❌ Tidak ada karakter aktif.", parse_mode='HTML')
        return
    
    registration_id = current_reg.get('id')
    
    identity_manager = IdentityManager()
    long_term_memories = await identity_manager.repo.get_long_term_memory(registration_id, limit=200)
    
    preferences = [p for p in long_term_memories if p.get('type') == 'preference']
    
    if not preferences:
        await query.edit_message_text("💖 **PREFERENSI**\n\nBelum ada data preferensi.", parse_mode='HTML')
        return
    
    lines = ["💖 **PREFERENSI**\n"]
    for p in preferences[:10]:
        lines.append(f"• {p.get('content', '')[:80]}")
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="memory_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("\n".join(lines), reply_markup=reply_markup, parse_mode='HTML')


async def memory_weighted_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk lihat weighted stats"""
    query = update.callback_query
    await query.answer()
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await query.edit_message_text("❌ Tidak ada karakter aktif.", parse_mode='HTML')
        return
    
    registration_id = current_reg.get('id')
    
    identity_manager = IdentityManager()
    working_memories = await identity_manager.repo.get_working_memory(registration_id, limit=1000)
    
    weighted_stats = await _calculate_weighted_stats(working_memories)
    
    response = _format_weighted_stats(weighted_stats)
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="memory_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(response, reply_markup=reply_markup, parse_mode='HTML')


async def flashback_random_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk flashback random"""
    query = update.callback_query
    await query.answer()
    
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await query.edit_message_text("❌ Tidak ada karakter aktif.", parse_mode='HTML')
        return
    
    registration_id = current_reg.get('id')
    bot_name = current_reg.get('bot_name')
    
    identity_manager = IdentityManager()
    
    working_memories = await identity_manager.repo.get_working_memory(registration_id, limit=1000)
    long_term_memories = await identity_manager.repo.get_long_term_memory(registration_id, limit=200)
    
    important_moments = []
    for mem in working_memories:
        if mem.get('importance', 0) >= 0.7:
            important_moments.append({
                'type': 'working',
                'user': mem['user'],
                'bot': mem['bot'],
                'timestamp': mem['timestamp'],
                'importance': mem.get('importance', 0)
            })
    
    milestones = [m for m in long_term_memories if m.get('type') == 'milestone']
    for m in milestones:
        important_moments.append({
            'type': 'milestone',
            'content': m.get('content', ''),
            'timestamp': m.get('timestamp', 0),
            'importance': 0.8
        })
    
    if not important_moments:
        await query.edit_message_text(
            f"🎭 Belum ada kenangan berarti dengan {bot_name}.",
            parse_mode='HTML'
        )
        return
    
    important_moments.sort(key=lambda x: (x['importance'], x['timestamp']), reverse=True)
    selected = random.choice(important_moments[:20])
    
    time_str = datetime.fromtimestamp(selected['timestamp']).strftime("%d %b %Y, %H:%M")
    
    if selected['type'] == 'milestone':
        flashback_text = f"""
🏆 **FLASHBACK: MOMEN SPESIAL** 🏆

*{time_str}*

{selected.get('content', '')}

💭 Kenangan indah bersama {bot_name}...
"""
    else:
        user_snippet = selected.get('user', '')[:100]
        bot_snippet = selected.get('bot', '')[:100]
        flashback_text = f"""
💭 **FLASHBACK** 💭

*{time_str}*

👤 Kamu: "{user_snippet}"

🤖 {bot_name}: "{bot_snippet}"

💌 Kenangan ini masih teringat sampai sekarang...
"""
    
    keyboard = [[InlineKeyboardButton("🎭 Flashback Lain", callback_data="flashback_random")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(flashback_text, reply_markup=reply_markup, parse_mode='HTML')


async def memory_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback kembali ke menu memory"""
    query = update.callback_query
    await query.answer()
    
    # Panggil ulang memory command
    await memory_command(update, context)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def _calculate_weighted_stats(working_memories: List[Dict]) -> Dict:
    """Hitung weighted stats dari working memory"""
    if not working_memories:
        return {'total': 0, 'avg_importance': 0, 'high': 0, 'medium': 0, 'low': 0}
    
    total = len(working_memories)
    importance_sum = sum(m.get('importance', 0.3) for m in working_memories)
    avg_importance = importance_sum / total
    
    high = sum(1 for m in working_memories if m.get('importance', 0) >= 0.7)
    medium = sum(1 for m in working_memories if 0.4 <= m.get('importance', 0) < 0.7)
    low = sum(1 for m in working_memories if m.get('importance', 0) < 0.4)
    
    top_important = sorted(working_memories, key=lambda x: x.get('importance', 0), reverse=True)[:5]
    
    return {
        'total': total,
        'avg_importance': round(avg_importance, 2),
        'high': high,
        'medium': medium,
        'low': low,
        'top_important': [
            {'user': m['user'][:80], 'importance': m.get('importance', 0)}
            for m in top_important
        ]
    }


def _format_memory_summary_99(
    bot_name: str,
    total_chats: int,
    weighted_stats: Dict,
    milestones: List[Dict],
    promises: List[Dict],
    plans: List[Dict],
    preferences: List[Dict]
) -> str:
    """Format ringkasan memory dengan weighted stats"""
    
    bar_length = 20
    filled = int(weighted_stats['avg_importance'] * bar_length)
    importance_bar = "⭐" * filled + "·" * (bar_length - filled)
    
    emotional_count = len([m for m in milestones if m.get('emotional_tag')])
    
    return (
        f"🧠 **MEMORY {bot_name.upper()}**\n\n"
        f"📊 **Statistik:**\n"
        f"• Total Chat: {total_chats}\n"
        f"• Working Memory: {min(weighted_stats['total'], 1000)} chat\n"
        f"• Weighted Importance: {importance_bar} {weighted_stats['avg_importance']:.0%}\n"
        f"  - Penting (>70%): {weighted_stats['high']}\n"
        f"  - Sedang (40-70%): {weighted_stats['medium']}\n"
        f"  - Biasa (<40%): {weighted_stats['low']}\n"
        f"• Milestone: {len(milestones)} momen spesial\n"
        f"• Memory Emosional: {emotional_count} momen\n"
        f"• Janji Tertunda: {len(promises)}\n"
        f"• Rencana: {len(plans)}\n"
        f"• Preferensi: {len(preferences)} item\n\n"
        f"💡 Bot ingat {min(weighted_stats['total'], 1000)} chat terakhir dengan weighted importance.\n"
        f"   Momen penting (⭐) lebih diingat daripada obrolan biasa.\n"
        f"   Bot juga ingat semua momen spesial sepanjang hubungan.\n\n"
        f"_Pilih kategori untuk melihat detail:_"
    )


def _format_weighted_stats(weighted_stats: Dict) -> str:
    """Format weighted stats untuk display"""
    if weighted_stats['total'] == 0:
        return "📊 **WEIGHTED STATS**\n\nBelum ada data cukup."
    
    lines = ["📊 **WEIGHTED STATS**\n"]
    lines.append(f"📈 **Total Chat:** {weighted_stats['total']}")
    lines.append(f"⭐ **Rata-rata Importance:** {weighted_stats['avg_importance']:.0%}")
    lines.append("")
    lines.append("📊 **Distribusi:**")
    lines.append(f"   • Tinggi (>70%): {weighted_stats['high']} chat")
    lines.append(f"   • Sedang (40-70%): {weighted_stats['medium']} chat")
    lines.append(f"   • Rendah (<40%): {weighted_stats['low']} chat")
    lines.append("")
    
    if weighted_stats['top_important']:
        lines.append("🏆 **TOP 5 MOMEN PENTING:**")
        for i, m in enumerate(weighted_stats['top_important'], 1):
            lines.append(f"{i}. [{m['importance']:.0%}] {m['user'][:60]}")
    
    return "\n".join(lines)


__all__ = [
    'memory_command',
    'flashback_command',
    'memory_chat_callback',
    'memory_milestone_callback',
    'memory_promises_callback',
    'memory_preferences_callback',
    'memory_weighted_callback',
    'flashback_random_callback',
    'memory_back_callback'
]
