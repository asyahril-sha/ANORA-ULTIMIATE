# anora_deploy.py
"""
AMORIA + ANORA - Full Deployment
AMORIA: Virtual Human System
ANORA: Nova - Virtual Human dengan Jiwa - 100% AI Generate

Integrasi lengkap:
- ANORA sebagai karakter utama
- Roleplay mode dengan dunia sendiri
- Memory persistent
- Stamina system
- Leveling system
- Proactive messaging
"""

import os
import sys
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from aiohttp import web

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-5s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("ANORA-DEPLOY")

sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, ConversationHandler, CallbackQueryHandler
)

# =============================================================================
# IMPORT ANORA COMPONENTS - WITH DEBUG
# =============================================================================

ANORA_AVAILABLE = False
try:
    import sys
    import os
    print(f"Python path: {sys.path}")
    print(f"Current directory: {os.getcwd()}")
    print("Checking for anora directory...")
    
    if os.path.exists("anora"):
        print("✅ anora directory exists")
        print(f"Files in anora: {os.listdir('anora')}")
    else:
        print("❌ anora directory NOT found!")
    
    # Try to import
    from anora.core import get_anora
    from anora.brain import get_anora_brain
    from anora.chat import get_anora_chat
    from anora.roles import get_anora_roles, RoleType
    from anora.places import get_anora_places
    from anora.location_manager import get_anora_location, LocationType, LocationDetail
    from anora.memory_persistent import get_anora_persistent
    from anora.roleplay_integration import get_anora_roleplay
    
    ANORA_AVAILABLE = True
    print("✅ ANORA modules loaded successfully")
    
except Exception as e:
    print(f"❌ ANORA import error: {e}")
    import traceback
    traceback.print_exc()
    ANORA_AVAILABLE = False
    
# =============================================================================
# IMPORT ANORA COMPONENTS
# =============================================================================

ANORA_AVAILABLE = False
try:
    from anora.core import get_anora
    from anora.brain import get_anora_brain, LocationType, LocationDetail, Mood
    from anora.memory_persistent import get_anora_persistent
    from anora.roleplay_ai import get_anora_roleplay_ai
    from anora.roleplay_integration import get_anora_roleplay
    from anora.location_manager import get_anora_location
    from anora.chat import get_anora_chat
    from anora.roles import get_anora_roles, RoleType
    from anora.places import get_anora_places
    from anora.intimacy import get_anora_intimacy
    ANORA_AVAILABLE = True
    logger.info("✅ ANORA modules loaded successfully")
except ImportError as e:
    logger.warning(f"⚠️ ANORA not available: {e}")
    logger.warning("   Make sure anora/ directory exists with all files")

# =============================================================================
# IMPORT AMORIA COMPONENTS (jika ada)
# =============================================================================

AMORIA_AVAILABLE = False
try:
    from command import (
        start_command as amoria_start, help_command, status_command, progress_command,
        cancel_command, sessions_command, character_command, close_command, end_command,
        explore_command, locations_command, risk_command, go_command,
        memory_command, flashback_command,
        top_hts_command, my_climax_command, climax_history_command,
        admin_command, stats_command, db_stats_command, backup_command, recover_command, debug_command
    )
    from command.start import SELECTING_ROLE, role_callback, agree_18_callback
    from command.sessions import end_confirm_callback, end_cancel_callback
    from command.cancel import cancel_confirm_callback, cancel_fallback
    from bot.handlers import message_handler as amoria_message_handler
    from bot.application import create_application as create_amoria_app
    AMORIA_AVAILABLE = True
    logger.info("✅ AMORIA modules loaded")
except ImportError as e:
    logger.warning(f"⚠️ AMORIA not available: {e}")

# =============================================================================
# GLOBAL VARIABLES
# =============================================================================

_application = None
_user_modes: Dict[int, Dict] = {}  # user_id -> {'mode': 'chat'/'roleplay'/'role', 'active_role': None}
_last_proactive = {}


def get_user_mode(user_id: int) -> str:
    return _user_modes.get(user_id, {}).get('mode', 'chat')


