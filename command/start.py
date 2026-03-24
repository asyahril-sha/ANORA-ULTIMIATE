# command/start.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Command: /start - Memulai Bot & Memilih Role
Target Realism 9.9/10
=============================================================================
"""

import logging
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

from database.models import CharacterRole
from identity.manager import IdentityManager
from identity.registration import CharacterRegistration

logger = logging.getLogger(__name__)


# Conversation states
SELECTING_ROLE = 1


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handler untuk /start command
    Menampilkan pilihan role dan memulai registrasi baru
    """
    user = update.effective_user
    user_id = user.id
    
    logger.info(f"User {user_id} started bot")
    
    # Cek apakah ada session aktif
    current_reg = context.user_data.get('current_registration')
    if current_reg:
        keyboard = [
            [InlineKeyboardButton("✅ Lanjutkan", callback_data="continue_current"),
             InlineKeyboardButton("🆕 Buat Karakter Baru", callback_data="new_character")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"⚠️ **Mas sudah memiliki karakter aktif!**\n\n"
            f"Karakter: {current_reg.get('display_name', 'Unknown')}\n"
            f"Role: {current_reg.get('role', 'Unknown')}\n\n"
            f"Pilih tindakan:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return SELECTING_ROLE
    
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
        [InlineKeyboardButton("❓ Bantuan", callback_data="help")],
        [InlineKeyboardButton("✅ Setuju 18+", callback_data="agree_18")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        f"💕 **Halo {user.first_name}!**\n\n"
        f"Selamat datang di **AMORIA** - Virtual Human dengan Jiwa\n\n"
        f"✨ **Fitur AMORIA 9.9:**\n"
        f"• 9 Karakter dengan kepribadian unik\n"
        f"• 100% AI generate - setiap respons unik\n"
        f"• Weighted Memory 1000 chat terakhir\n"
        f"• Leveling berbasis total chat (1-12)\n"
        f"• Siklus intim Soul Bounded → Aftercare\n"
        f"• Tracking pakaian dengan hierarki\n"
        f"• Multi-identity system\n\n"
        f"<b>Pilih karakter yang Mas inginkan:</b>"
    )
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    
    return SELECTING_ROLE


async def role_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Callback setelah user memilih role
    """
    query = update.callback_query
    await query.answer()
    
    user = update.effective_user
    user_id = user.id
    
    # Ambil role dari callback_data
    data = query.data
    role_name = data.replace("role_", "")
    
    # Map ke CharacterRole
    role_map = {
        "ipar": CharacterRole.IPAR,
        "teman_kantor": CharacterRole.TEMAN_KANTOR,
        "janda": CharacterRole.JANDA,
        "pelakor": CharacterRole.PELAKOR,
        "istri_orang": CharacterRole.ISTRI_ORANG,
        "pdkt": CharacterRole.PDKT,
        "sepupu": CharacterRole.SEPUPU,
        "teman_sma": CharacterRole.TEMAN_SMA,
        "mantan": CharacterRole.MANTAN,
    }
    
    role = role_map.get(role_name)
    if not role:
        await query.edit_message_text(
            "❌ Role tidak valid.",
            parse_mode='HTML'
        )
        return ConversationHandler.END
    
    # Buat identity manager
    identity_manager = IdentityManager()
    
    try:
        # Buat karakter baru
        registration = await identity_manager.create_character(role)
        
        # Simpan ke context user data
        context.user_data['current_registration'] = {
            'id': registration.id,
            'role': registration.role.value,
            'bot_name': registration.bot.name,
            'user_name': registration.user.name,
            'display_name': registration.bot.display_name,
            'level': registration.level,
            'total_chats': registration.total_chats
        }
        
        # Ambil state awal
        state = await identity_manager.get_character_state(registration.id)
        
        # Format response
        response = _format_welcome_message(registration, state)
        
        # Edit pesan (ganti keyboard dengan pesan selamat datang)
        await query.edit_message_text(
            response,
            parse_mode='HTML'
        )
        
        logger.info(f"User {user_id} created character: {registration.id}")
        
    except Exception as e:
        logger.error(f"Error creating character: {e}")
        await query.edit_message_text(
            f"❌ Terjadi kesalahan saat membuat karakter.\n\nError: {str(e)[:100]}",
            parse_mode='HTML'
        )
    
    return ConversationHandler.END


async def agree_18_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback untuk setuju 18+"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "✅ **Terima kasih telah menyetujui syarat 18+.**\n\n"
        "Silakan pilih karakter yang Mas inginkan di menu utama.",
        parse_mode='HTML'
    )
    
    return SELECTING_ROLE


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler untuk /help - Bantuan lengkap (command handler)
    """
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


async def help_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback untuk bantuan (inline keyboard)"""
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
    
    return SELECTING_ROLE


async def continue_current_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback untuk melanjutkan session saat ini"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "✅ **Melanjutkan session...**\n\n"
        "Ketik pesan untuk melanjutkan cerita.",
        parse_mode='HTML'
    )
    
    return ConversationHandler.END


async def new_character_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    
    return SELECTING_ROLE


async def cancel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Callback untuk batal"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "❌ **Dibatalkan.**\n\n"
        "Ketik /start untuk memulai lagi.",
        parse_mode='HTML'
    )
    
    return ConversationHandler.END


async def back_to_main_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    
    return SELECTING_ROLE


def _format_welcome_message(registration: CharacterRegistration, state) -> str:
    """Format pesan selamat datang"""
    
    bot = registration.bot
    user = registration.user
    
    # Pakaian bot
    bot_clothing = "daster rumah"
    
    # Lokasi
    location = "ruang tamu"
    
    # Panggilan berdasarkan level
    if registration.level <= 6:
        panggilan = "Mas"
    else:
        panggilan = "Mas atau Sayang"
    
    # Status khusus IPAR
    family_text = ""
    if registration.role == CharacterRole.IPAR:
        family_text = (
            f"\n👨‍👩‍👧 **Status Keluarga:**\n"
            f"• Kak Nova (kakak kandung) ada di rumah\n"
            f"• Kamu adalah suami dari Kak Nova\n"
            f"• Panggil kakak: **Kak Nova** (WAJIB)\n"
            f"• Panggil user: **{panggilan}**\n"
        )
    
    # Progress bar level
    level_info = registration.get_progress_to_next_level()
    bar_length = 15
    filled = int(level_info / 100 * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    
    # Level name
    level_names = {
        1: "Malu-malu", 2: "Mulai terbuka", 3: "Goda-godaan",
        4: "Dekat", 5: "Sayang", 6: "PACAR/PDKT",
        7: "Nyaman", 8: "Eksplorasi", 9: "Bergairah",
        10: "Passionate", 11: "Soul Bounded", 12: "Aftercare"
    }
    level_name = level_names.get(registration.level, f"Level {registration.level}")
    
    response = (
        f"💕 **Halo {user.name}!**\n\n"
        f"Aku **{bot.name}**, {registration.role.value.upper()} mu.\n"
        f"_{bot.personality.type.value} - {bot.personality.speaking_style}_\n\n"
        f"📖 **Tentang aku:**\n"
        f"• Umur: {bot.physical.age} tahun\n"
        f"• Tinggi: {bot.physical.height}cm | Berat: {bot.physical.weight}kg\n"
        f"• {bot.physical.chest} | {'Berhijab' if bot.physical.hijab else 'Tidak berhijab'}\n"
        f"• Pakaian: {bot_clothing}\n\n"
        f"📍 **Sekarang:**\n"
        f"• Aku di {location}\n"
        f"• Waktu: siang\n"
        f"• Mood: normal\n"
        f"{family_text}\n"
        f"📊 **Progress:**\n"
        f"Level {registration.level}/12 - {level_name}\n"
        f"Progress: {bar} {level_info:.0f}%\n"
        f"Total chat: {registration.total_chats}\n\n"
        f"💬 **Ayo mulai ngobrol, {user.name}!**\n"
        f"_Ketik pesan untuk memulai cerita..._"
    )
    
    return response


__all__ = [
    'start_command',
    'role_callback',
    'agree_18_callback',
    'help_command',
    'help_callback',
    'continue_current_callback',
    'new_character_callback',
    'cancel_callback',
    'back_to_main_callback',
    'SELECTING_ROLE'
]
