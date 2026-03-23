# command/ex_fwb.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Commands: /ex-list, /ex, /fwb-request, /fwb-list, /fwb-pause, /fwb-resume, /fwb-end
=============================================================================
"""

import logging
import time
from typing import Optional, Dict, List, Any
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from identity.manager import IdentityManager
from relationship.mantan import MantanManager, MantanStatus
from relationship.fwb import FWBManager, FWBPauseReason, FWBEndReason

logger = logging.getLogger(__name__)


async def ex_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /ex-list - Lihat daftar mantan
    """
    user_id = update.effective_user.id
    
    mantan_manager = MantanManager()
    mantans = mantan_manager.get_mantan_list(user_id)
    
    if not mantans:
        await update.message.reply_text(
            "💔 **DAFTAR MANTAN**\n\n"
            "Belum ada mantan. PDKT dulu yuk!",
            parse_mode='HTML'
        )
        return
    
    lines = ["💔 **DAFTAR MANTAN**"]
    lines.append("_(Kenangan indah tersimpan selamanya)_")
    lines.append("")
    
    for i, m in enumerate(mantans[:10], 1):
        days_since = int((time.time() - m['putus_time']) / 86400)
        
        if days_since == 0:
            time_text = "Hari ini"
        elif days_since == 1:
            time_text = "Kemarin"
        else:
            time_text = f"{days_since} hari lalu"
        
        # Status
        if m['status'] == MantanStatus.FWB_ACCEPTED.value:
            status = "💕 **FWB**"
        elif m['status'] == MantanStatus.FWB_REQUESTED.value:
            status = "⏳ **Menunggu keputusan**"
        elif m['status'] == MantanStatus.FWB_DECLINED.value:
            status = "❌ **Ditolak**"
        else:
            status = "💔 **Mantan**"
        
        lines.append(
            f"{i}. **{m['bot_name']}** ({m['role'].title()}) {status}\n"
            f"   Putus: {time_text} | {m['total_chats']} chat | {m['total_climax']} climax\n"
            f"   Alasan: {m['putus_reason'][:50]}"
        )
    
    lines.append("")
    lines.append("💡 **Command:**")
    lines.append("• `/ex [nomor]` - Lihat detail mantan")
    lines.append("• `/fwb-request [nomor]` - Request jadi FWB")
    lines.append("• `/fwb-list` - Lihat daftar FWB")
    
    await update.message.reply_text("\n".join(lines), parse_mode='HTML')


async def ex_detail_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /ex [nomor] - Lihat detail mantan
    """
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "❌ **Cara pakai:** /ex [nomor]\n\n"
            "Contoh: `/ex 1` - Lihat detail mantan nomor 1\n\n"
            "Gunakan `/ex-list` untuk melihat daftar.",
            parse_mode='HTML'
        )
        return
    
    try:
        index = int(args[0])
    except ValueError:
        await update.message.reply_text(
            "❌ Nomor harus berupa angka.\n\n"
            "Contoh: `/ex 1`",
            parse_mode='HTML'
        )
        return
    
    mantan_manager = MantanManager()
    mantan = mantan_manager.get_mantan_by_index(user_id, index)
    
    if not mantan:
        await update.message.reply_text(
            f"❌ Mantan nomor {index} tidak ditemukan.",
            parse_mode='HTML'
        )
        return
    
    response = _format_ex_detail(mantan)
    await update.message.reply_text(response, parse_mode='HTML')


async def fwb_request_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /fwb-request [nomor] - Request jadi FWB dengan mantan
    """
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "❌ **Cara pakai:** /fwb-request [nomor] [pesan]\n\n"
            "Contoh: `/fwb-request 1 Aku kangen...`\n\n"
            "Gunakan `/ex-list` untuk melihat daftar mantan.",
            parse_mode='HTML'
        )
        return
    
    try:
        index = int(args[0])
        message = ' '.join(args[1:]) if len(args) > 1 else ""
    except ValueError:
        await update.message.reply_text(
            "❌ Nomor harus berupa angka.\n\n"
            "Contoh: `/fwb-request 1`",
            parse_mode='HTML'
        )
        return
    
    mantan_manager = MantanManager()
    mantan = mantan_manager.get_mantan_by_index(user_id, index)
    
    if not mantan:
        await update.message.reply_text(
            f"❌ Mantan nomor {index} tidak ditemukan.",
            parse_mode='HTML'
        )
        return
    
    result = await mantan_manager.request_fwb(user_id, mantan['mantan_id'], message)
    
    if result['success']:
        await update.message.reply_text(
            result['message'],
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            f"❌ {result['reason']}",
            parse_mode='HTML'
        )