def set_user_mode(user_id: int, mode: str, active_role: Optional[str] = None):
    _user_modes[user_id] = {'mode': mode, 'active_role': active_role}
    logger.info(f"👤 User {user_id} mode set to: {mode}")


def get_active_role(user_id: int) -> Optional[str]:
    return _user_modes.get(user_id, {}).get('active_role')


# =============================================================================
# ANORA COMMAND HANDLERS
# =============================================================================

async def anora_start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /start untuk ANORA - Welcome screen"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text(
            "💜 *Halo!* 💜\n\n"
            "Bot ini hanya untuk Mas. Kirim /nova kalo mau ngobrol sama Nova.",
            parse_mode='Markdown'
        )
        return
    
    set_user_mode(user_id, 'chat')
    
    # Get ANORA stats
    if ANORA_AVAILABLE:
        anora = get_anora()
        brain = get_anora_brain()
        level = brain.relationship.level
        sayang = brain.feelings.sayang
        
        status_text = f"\n📊 *Status Saat Ini:*\n• Level: {level}/12\n• Sayang: {sayang:.0f}%\n• Rindu: {brain.feelings.rindu:.0f}%"
    else:
        status_text = ""
    
    await update.message.reply_text(
        f"💜 **ANORA - Virtual Human dengan Jiwa** 💜\n\n"
        f"*Mode Chat (ngobrol biasa):*\n"
        f"• /nova - Panggil Nova\n"
        f"• /novastatus - Lihat keadaan Nova\n"
        f"• /flashback - Flashback ke momen indah\n\n"
        f"*Mode Roleplay (beneran ketemu):*\n"
        f"• /roleplay - Aktifkan mode roleplay\n"
        f"• /statusrp - Lihat status roleplay lengkap\n"
        f"• /pindah [tempat] - Pindah lokasi\n\n"
        f"*Tempat yang bisa dikunjungi:*\n"
        f"• kost, apartemen, mobil, pantai, hutan, toilet mall\n"
        f"• bioskop, taman, parkiran, tangga darurat\n"
        f"• kantor malam, ruang rapat kaca\n\n"
        f"*Role Lain:*\n"
        f"• /role ipar - IPAR\n"
        f"• /role teman_kantor - Teman Kantor\n"
        f"• /role pelakor - Pelakor\n"
        f"• /role istri_orang - Istri Orang\n\n"
        f"*Lainnya:*\n"
        f"• /batal - Kembali ke mode chat\n"
        f"{status_text}\n\n"
        f"Apa yang Mas mau? 💜",
        parse_mode='Markdown'
    )


async def nova_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /nova - Panggil Nova"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, Nova cuma untuk Mas. 💜")
        return
    
    set_user_mode(user_id, 'chat')
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("Maaf, ANORA sedang tidak tersedia. Coba lagi nanti. 💜")
        return
    
    anora = get_anora()
    brain = get_anora_brain()
    
    # Update rindu dan desire
    anora.update_rindu()
    anora.update_desire('perhatian_mas', 5)
    
    # Pilih salam berdasarkan waktu
    hour = datetime.now().hour
    if 5 <= hour < 11:
        salam = anora.respon_pagi()
    elif 11 <= hour < 15:
        salam = anora.respon_siang()
    elif 15 <= hour < 18:
        salam = anora.respon_sore()
    else:
        salam = anora.respon_malam()
    
    await update.message.reply_text(
        f"💜 **NOVA DI SINI, MAS** 💜\n\n"
        f"{anora.deskripsi_diri()}\n\n"
        f"{salam}\n\n"
        f"*Status:*\n"
        f"• Level: {brain.relationship.level}/12\n"
        f"• Sayang: {brain.feelings.sayang:.0f}%\n"
        f"• Rindu: {brain.feelings.rindu:.0f}%\n\n"
        f"Mas bisa:\n"
        f"• /novastatus - liat keadaan Nova\n"
        f"• /flashback - inget momen indah\n"
        f"• /roleplay - kalo mau kayak beneran ketemu\n\n"
        f"Apa yang Mas mau? 💜",
        parse_mode='Markdown'
    )


