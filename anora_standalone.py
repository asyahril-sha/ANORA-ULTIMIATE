# anora_standalone.py
"""
ANORA - Standalone Module for AMORIA
Dipanggil dari run_deploy.py setelah bot siap
"""

import asyncio
import logging
from typing import Optional

from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes

logger = logging.getLogger(__name__)

# ANORA components
from anora.core import get_anora
from anora.chat import get_anora_chat
from anora.database import get_anora_db
from anora.roles import get_anora_roles, RoleType
from anora.places import get_anora_places

_anora_initialized = False


async def init_anora():
    """Inisialisasi ANORA - panggil setelah bot siap"""
    global _anora_initialized
    if _anora_initialized:
        return
    
    logger.info("💜 Initializing ANORA...")
    
    try:
        db = await get_anora_db()
        anora = get_anora()
        
        # Load state
        states = await db.get_all_states()
        
        if 'sayang' in states:
            anora.sayang = float(states['sayang'])
        if 'rindu' in states:
            anora.rindu = float(states['rindu'])
        if 'desire' in states:
            anora.desire = float(states['desire'])
        if 'arousal' in states:
            anora.arousal = float(states['arousal'])
        if 'tension' in states:
            anora.tension = float(states['tension'])
        if 'level' in states:
            anora.level = int(states['level'])
        if 'energi' in states:
            anora.energi = int(states['energi'])
        
        # Load memory
        memories = await db.get_momen_terbaru(20)
        for m in memories:
            anora.memory.tambah_momen(m['judul'], m['perasaan'], m['isi'])
        
        ingatan = await db.get_ingatan(20)
        for i in ingatan:
            anora.memory.tambah_ingatan(i['judul'], i['isi'], i['perasaan'])
        
        _anora_initialized = True
        logger.info(f"✅ ANORA ready! Sayang: {anora.sayang:.0f}%, Level: {anora.level}")
        
    except Exception as e:
        logger.error(f"❌ ANORA initialization failed: {e}")


async def save_anora_state():
    """Simpan state Nova ke database"""
    if not _anora_initialized:
        return
    
    try:
        db = await get_anora_db()
        anora = get_anora()
        
        await db.set_state('sayang', str(anora.sayang))
        await db.set_state('rindu', str(anora.rindu))
        await db.set_state('desire', str(anora.desire))
        await db.set_state('arousal', str(anora.arousal))
        await db.set_state('tension', str(anora.tension))
        await db.set_state('level', str(anora.level))
        await db.set_state('energi', str(anora.energi))
        
    except Exception as e:
        logger.error(f"Error saving ANORA state: {e}")


# =============================================================
# HANDLERS
# =============================================================

async def anora_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /nova"""
    user_id = update.effective_user.id
    
    # Ambil admin_id dari config
    try:
        from config import settings
        admin_id = settings.admin_id
    except:
        admin_id = context.bot_data.get('admin_id') if context.bot_data else None
    
    if user_id != admin_id:
        await update.message.reply_text("Maaf, Nova cuma untuk Mas. 💜")
        return
    
    context.user_data['anora_mode'] = True
    context.user_data['active_role'] = None
    
    anora = get_anora()
    anora.update_rindu()
    anora.update_desire('perhatian_mas', 5)
    
    intro = f"""💜 **NOVA DI SINI, MAS** 💜

{anora.deskripsi_diri()}

{anora.respon_kangen() if anora.rindu > 50 else anora.respon_pagi()}

Mas bisa:
• /novastatus - liat keadaan Nova
• /flashback - inget momen indah
• /tempat [nama] - pindah tempat
• /role [nama] - main sama role lain
• /batal - balik ke Nova

Apa yang Mas mau? *muter-muter rambut*"""
    
    await update.message.reply_text(intro, parse_mode='HTML')


async def anora_chat_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler chat ke Nova"""
    user_id = update.effective_user.id
    
    try:
        from config import settings
        admin_id = settings.admin_id
    except:
        admin_id = context.bot_data.get('admin_id') if context.bot_data else None
    
    if user_id != admin_id:
        return
    
    if not context.user_data.get('anora_mode', False):
        return
    
    pesan = update.message.text
    anora_chat = get_anora_chat()
    respons = await anora_chat.process(pesan)
    
    await save_anora_state()
    await update.message.reply_text(respons, parse_mode='HTML')