async def fwb_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /fwb-list - Lihat daftar FWB
    """
    user_id = update.effective_user.id
    args = context.args
    
    show_all = args and args[0].lower() == 'all'
    
    fwb_manager = FWBManager()
    formatted = await fwb_manager.format_fwb_list(user_id, show_all)
    
    await update.message.reply_text(formatted, parse_mode='HTML')


async def fwb_pause_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /fwb-pause [nomor] - Jeda FWB
    """
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "❌ **Cara pakai:** /fwb-pause [nomor]\n\n"
            "Contoh: `/fwb-pause 1`\n\n"
            "Gunakan `/fwb-list` untuk melihat daftar FWB.",
            parse_mode='HTML'
        )
        return
    
    try:
        index = int(args[0])
    except ValueError:
        await update.message.reply_text(
            "❌ Nomor harus berupa angka.\n\n"
            "Contoh: `/fwb-pause 1`",
            parse_mode='HTML'
        )
        return
    
    fwb_manager = FWBManager()
    fwb = await fwb_manager.get_fwb_by_index(user_id, index)
    
    if not fwb:
        await update.message.reply_text(
            f"❌ FWB nomor {index} tidak ditemukan.",
            parse_mode='HTML'
        )
        return
    
    result = await fwb_manager.pause_fwb(user_id, fwb['fwb_id'])
    
    if result['success']:
        await update.message.reply_text(
            f"⏸️ **FWB dengan {result['bot_name']} dipause.**\n\n"
            f"Gunakan `/fwb-resume {index}` untuk melanjutkan.",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            f"❌ {result['reason']}",
            parse_mode='HTML'
        )