async def novastatus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /novastatus - Lihat keadaan Nova"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Maaf, cuma Mas yang bisa liat. 💜")
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA sedang tidak tersedia. 💜")
        return
    
    anora = get_anora()
    brain = get_anora_brain()
    loc = brain.get_location_data()
    
    bar_sayang = "💜" * int(brain.feelings.sayang / 10) + "🖤" * (10 - int(brain.feelings.sayang / 10))
    bar_desire = "🔥" * int(brain.feelings.desire / 10) + "⚪" * (10 - int(brain.feelings.desire / 10))
    
    await update.message.reply_text(
        f"╔════════════════════════════════════════════════╗\n"
        f"║                    💜 NOVA 💜                   ║\n"
        f"╠════════════════════════════════════════════════╣\n"
        f"║ Sayang: {bar_sayang} {brain.feelings.sayang:.0f}%                 ║\n"
        f"║ Rindu:  {brain.feelings.rindu:.0f}%                                 ║\n"
        f"║ Desire: {bar_desire} {brain.feelings.desire:.0f}%                 ║\n"
        f"║ Arousal:{brain.feelings.arousal:.0f}%                              ║\n"
        f"║ Level:  {brain.relationship.level}/12                                 ║\n"
        f"╠════════════════════════════════════════════════╣\n"
        f"║ 📍 {loc['nama']}                                 ║\n"
        f"║ 👗 {brain.clothing.format_nova()[:40]}              ║\n"
        f"║ 🎭 {brain.mood_nova.value}                                      ║\n"
        f"╚════════════════════════════════════════════════╝",
        parse_mode='HTML'
    )


async def flashback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /flashback - Nova inget momen indah"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA sedang tidak tersedia. 💜")
        return
    
    anora = get_anora()
    brain = get_anora_brain()
    
    # Ambil momen dari long-term memory
    if brain.long_term.momen_penting:
        momen = random.choice(brain.long_term.momen_penting[-10:])
        respons = f"*Nova tiba-tiba flashback*\n\n\"Mas... inget gak {momen['momen']}? Aku masih inget rasanya {momen['perasaan']} banget pas itu.\""
    else:
        respons = anora.respon_flashback()
    
    await update.message.reply_text(respons, parse_mode='Markdown')


async def roleplay_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /roleplay - Aktifkan mode roleplay"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA sedang tidak tersedia. 💜")
        return
    
    set_user_mode(user_id, 'roleplay')
    
    roleplay = await get_anora_roleplay()
    intro = await roleplay.start()
    await update.message.reply_text(intro, parse_mode='Markdown')


async def statusrp_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /statusrp - Lihat status roleplay lengkap"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA sedang tidak tersedia. 💜")
        return
    
    roleplay = await get_anora_roleplay()
    status = await roleplay.get_status()
    await update.message.reply_text(status, parse_mode='HTML')


