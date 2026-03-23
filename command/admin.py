# command/admin.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Commands: /admin, /stats, /db-stats, /backup, /recover, /debug
=============================================================================
"""

import logging
import time
import asyncio
from typing import Optional, Dict, List, Any
from datetime import datetime

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from config import settings
from identity.manager import IdentityManager
from database.repository import Repository
from backup.automated import get_backup_manager
from backup.recovery import RecoveryManager
from utils.performance import get_performance_monitor

logger = logging.getLogger(__name__)


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /admin - Panel Admin
    """
    user_id = update.effective_user.id
    
    # Cek admin
    if user_id != settings.admin_id:
        await update.message.reply_text(
            "❌ **Akses Ditolak**\n\n"
            "Command ini hanya untuk admin bot.",
            parse_mode='HTML'
        )
        return
    
    identity_manager = IdentityManager()
    repo = Repository()
    perf_monitor = get_performance_monitor()
    
    # Dapatkan statistik
    db_stats = await repo.get_stats()
    perf_stats = perf_monitor.get_stats()
    characters = await identity_manager.get_all_characters()
    
    total_characters = len(characters)
    active_characters = sum(1 for c in characters if c.status == 'active')
    total_chats = sum(c.total_chats for c in characters)
    total_climax = sum(c.total_climax_bot + c.total_climax_user for c in characters)
    
    # Format response
    response = _format_admin_panel(
        db_stats=db_stats,
        perf_stats=perf_stats,
        total_characters=total_characters,
        active_characters=active_characters,
        total_chats=total_chats,
        total_climax=total_climax
    )
    
    # Keyboard
    keyboard = [
        [InlineKeyboardButton("📊 Statistik Bot", callback_data="admin_stats"),
         InlineKeyboardButton("🗄️ Statistik DB", callback_data="admin_db_stats")],
        [InlineKeyboardButton("🔍 Debug Info", callback_data="admin_debug"),
         InlineKeyboardButton("💾 Backup Manual", callback_data="admin_backup")],
        [InlineKeyboardButton("🔄 Recover", callback_data="admin_recover"),
         InlineKeyboardButton("🧹 Cleanup", callback_data="admin_cleanup")],
        [InlineKeyboardButton("❌ Tutup", callback_data="admin_close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(response, reply_markup=reply_markup, parse_mode='HTML')


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /stats - Statistik bot
    """
    user_id = update.effective_user.id
    
    # Cek admin
    if user_id != settings.admin_id:
        await update.message.reply_text(
            "❌ Command hanya untuk admin.",
            parse_mode='HTML'
        )
        return
    
    identity_manager = IdentityManager()
    perf_monitor = get_performance_monitor()
    
    characters = await identity_manager.get_all_characters()
    perf_stats = perf_monitor.get_stats()
    
    total_characters = len(characters)
    active_characters = sum(1 for c in characters if c.status == 'active')
    total_chats = sum(c.total_chats for c in characters)
    total_climax = sum(c.total_climax_bot + c.total_climax_user for c in characters)
    
    # Kelompokkan berdasarkan role
    by_role = {}
    for c in characters:
        role = c.role.value
        if role not in by_role:
            by_role[role] = {'count': 0, 'chats': 0, 'climax': 0}
        by_role[role]['count'] += 1
        by_role[role]['chats'] += c.total_chats
        by_role[role]['climax'] += c.total_climax_bot + c.total_climax_user
    
    # Format response
    response = _format_stats(
        total_characters=total_characters,
        active_characters=active_characters,
        total_chats=total_chats,
        total_climax=total_climax,
        by_role=by_role,
        perf_stats=perf_stats
    )
    
    await update.message.reply_text(response, parse_mode='HTML')


async def db_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /db-stats - Statistik database
    """
    user_id = update.effective_user.id
    
    # Cek admin
    if user_id != settings.admin_id:
        await update.message.reply_text(
            "❌ Command hanya untuk admin.",
            parse_mode='HTML'
        )
        return
    
    repo = Repository()
    db_stats = await repo.get_stats()
    
    response = _format_db_stats(db_stats)
    
    await update.message.reply_text(response, parse_mode='HTML')


async def backup_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /backup - Backup manual
    """
    user_id = update.effective_user.id
    
    # Cek admin
    if user_id != settings.admin_id:
        await update.message.reply_text(
            "❌ Command hanya untuk admin.",
            parse_mode='HTML'
        )
        return
    
    # Konfirmasi
    keyboard = [
        [InlineKeyboardButton("✅ Ya, Backup Sekarang", callback_data="backup_confirm"),
         InlineKeyboardButton("❌ Batal", callback_data="backup_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💾 **Backup Manual**\n\n"
        "Backup akan menyimpan semua data:\n"
        "• Database utama\n"
        "• Semua session\n"
        "• File konfigurasi\n\n"
        "**Yakin ingin melakukan backup sekarang?**",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def recover_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /recover - Restore dari backup
    """
    user_id = update.effective_user.id
    
    # Cek admin
    if user_id != settings.admin_id:
        await update.message.reply_text(
            "❌ Command hanya untuk admin.",
            parse_mode='HTML'
        )
        return
    
    backup_manager = get_backup_manager()
    backups = await backup_manager.get_backup_list()
    
    if not backups:
        await update.message.reply_text(
            "💾 **Recover**\n\n"
            "Tidak ada backup tersedia.\n"
            "Gunakan `/backup` untuk membuat backup.",
            parse_mode='HTML'
        )
        return
    
    # Tampilkan daftar backup
    keyboard = []
    for i, b in enumerate(backups[:10], 1):
        keyboard.append([
            InlineKeyboardButton(
                f"{i}. {b['filename']} ({b['date']})",
                callback_data=f"recover_select_{i}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("❌ Batal", callback_data="recover_cancel")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💾 **Pilih Backup untuk Restore**\n\n"
        "⚠️ **Peringatan:** Restore akan menimpa data saat ini!\n\n"
        "Pilih backup:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /debug - Info debug
    """
    user_id = update.effective_user.id
    
    # Cek admin
    if user_id != settings.admin_id:
        await update.message.reply_text(
            "❌ Command hanya untuk admin.",
            parse_mode='HTML'
        )
        return
    
    identity_manager = IdentityManager()
    current_reg = context.user_data.get('current_registration')
    
    debug_info = await _get_debug_info(identity_manager, current_reg)
    
    await update.message.reply_text(debug_info, parse_mode='HTML')


async def admin_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk statistik bot"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Cek admin
    if user_id != settings.admin_id:
        await query.edit_message_text("❌ Akses ditolak.", parse_mode='HTML')
        return
    
    identity_manager = IdentityManager()
    perf_monitor = get_performance_monitor()
    
    characters = await identity_manager.get_all_characters()
    perf_stats = perf_monitor.get_stats()
    
    total_characters = len(characters)
    active_characters = sum(1 for c in characters if c.status == 'active')
    total_chats = sum(c.total_chats for c in characters)
    total_climax = sum(c.total_climax_bot + c.total_climax_user for c in characters)
    
    by_role = {}
    for c in characters:
        role = c.role.value
        if role not in by_role:
            by_role[role] = {'count': 0, 'chats': 0, 'climax': 0}
        by_role[role]['count'] += 1
        by_role[role]['chats'] += c.total_chats
        by_role[role]['climax'] += c.total_climax_bot + c.total_climax_user
    
    response = _format_stats(
        total_characters=total_characters,
        active_characters=active_characters,
        total_chats=total_chats,
        total_climax=total_climax,
        by_role=by_role,
        perf_stats=perf_stats
    )
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(response, reply_markup=reply_markup, parse_mode='HTML')


async def admin_db_stats_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk statistik database"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Cek admin
    if user_id != settings.admin_id:
        await query.edit_message_text("❌ Akses ditolak.", parse_mode='HTML')
        return
    
    repo = Repository()
    db_stats = await repo.get_stats()
    
    response = _format_db_stats(db_stats)
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(response, reply_markup=reply_markup, parse_mode='HTML')


async def admin_debug_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk debug info"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Cek admin
    if user_id != settings.admin_id:
        await query.edit_message_text("❌ Akses ditolak.", parse_mode='HTML')
        return
    
    identity_manager = IdentityManager()
    current_reg = context.user_data.get('current_registration')
    
    debug_info = await _get_debug_info(identity_manager, current_reg)
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(debug_info, reply_markup=reply_markup, parse_mode='HTML')


async def admin_backup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk backup manual"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Cek admin
    if user_id != settings.admin_id:
        await query.edit_message_text("❌ Akses ditolak.", parse_mode='HTML')
        return
    
    backup_manager = get_backup_manager()
    
    # Lakukan backup
    backup_path = await backup_manager.create_backup()
    
    if backup_path:
        response = (
            f"💾 **Backup Berhasil!**\n\n"
            f"File: `{backup_path.name}`\n"
            f"Size: {backup_path.stat().st_size / (1024 * 1024):.2f} MB\n"
            f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Backup tersimpan di `{backup_path.parent}`"
        )
    else:
        response = "❌ **Backup Gagal!**\n\nCek log untuk detail error."
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(response, reply_markup=reply_markup, parse_mode='HTML')


async def admin_recover_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk recover"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Cek admin
    if user_id != settings.admin_id:
        await query.edit_message_text("❌ Akses ditolak.", parse_mode='HTML')
        return
    
    backup_manager = get_backup_manager()
    backups = await backup_manager.get_backup_list()
    
    if not backups:
        await query.edit_message_text(
            "💾 **Recover**\n\nTidak ada backup tersedia.",
            parse_mode='HTML'
        )
        return
    
    # Tampilkan daftar backup
    keyboard = []
    for i, b in enumerate(backups[:10], 1):
        keyboard.append([
            InlineKeyboardButton(
                f"{i}. {b['filename']} ({b['date']})",
                callback_data=f"recover_select_{i}"
            )
        ])
    
    keyboard.append([InlineKeyboardButton("🔙 Kembali", callback_data="admin_back")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "💾 **Pilih Backup untuk Restore**\n\n"
        "⚠️ **Peringatan:** Restore akan menimpa data saat ini!\n\n"
        "Pilih backup:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def admin_cleanup_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback untuk cleanup"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Cek admin
    if user_id != settings.admin_id:
        await query.edit_message_text("❌ Akses ditolak.", parse_mode='HTML')
        return
    
    # Konfirmasi
    keyboard = [
        [InlineKeyboardButton("✅ Ya, Cleanup", callback_data="cleanup_confirm"),
         InlineKeyboardButton("❌ Batal", callback_data="admin_back")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "🧹 **Cleanup Data**\n\n"
        "Aksi ini akan:\n"
        "• Menghapus karakter yang tidak aktif > 30 hari\n"
        "• Menyisakan 10 karakter teratas per role\n"
        "• Membersihkan memory lama\n\n"
        "⚠️ **Data yang dihapus tidak bisa dikembalikan!**\n\n"
        "**Yakin ingin melanjutkan?**",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def admin_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback kembali ke panel admin"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Cek admin
    if user_id != settings.admin_id:
        await query.edit_message_text("❌ Akses ditolak.", parse_mode='HTML')
        return
    
    # Panggil ulang admin panel
    identity_manager = IdentityManager()
    repo = Repository()
    perf_monitor = get_performance_monitor()
    
    db_stats = await repo.get_stats()
    perf_stats = perf_monitor.get_stats()
    characters = await identity_manager.get_all_characters()
    
    total_characters = len(characters)
    active_characters = sum(1 for c in characters if c.status == 'active')
    total_chats = sum(c.total_chats for c in characters)
    total_climax = sum(c.total_climax_bot + c.total_climax_user for c in characters)
    
    response = _format_admin_panel(
        db_stats=db_stats,
        perf_stats=perf_stats,
        total_characters=total_characters,
        active_characters=active_characters,
        total_chats=total_chats,
        total_climax=total_climax
    )
    
    keyboard = [
        [InlineKeyboardButton("📊 Statistik Bot", callback_data="admin_stats"),
         InlineKeyboardButton("🗄️ Statistik DB", callback_data="admin_db_stats")],
        [InlineKeyboardButton("🔍 Debug Info", callback_data="admin_debug"),
         InlineKeyboardButton("💾 Backup Manual", callback_data="admin_backup")],
        [InlineKeyboardButton("🔄 Recover", callback_data="admin_recover"),
         InlineKeyboardButton("🧹 Cleanup", callback_data="admin_cleanup")],
        [InlineKeyboardButton("❌ Tutup", callback_data="admin_close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(response, reply_markup=reply_markup, parse_mode='HTML')


async def admin_close_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback tutup panel admin"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "👑 **Admin Panel Ditutup**\n\n"
        "Ketik `/admin` untuk membuka lagi.",
        parse_mode='HTML'
    )


async def backup_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback konfirmasi backup"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Cek admin
    if user_id != settings.admin_id:
        await query.edit_message_text("❌ Akses ditolak.", parse_mode='HTML')
        return
    
    backup_manager = get_backup_manager()
    
    # Lakukan backup
    backup_path = await backup_manager.create_backup()
    
    if backup_path:
        response = (
            f"💾 **Backup Berhasil!**\n\n"
            f"File: `{backup_path.name}`\n"
            f"Size: {backup_path.stat().st_size / (1024 * 1024):.2f} MB\n"
            f"Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"Backup tersimpan di `{backup_path.parent}`"
        )
    else:
        response = "❌ **Backup Gagal!**\n\nCek log untuk detail error."
    
    keyboard = [[InlineKeyboardButton("🔙 Kembali", callback_data="admin_back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(response, reply_markup=reply_markup, parse_mode='HTML')


async def backup_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback batal backup"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "✅ **Backup dibatalkan.**",
        parse_mode='HTML'
    )
    
    # Kembali ke admin panel
    await admin_back_callback(update, context)


async def recover_select_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback pilih backup untuk recover"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    index = int(data.replace("recover_select_", "")) - 1
    
    backup_manager = get_backup_manager()
    backups = await backup_manager.get_backup_list()
    
    if index < 0 or index >= len(backups):
        await query.edit_message_text("❌ Backup tidak ditemukan.", parse_mode='HTML')
        return
    
    backup = backups[index]
    backup_path = backup_manager.backup_dir / backup['filename']
    
    # Konfirmasi
    keyboard = [
        [InlineKeyboardButton("✅ Ya, Restore", callback_data=f"recover_confirm_{index}"),
         InlineKeyboardButton("❌ Batal", callback_data="recover_cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"⚠️ **Konfirmasi Restore**\n\n"
        f"Backup: `{backup['filename']}`\n"
        f"Tanggal: {backup['date']}\n"
        f"Size: {backup['size_mb']} MB\n\n"
        f"**SEMUA DATA SAAT INI AKAN DITIMPA!**\n\n"
        f"Yakin ingin melanjutkan?",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )


async def recover_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback konfirmasi restore"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data
    
    index = int(data.replace("recover_confirm_", ""))
    
    backup_manager = get_backup_manager()
    backups = await backup_manager.get_backup_list()
    
    if index < 0 or index >= len(backups):
        await query.edit_message_text("❌ Backup tidak ditemukan.", parse_mode='HTML')
        return
    
    backup = backups[index]
    backup_path = backup_manager.backup_dir / backup['filename']
    
    recovery_manager = RecoveryManager(backup_manager)
    
    await query.edit_message_text(
        "🔄 **Restore sedang berjalan...**\n\n"
        "Mohon tunggu, proses ini bisa memakan waktu beberapa menit.",
        parse_mode='HTML'
    )
    
    try:
        result = await recovery_manager.restore_backup(backup_path)
        
        if result['success']:
            response = (
                f"✅ **Restore Berhasil!**\n\n"
                f"Backup: `{backup['filename']}`\n"
                f"Files restored: {result.get('files_restored', 0)}\n\n"
                f"Bot akan restart dalam beberapa detik..."
            )
        else:
            response = f"❌ **Restore Gagal!**\n\n{result.get('error', 'Unknown error')}"
        
        await query.edit_message_text(response, parse_mode='HTML')
        
    except Exception as e:
        logger.error(f"Restore failed: {e}")
        await query.edit_message_text(
            f"❌ **Restore Gagal!**\n\n{str(e)}",
            parse_mode='HTML'
        )


async def recover_cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback batal restore"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "✅ **Restore dibatalkan.**",
        parse_mode='HTML'
    )
    
    # Kembali ke admin panel
    await admin_back_callback(update, context)


async def cleanup_confirm_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Callback konfirmasi cleanup"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Cek admin
    if user_id != settings.admin_id:
        await query.edit_message_text("❌ Akses ditolak.", parse_mode='HTML')
        return
    
    identity_manager = IdentityManager()
    
    await query.edit_message_text(
        "🧹 **Cleanup sedang berjalan...**\n\n"
        "Menghapus data lama...",
        parse_mode='HTML'
    )
    
    await identity_manager.cleanup_old_characters()
    
    await query.edit_message_text(
        "✅ **Cleanup Selesai!**\n\n"
        "• Karakter tidak aktif > 30 hari dihapus\n"
        "• Hanya 10 karakter teratas per role yang disimpan\n\n"
        "Data bersih!",
        parse_mode='HTML'
    )


def _format_admin_panel(
    db_stats: Dict,
    perf_stats: Dict,
    total_characters: int,
    active_characters: int,
    total_chats: int,
    total_climax: int
) -> str:
    """Format admin panel"""
    
    uptime = perf_stats.get('uptime', 0)
    uptime_hours = int(uptime / 3600)
    uptime_minutes = int((uptime % 3600) / 60)
    
    return (
        "👑 **ADMIN PANEL - AMORIA**\n\n"
        f"👤 **Admin ID:** `{settings.admin_id}`\n"
        f"📊 **Karakter:** {total_characters} total, {active_characters} aktif\n"
        f"💬 **Total Chat:** {total_chats}\n"
        f"💦 **Total Climax:** {total_climax}\n"
        f"⏱️ **Uptime:** {uptime_hours}j {uptime_minutes}m\n"
        f"📈 **Response Time:** {perf_stats.get('response_time', {}).get('avg', 0):.2f}s\n"
        f"💾 **Database Size:** {db_stats.get('db_size_mb', 0):.2f} MB\n\n"
        f"**Pilih menu di bawah:**"
    )


def _format_stats(
    total_characters: int,
    active_characters: int,
    total_chats: int,
    total_climax: int,
    by_role: Dict,
    perf_stats: Dict
) -> str:
    """Format statistik bot"""
    
    lines = [
        "📊 **STATISTIK BOT**\n",
        f"👤 **Karakter:** {total_characters} total, {active_characters} aktif",
        f"💬 **Total Chat:** {total_chats}",
        f"💦 **Total Climax:** {total_climax}",
        "",
        "📈 **Response Time:**",
        f"• Rata-rata: {perf_stats.get('response_time', {}).get('avg', 0):.2f}s",
        f"• Maks: {perf_stats.get('response_time', {}).get('max', 0):.2f}s",
        f"• p95: {perf_stats.get('response_time', {}).get('p95', 0):.2f}s",
        "",
        "🎭 **Per Role:**"
    ]
    
    for role, data in by_role.items():
        lines.append(f"• **{role.upper()}:** {data['count']} karakter, {data['chats']} chat, {data['climax']} climax")
    
    return "\n".join(lines)


def _format_db_stats(db_stats: Dict) -> str:
    """Format statistik database"""
    
    lines = [
        "🗄️ **STATISTIK DATABASE**\n",
        f"📁 **Database Size:** {db_stats.get('db_size_mb', 0):.2f} MB",
        "",
        "📊 **Tabel:**"
    ]
    
    for key, value in db_stats.items():
        if key.endswith('_count'):
            table = key.replace('_count', '')
            lines.append(f"• **{table}:** {value} baris")
    
    if db_stats.get('active_registrations', 0) > 0:
        lines.append(f"\n🟢 **Aktif:** {db_stats.get('active_registrations', 0)} registrasi aktif")
    
    if db_stats.get('total_chats_all_time', 0) > 0:
        lines.append(f"💬 **Total Chat:** {db_stats.get('total_chats_all_time', 0)}")
    
    return "\n".join(lines)


async def _get_debug_info(identity_manager: IdentityManager, current_reg: Optional[Dict]) -> str:
    """Dapatkan info debug"""
    
    import platform
    import sys
    
    characters = await identity_manager.get_all_characters()
    
    debug_info = [
        "🔍 **DEBUG INFO**\n",
        "**System:**",
        f"• Python: {sys.version}",
        f"• Platform: {platform.platform()}",
        "",
        "**Bot:**",
        f"• Admin ID: {settings.admin_id}",
        f"• AI Model: {settings.ai.model}",
        f"• Database: {settings.database.type}",
        "",
        "**Characters:**",
        f"• Total: {len(characters)}",
    ]
    
    if current_reg:
        debug_info.append("")
        debug_info.append("**Current Character:**")
        debug_info.append(f"• ID: {current_reg.get('id')}")
        debug_info.append(f"• Role: {current_reg.get('role')}")
        debug_info.append(f"• Bot: {current_reg.get('bot_name')}")
        debug_info.append(f"• User: {current_reg.get('user_name')}")
    
    return "\n".join(debug_info)


__all__ = [
    'admin_command',
    'stats_command',
    'db_stats_command',
    'backup_command',
    'recover_command',
    'debug_command',
    'admin_stats_callback',
    'admin_db_stats_callback',
    'admin_debug_callback',
    'admin_backup_callback',
    'admin_recover_callback',
    'admin_cleanup_callback',
    'admin_back_callback',
    'admin_close_callback',
    'backup_confirm_callback',
    'backup_cancel_callback',
    'recover_select_callback',
    'recover_confirm_callback',
    'recover_cancel_callback',
    'cleanup_confirm_callback'
]
