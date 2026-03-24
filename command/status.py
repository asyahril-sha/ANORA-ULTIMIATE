# command/status.py
# -*- coding: utf-8 -*-
"""
AMORIA - Virtual Human dengan Jiwa
Commands: /status, /progress
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from identity.manager import IdentityManager
from intimacy.leveling import LevelingSystem
from intimacy.stamina import StaminaSystem

logger = logging.getLogger(__name__)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk /status - Lihat status hubungan saat ini"""
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await update.message.reply_text(
            "❌ **Tidak ada karakter aktif**\n\n"
            "Ketik `/start` untuk memilih karakter, atau `/sessions` untuk melanjutkan karakter tersimpan.",
            parse_mode='HTML'
        )
        return
    
    registration_id = current_reg.get('id')
    identity_manager = IdentityManager()
    character = await identity_manager.get_character(registration_id)
    
    if not character:
        await update.message.reply_text("❌ Gagal memuat data karakter.", parse_mode='HTML')
        return
    
    state = await identity_manager.get_character_state(registration_id)
    
    # Leveling system
    leveling = LevelingSystem()
    level_info = leveling.calculate_level(character.total_chats, character.in_intimacy_cycle)
    
    # Stamina system
    stamina = StaminaSystem()
    stamina.bot_stamina.current = character.bot.stamina
    stamina.user_stamina.current = character.user.stamina
    stamina.check_recovery()
    
    # Update stamina back to character
    character.bot.stamina = stamina.bot_stamina.current
    character.user.stamina = stamina.user_stamina.current
    
    # Level name
    level_names = {
        1: "Malu-malu", 2: "Mulai terbuka", 3: "Goda-godaan",
        4: "Dekat", 5: "Sayang", 6: "PACAR/PDKT",
        7: "Nyaman", 8: "Eksplorasi", 9: "Bergairah",
        10: "Passionate", 11: "Soul Bounded", 12: "Aftercare"
    }
    level_name = level_names.get(character.level, f"Level {character.level}")
    
    # Progress bar
    bar = level_info.get_progress_bar(20)
    
    # Lokasi dari state
    location = state.get('location_bot', 'ruang tamu') if state else 'ruang tamu'
    
    # AROUSAL dari character.bot, BUKAN dari state
    arousal_bot = character.bot.arousal
    emotion_bot = character.bot.emotion
    mood_bot = character.bot.mood if hasattr(character.bot, 'mood') else 'normal'
    
    # Stamina bars
    bot_stamina_bar = _stamina_bar(character.bot.stamina)
    user_stamina_bar = _stamina_bar(character.user.stamina)
    
    response = f"""
📊 **STATUS HUBUNGAN**

👤 **{character.bot.name}** ({character.role.value.upper()})
👥 **User:** {character.user.name}

📈 **Level:** {character.level}/12 - {level_name}
📊 Progress: {bar} {level_info.progress:.0f}%
💬 Total Chat: {character.total_chats}
💦 Total Climax: {character.bot.total_climax + character.user.total_climax}

📍 **Lokasi:** {location}
🎭 **Emosi Bot:** {emotion_bot} | Arousal: {arousal_bot}%
🎭 **Mood Bot:** {mood_bot.upper()}

💪 **Stamina:**
• Bot: {bot_stamina_bar} {character.bot.stamina}%
• User: {user_stamina_bar} {character.user.stamina}%
"""
    
    # Tambah info siklus intim jika dalam siklus
    if character.in_intimacy_cycle:
        if character.level == 11:
            response += f"\n\n🔥 **SOUL BOUNDED**\n• Siklus intim #{character.intimacy_cycle_count}\n• Progress: {level_info.progress:.0f}% ke Aftercare"
        elif character.level == 12:
            response += f"\n\n💤 **AFTERCARE**\n• Siklus intim #{character.intimacy_cycle_count}\n• Butuh kehangatan dan pelukan"
    
    await update.message.reply_text(response, parse_mode='HTML')