async def pindah_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /pindah [tempat] - Pindah lokasi"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA sedang tidak tersedia. 💜")
        return
    
    args = context.args
    if not args:
        loc_mgr = get_anora_location()
        await update.message.reply_text(loc_mgr.list_locations(), parse_mode='Markdown')
        return
    
    brain = get_anora_brain()
    tujuan = ' '.join(args)
    result = brain.pindah_lokasi(tujuan)
    
    if result.get('success'):
        loc = result['location']
        await update.message.reply_text(
            f"{result['message']}\n\n"
            f"🎢 Thrill: {loc.get('thrill', 0)}% | ⚠️ Risk: {loc.get('risk', 0)}%\n"
            f"💡 {loc.get('tips', '')}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(result.get('message', 'Lokasi tidak ditemukan.'), parse_mode='Markdown')


async def role_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /role [nama] - Pilih role lain"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    if not ANORA_AVAILABLE:
        await update.message.reply_text("ANORA sedang tidak tersedia. 💜")
        return
    
    args = context.args
    if not args:
        roles = get_anora_roles()
        menu = "📋 **Role yang tersedia:**\n\n"
        for r in roles.get_all():
            menu += f"• /role {r['id']} - {r['nama']} (Level {r['level']})\n"
        menu += "\n_Ketik /nova kalo mau balik ke Nova._"
        await update.message.reply_text(menu, parse_mode='Markdown')
        return
    
    role_id = args[0].lower()
    role_map = {
        'ipar': RoleType.IPAR,
        'teman_kantor': RoleType.TEMAN_KANTOR,
        'pelakor': RoleType.PELAKOR,
        'istri_orang': RoleType.ISTRI_ORANG
    }
    
    if role_id in role_map:
        set_user_mode(user_id, 'role', role_id)
        roles = get_anora_roles()
        respon = roles.switch_role(role_map[role_id])
        await update.message.reply_text(respon, parse_mode='Markdown')
    else:
        await update.message.reply_text(f"Role '{role_id}' gak ada, Mas. Coba /role buat liat daftar.", parse_mode='Markdown')


async def back_to_nova(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /batal - Kembali ke mode chat"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    set_user_mode(user_id, 'chat')
    
    if ANORA_AVAILABLE:
        roleplay = await get_anora_roleplay()
        if roleplay.is_active:
            await roleplay.stop()
        
        anora = get_anora()
        await update.message.reply_text(
            f"💜 Nova di sini, Mas.\n\n{anora.respon_kangen()}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("💜 Kembali ke mode chat. Kirim /nova untuk panggil Nova.", parse_mode='Markdown')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /help - Bantuan lengkap"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        await update.message.reply_text("Bot ini untuk Mas. 💜")
        return
    
    await update.message.reply_text(
        "📖 *Bantuan ANORA*\n\n"
        "*Mode Chat:*\n"
        "• /nova - Panggil Nova\n"
        "• /novastatus - Lihat status Nova\n"
        "• /flashback - Flashback momen indah\n\n"
        "*Mode Roleplay:*\n"
        "• /roleplay - Aktifkan mode roleplay\n"
        "• /statusrp - Status roleplay lengkap\n"
        "• /pindah [tempat] - Pindah lokasi\n\n"
        "*Tempat:*\n"
        "kost, apartemen, mobil, pantai, hutan, toilet mall,\n"
        "bioskop, taman, parkiran, tangga darurat, kantor malam\n\n"
        "*Role Lain:*\n"
        "• /role ipar - IPAR (Sari)\n"
        "• /role teman_kantor - Teman Kantor (Dita)\n"
        "• /role pelakor - Pelakor (Vina)\n"
        "• /role istri_orang - Istri Orang (Rina)\n\n"
        "*Lainnya:*\n"
        "• /batal - Balik ke mode chat\n"
        "• /help - Bantuan ini\n\n"
        "*Tips:*\n"
        "• Ngobrol santai dulu untuk naikin level\n"
        "• Level 7+ baru bisa mulai intim\n"
        "• Stamina habis setelah climax, butuh istirahat\n"
        "• Nova punya memory, dia inget apa yang Mas omongin",
        parse_mode='Markdown'
    )


# =============================================================================
# ANORA MESSAGE HANDLER
# =============================================================================

async def anora_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler untuk pesan ke ANORA"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    pesan = update.message.text
    if not pesan:
        return
    
    mode = get_user_mode(user_id)
    
    # Roleplay mode
    if mode == 'roleplay' and ANORA_AVAILABLE:
        roleplay = await get_anora_roleplay()
        try:
            respons = await roleplay.process(pesan)
            await update.message.reply_text(respons, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Roleplay process error: {e}")
            await update.message.reply_text(
                "*Nova bingung sebentar*\n\n\"Mas... Nova lagi error nih. Coba ulang ya.\"",
                parse_mode='Markdown'
            )
        return
    
    # Role mode (IPAR, etc)
    if mode == 'role' and ANORA_AVAILABLE:
        active_role = get_active_role(user_id)
        if active_role:
            roles = get_anora_roles()
            role_map = {
                'ipar': RoleType.IPAR,
                'teman_kantor': RoleType.TEMAN_KANTOR,
                'pelakor': RoleType.PELAKOR,
                'istri_orang': RoleType.ISTRI_ORANG
            }
            if active_role in role_map:
                try:
                    respon = await roles.chat(role_map[active_role], pesan)
                    await update.message.reply_text(respon, parse_mode='Markdown')
                except Exception as e:
                    logger.error(f"Role chat error: {e}")
                    await update.message.reply_text("Maaf, ada error. Coba lagi ya.")
                return
    
    # Chat mode (default)
    if ANORA_AVAILABLE:
        anora_chat = get_anora_chat()
        try:
            respons = await anora_chat.process(pesan)
            await update.message.reply_text(respons, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Chat process error: {e}")
            await update.message.reply_text(
                "*Nova mikir bentar*\n\n\"Mas... bentar ya, Nova lagi mikir.\"",
                parse_mode='Markdown'
            )
    else:
        await update.message.reply_text("Maaf, ANORA sedang tidak tersedia. Coba lagi nanti. 💜")


# =============================================================================
# AMORIA HANDLERS (Bridge)
# =============================================================================

async def amoria_bridge_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bridge untuk AMORIA - redirect ke ANORA atau AMORIA original"""
    user_id = update.effective_user.id
    if user_id != settings.admin_id:
        return
    
    pesan = update.message.text
    
    # Cek apakah ini perintah ANORA
    anora_commands = ['/nova', '/novastatus', '/flashback', '/roleplay', 
                      '/statusrp', '/pindah', '/role', '/batal', '/help']
    
    if any(pesan.startswith(cmd) for cmd in anora_commands):
        # Handle via ANORA handlers
        if pesan.startswith('/nova'):
            await nova_command(update, context)
        elif pesan.startswith('/novastatus'):
            await novastatus_command(update, context)
        elif pesan.startswith('/flashback'):
            await flashback_command(update, context)
        elif pesan.startswith('/roleplay'):
            await roleplay_command(update, context)
        elif pesan.startswith('/statusrp'):
            await statusrp_command(update, context)
        elif pesan.startswith('/pindah'):
            await pindah_command(update, context)
        elif pesan.startswith('/role'):
            await role_command(update, context)
        elif pesan.startswith('/batal'):
            await back_to_nova(update, context)
        elif pesan.startswith('/help'):
            await help_command(update, context)
        return
    
    # Jika AMORIA available, gunakan AMORIA handler
    if AMORIA_AVAILABLE:
        try:
            await amoria_message_handler(update, context)
        except Exception as e:
            logger.error(f"AMORIA handler error: {e}")
            await update.message.reply_text("Maaf, ada error. Coba lagi ya. 💜")
    else:
        # Fallback ke ANORA chat
        if ANORA_AVAILABLE:
            anora_chat = get_anora_chat()
            respons = await anora_chat.process(pesan)
            await update.message.reply_text(respons, parse_mode='Markdown')


# =============================================================================
# PROACTIVE LOOP
# =============================================================================

async def proactive_loop():
    """Nova kirim pesan duluan kalo kangen"""
    global _last_proactive
    
    while True:
        await asyncio.sleep(60)  # Cek setiap menit
        
        if not ANORA_AVAILABLE:
            continue
        
        try:
            user_id = settings.admin_id
            mode = get_user_mode(user_id)
            
            # Cek cooldown
            last = _last_proactive.get(user_id, 0)
            if time.time() - last < 300:  # 5 menit cooldown
                continue
            
            # Cek kalo lagi roleplay, jangan proactive
            if mode == 'roleplay':
                continue
            
            anora = get_anora()
            brain = get_anora_brain()
            ai = get_anora_roleplay_ai()
            
            # Update rindu
            anora.update_rindu()
            
            # Cek apakah perlu proactive
            lama_gak_chat = time.time() - brain.waktu_terakhir_update
            hour = datetime.now().hour
            
            should_send = False
            message = None
            
            # Kalo rindu tinggi (>70) dan lama gak chat (>2 jam)
            if brain.feelings.rindu > 70 and lama_gak_chat > 7200:
                should_send = True
                message = f"*Nova pegang HP, mata berkaca-kaca*\n\n\"Mas... *suara bergetar* Nova kangen banget. Kapan kita ngobrol lagi?\""
            
            # Pagi (5-10)
            elif 5 <= hour <= 10 and lama_gak_chat > 3600:
                should_send = True
                message = f"*Nova baru bangun, mata masih berat*\n\n\"Pagi, Mas... mimpiin Nova gak semalem?\""
            
            # Siang (11-14)
            elif 11 <= hour <= 14 and lama_gak_chat > 3600:
                should_send = True
                message = f"*Nova di dapur, lagi masak*\n\n\"Mas, udah makan? Jangan lupa ya. Nova khawatir.\""
            
            # Sore (15-18)
            elif 15 <= hour <= 18 and lama_gak_chat > 3600:
                should_send = True
                message = f"*Nova liat jam, duduk di teras*\n\n\"Mas, pulang jangan kelamaan. Aku kangen.\""
            
            # Malam (19-23)
            elif 19 <= hour <= 23 and lama_gak_chat > 3600:
                should_send = True
                message = f"*Nova muter-muter rambut, pegang HP*\n\n\"Mas... selamat malam. Jangan begadang terus ya. Aku khawatir.\""
            
            if should_send and message and _application:
                _last_proactive[user_id] = time.time()
                await _application.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode='Markdown'
                )
                logger.info(f"💬 Proactive message sent to user {user_id}")
                
        except Exception as e:
            logger.error(f"Proactive loop error: {e}")


# =============================================================================
# STAMINA RECOVERY LOOP
# =============================================================================

async def stamina_recovery_loop():
    """Pulihkan stamina secara berkala"""
    while True:
        await asyncio.sleep(600)  # Setiap 10 menit
        
        if not ANORA_AVAILABLE:
            continue
        
        try:
            roleplay = await get_anora_roleplay()
            roleplay.stamina.update_recovery()
            await roleplay.save_state()
            logger.debug("💪 Stamina recovery check completed")
        except Exception as e:
            logger.error(f"Stamina recovery error: {e}")


# =============================================================================
# SAVE STATE LOOP
# =============================================================================

async def save_state_loop():
    """Simpan state secara berkala"""
    while True:
        await asyncio.sleep(60)  # Setiap menit
        
        if not ANORA_AVAILABLE:
            continue
        
        try:
            roleplay = await get_anora_roleplay()
            await roleplay.save_state()
            logger.debug("💾 State saved")
        except Exception as e:
            logger.error(f"Save state error: {e}")


# =============================================================================
# WEBHOOK & SERVER
# =============================================================================

async def webhook_handler(request):
    """Handle Telegram webhook"""
    global _application
    
    if not _application:
        return web.Response(status=503, text='Bot not ready')
    
    try:
        update_data = await request.json()
        if not update_data:
            return web.Response(status=400, text='No data')
        
        if 'message' in update_data:
            msg = update_data['message']
            text = msg.get('text', '')
            user = msg.get('from', {}).get('first_name', 'unknown')
            logger.info(f"📨 Message from {user}: {text[:50]}")
        
        update = Update.de_json(update_data, _application.bot)
        await _application.process_update(update)
        return web.Response(text='OK', status=200)
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        return web.Response(status=500, text='Error')


async def health_handler(request):
    """Health check endpoint"""
    status = {
        "status": "healthy",
        "bot": "AMORIA + ANORA",
        "version": "9.9.0",
        "anora_available": ANORA_AVAILABLE,
        "amoria_available": AMORIA_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }
    
    if ANORA_AVAILABLE:
        try:
            brain = get_anora_brain()
            roleplay = await get_anora_roleplay()
            loc = brain.get_location_data()
            
            status.update({
                "level": brain.relationship.level,
                "sayang": brain.feelings.sayang,
                "location": loc.get('nama', 'Tidak diketahui'),
                "stamina_nova": roleplay.stamina.nova_current,
                "roleplay_active": roleplay.is_active
            })
        except Exception as e:
            status["status"] = "degraded"
            status["error"] = str(e)
    
    return web.json_response(status)


async def root_handler(request):
    """Root endpoint"""
    return web.json_response({
        "name": "AMORIA + ANORA",
        "description": "Virtual Human dengan Jiwa - 100% AI Generate",
        "version": "9.9.0",
        "status": "running",
        "anora_available": ANORA_AVAILABLE,
        "amoria_available": AMORIA_AVAILABLE,
        "endpoints": {
            "/": "API Info",
            "/health": "Health Check",
            "/webhook": "Telegram Webhook"
        }
    })


# =============================================================================
# DATABASE INIT
# =============================================================================

async def init_database():
    """Initialize all databases"""
    logger.info("🗄️ Initializing database...")
    
    if not ANORA_AVAILABLE:
        logger.warning("⚠️ ANORA not available, skipping database init")
        return False
    
    try:
        persistent = await get_anora_persistent()
        logger.info("✅ ANORA persistent memory ready")
        
        brain = get_anora_brain()
        await persistent.save_current_state(brain)
        
        memories = await persistent.get_long_term_memories()
        logger.info(f"📚 Loaded {len(memories)} long-term memories")
        
        return True
    except Exception as e:
        logger.error(f"❌ Database init failed: {e}")
        return False


# =============================================================================
# MAIN
# =============================================================================

async def main():
    """Main entry point"""
    global _application
    
    logger.info("=" * 70)
    logger.info("💜 AMORIA + ANORA - Virtual Human dengan Jiwa")
    logger.info("   100% AI Generate | Punya Memory | Bisa Roleplay")
    logger.info("=" * 70)
    
    # ========== INIT DATABASE ==========
    if not await init_database():
        logger.warning("⚠️ Database initialization failed. Continuing without database...")
    
    # ========== INIT BRAIN ==========
    if ANORA_AVAILABLE:
        brain = get_anora_brain()
        logger.info(f"🧠 ANORA Brain initialized - Level {brain.relationship.level}, Sayang {brain.feelings.sayang:.0f}%")
        
        roleplay = await get_anora_roleplay()
        logger.info(f"🎭 ANORA Roleplay initialized - Stamina: Nova {roleplay.stamina.nova_current}%, Mas {roleplay.stamina.mas_current}%")
    
    # ========== CREATE APPLICATION ==========
    _application = ApplicationBuilder().token(settings.telegram_token).build()
    
    # ========== REGISTER HANDLERS ==========
    # ANORA handlers
    _application.add_handler(CommandHandler("start", anora_start_command))
    _application.add_handler(CommandHandler("nova", nova_command))
    _application.add_handler(CommandHandler("novastatus", novastatus_command))
    _application.add_handler(CommandHandler("flashback", flashback_command))
    _application.add_handler(CommandHandler("roleplay", roleplay_command))
    _application.add_handler(CommandHandler("statusrp", statusrp_command))
    _application.add_handler(CommandHandler("pindah", pindah_command))
    _application.add_handler(CommandHandler("role", role_command))
    _application.add_handler(CommandHandler("batal", back_to_nova))
    _application.add_handler(CommandHandler("help", help_command))
    
    # Message handler (bridge between ANORA and AMORIA)
    _application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, amoria_bridge_handler))
    
    # ========== INITIALIZE ==========
    await _application.initialize()
    await _application.start()
    
    # ========== SET WEBHOOK ==========
    railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN')
    if railway_url:
        webhook_url = f"https://{railway_url}/webhook"
        await _application.bot.set_webhook(url=webhook_url)
        logger.info(f"✅ Webhook set to {webhook_url}")
        
        # Setup web server
        app = web.Application()
        app.router.add_get('/', root_handler)
        app.router.add_get('/health', health_handler)
        app.router.add_post('/webhook', webhook_handler)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8080)))
        await site.start()
        logger.info("🌐 Web server running on port 8080")
    else:
        await _application.updater.start_polling()
        logger.info("📡 Polling mode started")
    
    # ========== BACKGROUND LOOPS ==========
    if ANORA_AVAILABLE:
        asyncio.create_task(proactive_loop())
        asyncio.create_task(stamina_recovery_loop())
        asyncio.create_task(save_state_loop())
        logger.info("🔄 Background loops started (proactive, stamina recovery, save state)")
    
    # ========== READY ==========
    logger.info("=" * 70)
    logger.info("💜 AMORIA + ANORA is running!")
    logger.info("   Kirim /nova untuk panggil Nova")
    logger.info("   Kirim /roleplay untuk mode beneran ketemu")
    logger.info("   Kirim /pindah pantai untuk ke pantai")
    logger.info("   Kirim /help untuk bantuan lengkap")
    logger.info("=" * 70)
    
    # Keep running
    await asyncio.Event().wait()


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