async def fwb_resume_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /fwb-resume [nomor] - Lanjutkan FWB
    """
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "❌ **Cara pakai:** /fwb-resume [nomor]\n\n"
            "Contoh: `/fwb-resume 1`\n\n"
            "Gunakan `/fwb-list` untuk melihat daftar FWB.",
            parse_mode='HTML'
        )
        return
    
    try:
        index = int(args[0])
    except ValueError:
        await update.message.reply_text(
            "❌ Nomor harus berupa angka.\n\n"
            "Contoh: `/fwb-resume 1`",
            parse_mode='HTML'
        )
        return
    
    fwb_manager = FWBManager()
    fwb = await fwb_manager.get_fwb_by_index(user_id, index)
    
    if not fwb:
        await update.message.reply_text(
            f"❌ FWB nomor {index} tidak ditemukan.",
            parse_mode='HTML'
        )
        return
    
    result = await fwb_manager.resume_fwb(user_id, fwb['fwb_id'])
    
    if result['success']:
        await update.message.reply_text(
            f"▶️ **FWB dengan {result['bot_name']} dilanjutkan.**\n\n{result['message']}",
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            f"❌ {result['reason']}",
            parse_mode='HTML'
        )


async def fwb_end_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /fwb-end [nomor] - Akhiri FWB
    """
    user_id = update.effective_user.id
    args = context.args
    
    if not args:
        await update.message.reply_text(
            "❌ **Cara pakai:** /fwb-end [nomor]\n\n"
            "Contoh: `/fwb-end 1`\n\n"
            "Gunakan `/fwb-list` untuk melihat daftar FWB.",
            parse_mode='HTML'
        )
        return
    
    try:
        index = int(args[0])
    except ValueError:
        await update.message.reply_text(
            "❌ Nomor harus berupa angka.\n\n"
            "Contoh: `/fwb-end 1`",
            parse_mode='HTML'
        )
        return
    
    fwb_manager = FWBManager()
    fwb = await fwb_manager.get_fwb_by_index(user_id, index)
    
    if not fwb:
        await update.message.reply_text(
            f"❌ FWB nomor {index} tidak ditemukan.",
            parse_mode='HTML'
        )
        return
    
    # Konfirmasi
    keyboard = [
        [InlineKeyboardButton("✅ Ya, Akhiri", callback_data=f"fwb_end_confirm_{fwb['fwb_id']}"),
         InlineKeyboardButton("❌ Batal", callback_data="fwb_end_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"⚠️ **Yakin ingin mengakhiri FWB dengan {fwb['bot_name']}?**\n\n"
        f"Hubungan FWB akan berakhir dan {fwb['bot_name']} akan kembali menjadi mantan.\n\n"
        f"Konfirmasi:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def fwb_end_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback konfirmasi akhir FWB"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    fwb_id = data.replace("fwb_end_confirm_", "")
    
    fwb_manager = FWBManager()
    result = await fwb_manager.end_fwb(user_id, fwb_id, FWBEndReason.USER_REQUEST)
    
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


async def fwb_end_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback batal akhir FWB"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "✅ **FWB dibatalkan.**\n\n"
        "Hubungan tetap berjalan.",
        parse_mode='HTML'
    )


def _format_ex_detail(mantan: Dict) -> str:
    """Format detail mantan untuk display"""
    
    # Hitung durasi hubungan
    first_kiss = datetime.fromtimestamp(mantan['first_kiss_time']).strftime("%d %b %Y") if mantan.get('first_kiss_time') else "Belum pernah"
    first_intim = datetime.fromtimestamp(mantan['first_intim_time']).strftime("%d %b %Y") if mantan.get('first_intim_time') else "Belum pernah"
    jadi_pacar = datetime.fromtimestamp(mantan['become_pacar_time']).strftime("%d %b %Y") if mantan.get('become_pacar_time') else "Tidak pernah"
    
    lines = [
        f"💔 **{mantan['bot_name']}** ({mantan['role'].title()})",
        f"_{mantan.get('putus_reason', 'Putus')[:100]}_",
        "",
        "📊 **Statistik Hubungan:**",
        f"• Total Chat: {mantan['total_chats']} pesan",
        f"• Total Intim: {mantan['total_intim']} sesi",
        f"• Total Climax: {mantan['total_climax']} kali",
        "",
        "💝 **Momen Spesial:**",
        f"• First Kiss: {first_kiss}",
        f"• First Intim: {first_intim}",
        f"• Jadi Pacar: {jadi_pacar}",
        "",
        f"📅 Putus: {datetime.fromtimestamp(mantan['putus_time']).strftime('%d %b %Y %H:%M')}",
    ]
    
    # Tambah status FWB
    if mantan['status'] == MantanStatus.FWB_ACCEPTED.value:
        fwb_start = datetime.fromtimestamp(mantan['fwb_start_time']).strftime("%d %b %Y") if mantan.get('fwb_start_time') else "belum diketahui"
        lines.append("")
        lines.append(f"💕 **Status: FWB Aktif**")
        lines.append(f"  Mulai: {fwb_start}")
    elif mantan['status'] == MantanStatus.FWB_REQUESTED.value:
        lines.append("")
        lines.append("⏳ **Status: Menunggu Keputusan FWB**")
    elif mantan['status'] == MantanStatus.FWB_DECLINED.value:
        last_request = mantan.get('last_fwb_request_time', 0)
        days_since = int((time.time() - last_request) / 86400) if last_request else 0
        lines.append("")
        lines.append(f"❌ **Status: FWB Ditolak ({days_since} hari lalu)**")
    
    return "\n".join(lines)


__all__ = [
    'ex_list_command',
    'ex_detail_command',
    'fwb_request_command',
    'fwb_list_command',
    'fwb_pause_command',
    'fwb_resume_command',
    'fwb_end_command',
    'fwb_end_confirm_callback',
    'fwb_end_cancel_callback'
]