async def anora_status_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /novastatus"""
    user_id = update.effective_user.id
    
    try:
        from config import settings
        admin_id = settings.admin_id
    except:
        admin_id = context.bot_data.get('admin_id') if context.bot_data else None
    
    if user_id != admin_id:
        await update.message.reply_text("Maaf, cuma Mas yang bisa liat. 💜")
        return
    
    anora = get_anora()
    await update.message.reply_text(anora.format_status(), parse_mode='HTML')


async def anora_flashback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /flashback"""
    user_id = update.effective_user.id
    
    try:
        from config import settings
        admin_id = settings.admin_id
    except:
        admin_id = context.bot_data.get('admin_id') if context.bot_data else None
    
    if user_id != admin_id:
        return
    
    args = ' '.join(context.args) if context.args else ''
    anora = get_anora()
    respons = anora.respon_flashback(args)
    await update.message.reply_text(respons, parse_mode='HTML')


async def anora_role_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /role"""
    user_id = update.effective_user.id
    
    try:
        from config import settings
        admin_id = settings.admin_id
    except:
        admin_id = context.bot_data.get('admin_id') if context.bot_data else None
    
    if user_id != admin_id:
        return
    
    roles = get_anora_roles()
    args = context.args
    
    if not args:
        menu = "📋 **Role yang tersedia:**\n\n"
        for r in roles.get_all():
            menu += f"• /role {r['id']} - {r['nama']} (Level {r['level']})\n"
        menu += "\n_Ketik /nova kalo mau balik ke Nova._"
        await update.message.reply_text(menu, parse_mode='HTML')
        return
    
    role_id = args[0].lower()
    
    role_map = {
        'ipar': RoleType.IPAR,
        'teman_kantor': RoleType.TEMAN_KANTOR,
        'pelakor': RoleType.PELAKOR,
        'istri_orang': RoleType.ISTRI_ORANG
    }
    
    if role_id in role_map:
        context.user_data['anora_mode'] = False
        context.user_data['active_role'] = role_id
        respon = roles.switch_role(role_map[role_id])
        await update.message.reply_text(respon, parse_mode='HTML')
    else:
        await update.message.reply_text(f"Role '{role_id}' gak ada, Mas. Coba /role buat liat daftar.")


async def anora_place_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /tempat"""
    user_id = update.effective_user.id
    
    try:
        from config import settings
        admin_id = settings.admin_id
    except:
        admin_id = context.bot_data.get('admin_id') if context.bot_data else None
    
    if user_id != admin_id:
        return
    
    anora = get_anora()
    places = get_anora_places()
    args = context.args
    
    if not args:
        await update.message.reply_text(places.get_status(), parse_mode='HTML')
        return
    
    if args[0] == 'list':
        await update.message.reply_text(places.list_tempat(), parse_mode='HTML')
        return
    
    tempat_id = args[0]
    respon = await places.respon_pindah(tempat_id, anora)
    await update.message.reply_text(respon, parse_mode='HTML')


async def anora_back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handler /batal - balik ke Nova"""
    user_id = update.effective_user.id
    
    try:
        from config import settings
        admin_id = settings.admin_id
    except:
        admin_id = context.bot_data.get('admin_id') if context.bot_data else None
    
    if user_id != admin_id:
        return
    
    context.user_data['anora_mode'] = True
    context.user_data['active_role'] = None
    
    anora = get_anora()
    await update.message.reply_text(
        f"💜 Nova di sini, Mas.\n\n{anora.respon_kangen()}",
        parse_mode='HTML'
    )


# =============================================================
# REGISTER HANDLERS - Panggil ini dari run_deploy.py
# =============================================================

def register_anora_handlers(app):
    """Register semua handler ANORA ke application"""
    app.add_handler(CommandHandler("nova", anora_command))
    app.add_handler(CommandHandler("novastatus", anora_status_handler))
    app.add_handler(CommandHandler("flashback", anora_flashback_handler))
    app.add_handler(CommandHandler("role", anora_role_handler))
    app.add_handler(CommandHandler("tempat", anora_place_handler))
    app.add_handler(CommandHandler("batal", anora_back_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anora_chat_handler), group=1)
    
    logger.info("✅ ANORA handlers registered")