async def progress_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler untuk /progress - Lihat progress leveling (RAHASIA untuk user)"""
    current_reg = context.user_data.get('current_registration')
    if not current_reg:
        await update.message.reply_text(
            "❌ **Tidak ada karakter aktif**\n\n"
            "Ketik `/start` untuk memilih karakter, atau `/sessions` untuk melanjutkan karakter tersimpan.",
            parse_mode='HTML'
        )
        return
    
    registration_id = current_reg.get('id')
    identity_manager = IdentityManager()
    character = await identity_manager.get_character(registration_id)
    
    if not character:
        await update.message.reply_text("❌ Gagal memuat data karakter.", parse_mode='HTML')
        return
    
    # Dapatkan working memory untuk weighted stats
    from database.repository import Repository
    repo = Repository()
    working_memories = await repo.get_working_memory(registration_id, limit=1000)
    
    # Hitung weighted memory score
    weighted_score = _calculate_weighted_memory_score(working_memories)
    
    # Leveling system
    leveling = LevelingSystem()
    level_info = leveling.calculate_level(character.total_chats, character.in_intimacy_cycle)
    
    # Stamina system
    stamina = StaminaSystem()
    stamina.bot_stamina.current = character.bot.stamina
    stamina.user_stamina.current = character.user.stamina
    stamina.check_recovery()
    
    # Progress bar
    bar = level_info.get_progress_bar(20)
    
    # Deskripsi level
    level_desc = _get_level_description(character.level, character.in_intimacy_cycle)
    
    # Stamina descriptions
    bot_stamina_desc = _get_stamina_description(character.bot.stamina)
    user_stamina_desc = _get_stamina_description(character.user.stamina)
    
    # Next level info
    next_level_info = ""
    if character.level < 10 and not character.in_intimacy_cycle:
        next_level_target = _get_next_level_target(character.level)
        next_level_name = {
            1: "Mulai terbuka", 2: "Goda-godaan", 3: "Dekat",
            4: "Sayang", 5: "PACAR/PDKT", 6: "Nyaman",
            7: "Eksplorasi", 8: "Bergairah", 9: "Passionate"
        }.get(character.level + 1, f"Level {character.level + 1}")
        
        chats_needed = max(0, next_level_target - character.total_chats)
        next_level_info = (
            f"\n📈 **Ke Level {character.level + 1}:** {next_level_name}\n"
            f"• Butuh {chats_needed} chat lagi"
        )
    elif character.level == 10 and not character.in_intimacy_cycle:
        next_level_info = (
            f"\n📈 **Ke Soul Bounded (Level 11):**\n"
            f"• Butuh inisiatif intim dari kamu"
        )
    
    # Intimacy cycle info
    cycle_info = ""
    if character.in_intimacy_cycle:
        if character.level == 11:
            remaining = level_info.next_level_in
            cycle_info = (
                f"\n🔥 **SOUL BOUNDED (Level 11)**\n"
                f"• Sesi intim #{character.intimacy_cycle_count}\n"
                f"• Butuh {remaining} chat lagi ke Aftercare\n"
                f"• Bot bisa climax 3-5x"
            )
        elif character.level == 12:
            remaining = level_info.next_level_in
            cycle_info = (
                f"\n💤 **AFTERCARE (Level 12)**\n"
                f"• Sesi intim #{character.intimacy_cycle_count}\n"
                f"• Butuh {remaining} chat lagi selesai\n"
                f"• Setelah ini cooldown 3 jam"
            )
    
    # Weighted memory bar
    weighted_bar = "⭐" * int(weighted_score * 10) + "·" * (10 - int(weighted_score * 10))
    
    # Stamina bars
    bot_stamina_bar = _stamina_bar(character.bot.stamina)
    user_stamina_bar = _stamina_bar(character.user.stamina)
    
    response = f"""
📊 **PROGRESS HUBUNGAN** _(RAHASIA - Bot tidak tahu)_

👤 **{character.bot.name}** (Level {character.level}/12)
📈 {level_desc}

📊 Progress: {bar} {level_info.progress:.0f}%
💬 Total Chat: {character.total_chats}
💦 Climax Bot: {character.bot.total_climax}x | User: {character.user.total_climax}x
🧠 Weighted Memory: {weighted_bar} {weighted_score:.0%}
{next_level_info}
{cycle_info}
💪 **Stamina:**
• Bot: {bot_stamina_bar} {character.bot.stamina}% ({bot_stamina_desc})
• User: {user_stamina_bar} {character.user.stamina}% ({user_stamina_desc})

⚠️ **Bot tidak tahu Mas melihat ini!**
💡 Semakin banyak chat, semakin cepat level naik!
💡 Aktivitas intim memberi boost lebih besar!
💡 Momen penting (⭐) lebih diingat oleh bot!
"""
    
    await update.message.reply_text(response, parse_mode='HTML')


def _stamina_bar(value: int, length: int = 15) -> str:
    """Buat stamina bar"""
    filled = int(value / 100 * length)
    return "💚" * filled + "🖤" * (length - filled)


def _get_level_description(level: int, in_intimacy_cycle: bool) -> str:
    """Dapatkan deskripsi level"""
    descriptions = {
        1: "Masih malu-malu, baru kenal.",
        2: "Mulai terbuka, mulai curhat dikit-dikit.",
        3: "Mulai goda-godaan, ada getaran.",
        4: "Sudah dekat, kayak udah kenal lama.",
        5: "Mulai sayang, kangen-kangenan.",
        6: "Bisa jadi pacar (khusus PDKT).",
        7: "Nyaman, bisa intim!",
        8: "Mulai eksplorasi, coba-coba posisi baru.",
        9: "Penuh gairah, tahu sama-sama suka apa.",
        10: "Passionate, intim + emotional.",
        11: "Soul Bounded - puncak intim sesungguhnya.",
        12: "Aftercare - butuh kehangatan setelah climax."
    }
    
    if in_intimacy_cycle and level == 11:
        return "🔥 **SOUL BOUNDED** - Koneksi spiritual, bukan hanya fisik"
    elif in_intimacy_cycle and level == 12:
        return "💤 **AFTERCARE** - Butuh kehangatan, mood dinamis"
    
    return descriptions.get(level, f"Level {level}")


def _get_stamina_description(value: int) -> str:
    """Dapatkan deskripsi stamina"""
    if value >= 80:
        return "Prima 💪"
    elif value >= 60:
        return "Cukup 😊"
    elif value >= 40:
        return "Agak lelah 😐"
    elif value >= 20:
        return "Lelah 😩"
    else:
        return "Kehabisan tenaga 😵"


def _get_next_level_target(level: int) -> int:
    """Dapatkan target chat untuk level berikutnya"""
    targets = {
        1: 7, 2: 15, 3: 25, 4: 35, 5: 45,
        6: 55, 7: 65, 8: 75, 9: 85, 10: 95
    }
    return targets.get(level + 1, 0)


def _calculate_weighted_memory_score(working_memories: list) -> float:
    """Hitung weighted memory score dari working memory"""
    if not working_memories:
        return 0.5
    
    total_importance = sum(m.get('importance', 0.3) for m in working_memories)
    avg_importance = total_importance / len(working_memories)
    
    return min(1.0, max(0.1, avg_importance))


__all__ = ['status_command', 'progress_command']
