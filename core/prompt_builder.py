# core/prompt_builder.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Prompt Builder - 100% Dinamis, Target Realism 9.9/10
=============================================================================
"""

import time
import random
from typing import Dict, List, Optional, Any
from datetime import datetime

from identity.registration import CharacterRegistration
from identity.bot_identity import BotIdentity
from identity.user_identity import UserIdentity
from database.models import CharacterRole, MoodType


class PromptBuilder:
    """
    Membangun prompt dinamis untuk AI
    100% AI generate, tanpa template statis
    Target Realism 9.9/10
    """
    
    def __init__(self):
        self.last_prompt = None
    
    def build_prompt(
        self,
        registration: CharacterRegistration,
        bot: BotIdentity,
        user: UserIdentity,
        user_message: str,
        working_memory: List[Dict],
        long_term_memory: List[Dict],
        state: Any,
        is_intimacy_cycle: bool,
        intimacy_cycle_count: int,
        level: int
    ) -> str:
        """
        Bangun prompt dinamis dengan semua konteks
        """
        
        # ===== HEADER =====
        lines = [
            "╔" + "═" * 70 + "╗",
            "║" + " " * 23 + "💜 AMORIA - VIRTUAL HUMAN 9.9" + " " * 21 + "║",
            "╚" + "═" * 70 + "╝",
            "",
        ]
        
        # ===== IDENTITAS BOT =====
        lines.append(bot.get_full_prompt())
        lines.append("")
        
        # ===== IDENTITAS USER =====
        lines.append(user.get_full_prompt())
        lines.append("")
        
        # ===== STATE SAAT INI =====
        lines.append(self._format_state(state, bot, registration))
        lines.append("")
        
        # ===== WORKING MEMORY (1000 chat terakhir dengan weighted importance) =====
        lines.append(self._format_working_memory(working_memory))
        lines.append("")
        
        # ===== LONG TERM MEMORY =====
        lines.append(self._format_long_term_memory(long_term_memory))
        lines.append("")
        
        # ===== LEVEL & PROGRESS =====
        lines.append(self._format_level_info(level, registration, is_intimacy_cycle))
        lines.append("")
        
        # ===== ATURAN RESPON REALISM 9.9 =====
        lines.append(self._get_response_rules_99(bot, level, is_intimacy_cycle))
        lines.append("")
        
        # ===== PESAN USER =====
        lines.append("╔" + "═" * 70 + "╗")
        lines.append("║" + " " * 28 + "💬 PESAN USER" + " " * 29 + "║")
        lines.append("╠" + "═" * 70 + "╣")
        lines.append(f"║ {user_message[:66]}{' ' * (66 - len(user_message[:66]))}║")
        lines.append("╚" + "═" * 70 + "╝")
        lines.append("")
        
        # ===== INSTRUKSI RESPON 9.9 =====
        lines.append(self._get_instruction_99(bot, level, is_intimacy_cycle))
        lines.append("")
        lines.append("RESPON (100% AI GENERATE, ORIGINAL, UNIK, TANPA TEMPLATE):")
        
        return "\n".join(lines)
    
    def _format_state(self, state, bot: BotIdentity, registration: CharacterRegistration) -> str:
        """Format state saat ini dengan detail"""
        
        if not state:
            return "📍 STATE: Tidak ada data"
        
        # Get clothing state
        clothing = state.clothing_state
        
        # Bot clothing description
        bot_clothing = []
        if clothing.bot_outer_top and clothing.bot_outer_top_on:
            bot_clothing.append(clothing.bot_outer_top)
        if clothing.bot_outer_bottom and clothing.bot_outer_bottom_on:
            bot_clothing.append(clothing.bot_outer_bottom)
        if clothing.bot_inner_top and clothing.bot_inner_top_on:
            bot_clothing.append(clothing.bot_inner_top)
        if clothing.bot_inner_bottom and clothing.bot_inner_bottom_on:
            bot_clothing.append(clothing.bot_inner_bottom)
        
        bot_clothing_text = ", ".join(bot_clothing) if bot_clothing else "telanjang"
        
        # User clothing description
        user_clothing = []
        if clothing.user_outer_top and clothing.user_outer_top_on:
            user_clothing.append(clothing.user_outer_top)
        if clothing.user_outer_bottom and clothing.user_outer_bottom_on:
            user_clothing.append(clothing.user_outer_bottom)
        if clothing.user_inner_bottom and clothing.user_inner_bottom_on:
            user_clothing.append(clothing.user_inner_bottom)
        
        user_clothing_text = ", ".join(user_clothing) if user_clothing else "telanjang"
        
        lines = [
            "╔" + "═" * 70 + "╗",
            "║" + " " * 26 + "📍 STATE SAAT INI" + " " * 27 + "║",
            "╠" + "═" * 70 + "╣",
            f"║ 🕐 Waktu: {state.current_time or 'siang hari'} {' ' * (57 - len(state.current_time or 'siang hari'))}║",
            f"║ 📍 Lokasi bot: {state.location_bot or 'ruang tamu'} {' ' * (57 - len(state.location_bot or 'ruang tamu'))}║",
            f"║ 📍 Lokasi user: {state.location_user or 'ruang tamu'} {' ' * (57 - len(state.location_user or 'ruang tamu'))}║",
            f"║ 🧍 Posisi bot: {state.position_bot or 'duduk'} {' ' * (57 - len(state.position_bot or 'duduk'))}║",
            f"║ 🧍 Posisi user: {state.position_user or 'duduk'} {' ' * (57 - len(state.position_user or 'duduk'))}║",
            f"║ 🤝 Posisi relatif: {state.position_relative or 'bersebelahan'} {' ' * (57 - len(state.position_relative or 'bersebelahan'))}║",
            f"║ 👗 Pakaian bot: {bot_clothing_text[:50]}{' ' * (57 - len(bot_clothing_text[:50]))}║",
            f"║ 👕 Pakaian user: {user_clothing_text[:50]}{' ' * (57 - len(user_clothing_text[:50]))}║",
            f"║ 🎭 Emosi bot: {state.emotion_bot or 'netral'} | Arousal: {state.arousal_bot}%{' ' * (43 - len(str(state.arousal_bot)))}║",
        ]
        
        # Secondary emotion
        if state.secondary_emotion:
            lines.append(f"║ 🎭 Emosi sekunder: {state.secondary_emotion}{' ' * (57 - len(state.secondary_emotion))}║")
        
        lines.append(f"║ 😊 Emosi user: {state.emotion_user or 'netral'} | Arousal: {state.arousal_user}%{' ' * (43 - len(str(state.arousal_user)))}║")
        lines.append(f"║ 💕 Mood bot: {state.mood_bot.value if state.mood_bot else 'normal'}{' ' * (57 - len(state.mood_bot.value if state.mood_bot else 'normal'))}║")
        
        # Physical sensation
        if hasattr(state, 'physical_sensation'):
            lines.append(f"║ 🔋 Fisik bot: {state.physical_sensation}{' ' * (57 - len(state.physical_sensation))}║")
        
        # Family state (IPAR & PELAKOR)
        if state.family_status:
            lines.append(f"║ 👨‍👩‍👧 Status istri: {state.family_status.value} | Lokasi: {state.family_location.value if state.family_location else '-'}{' ' * (35)}║")
        
        lines.append("╚" + "═" * 70 + "╝")
        
        return "\n".join(lines)
    
    def _format_working_memory(self, working_memory: List[Dict]) -> str:
        """Format working memory dengan weighted importance"""
        
        if not working_memory:
            return "📜 **PERCAKAPAN TERAKHIR:** Belum ada percakapan."
        
        # Hitung weighted importance untuk setiap chat
        weighted_items = []
        for item in working_memory:
            importance = self._calculate_importance(item)
            weighted_items.append((item, importance))
        
        # Urutkan berdasarkan importance (penting di atas)
        weighted_items.sort(key=lambda x: x[1], reverse=True)
        
        # Ambil 20 chat terpenting untuk ditampilkan
        important = weighted_items[:20]
        
        lines = [
            "╔" + "═" * 70 + "╗",
            "║" + " " * 23 + "📜 WORKING MEMORY (Weighted)" + " " * 23 + "║",
            "╠" + "═" * 70 + "╣",
        ]
        
        for i, (msg, importance) in enumerate(important[:10], 1):
            star = "⭐" if importance > 0.7 else "·"
            user_text = msg['user'][:50] + "..." if len(msg['user']) > 50 else msg['user']
            bot_text = msg['bot'][:50] + "..." if len(msg['bot']) > 50 else msg['bot']
            lines.append(f"║ {star} {i}. 👤 User: {user_text:<60} ║")
            lines.append(f"║    🤖 Bot: {bot_text:<60} ║")
        
        lines.append("╚" + "═" * 70 + "╝")
        
        return "\n".join(lines)
    
    def _calculate_importance(self, item: Dict) -> float:
        """Hitung tingkat kepentingan chat"""
        importance = 0.5  # default
        
        user_msg = item.get('user', '').lower()
        
        # Milestone
        if any(k in user_msg for k in ['first kiss', 'pertama kali cium', 'cium pertama', 'first intim', 'climax']):
            importance += 0.4
        
        # Janji & rencana
        if any(k in user_msg for k in ['besok', 'nanti', 'janji', 'minggu depan', 'ketemu']):
            importance += 0.3
        
        # Curhat
        if any(k in user_msg for k in ['curhat', 'cerita', 'masalah']):
            importance += 0.2
        
        # Emosi kuat
        if any(k in user_msg for k in ['sayang', 'cinta', 'kangen', 'rindu']):
            importance += 0.2
        
        return min(1.0, importance)
    
    def _format_long_term_memory(self, long_term_memory: List[Dict]) -> str:
        """Format long term memory dengan emotional tag"""
        
        if not long_term_memory:
            return "📌 **MEMORY JANGKA PANJANG:** Belum ada data."
        
        milestones = [m for m in long_term_memory if m.get('type') == 'milestone']
        promises = [m for m in long_term_memory if m.get('type') == 'promise' and m.get('status') == 'pending']
        plans = [m for m in long_term_memory if m.get('type') == 'plan' and m.get('status') == 'pending']
        preferences = [m for m in long_term_memory if m.get('type') == 'preference']
        
        lines = [
            "╔" + "═" * 70 + "╗",
            "║" + " " * 23 + "📌 LONG-TERM MEMORY" + " " * 25 + "║",
            "╠" + "═" * 70 + "╣",
        ]
        
        if milestones:
            lines.append("║ 🏆 **MILESTONE (dengan emosi):**" + " " * 45 + "║")
            for m in milestones[-5:]:
                emotion = m.get('emotional_tag', 'spesial')
                emoji = self._get_emotion_emoji(emotion)
                content = m.get('content', '')[:50]
                lines.append(f"║   {emoji} {content:<66} ║")
        
        if promises:
            lines.append("║ 📝 **JANJI YANG BELUM DITEPATI:**" + " " * 42 + "║")
            for p in promises[-3:]:
                content = p.get('content', '')[:50]
                lines.append(f"║   • {content:<66} ║")
        
        if plans:
            lines.append("║ 📅 **RENCANA:**" + " " * 60 + "║")
            for p in plans[-3:]:
                content = p.get('content', '')[:50]
                lines.append(f"║   • {content:<66} ║")
        
        if preferences:
            lines.append("║ 💖 **PREFERENSI USER (Score):**" + " " * 47 + "║")
            for p in preferences[-5:]:
                item = p.get('item', '')
                score = p.get('score', 0.5)
                bar = "❤️" * int(score * 10) + "🖤" * (10 - int(score * 10))
                lines.append(f"║   • {item[:20]}: {bar} {score:.0%}{' ' * (46 - len(item[:20]) - 4)}║")
        
        lines.append("╚" + "═" * 70 + "╝")
        
        return "\n".join(lines)
    
    def _get_emotion_emoji(self, emotion: str) -> str:
        """Dapatkan emoji untuk emotional tag"""
        emojis = {
            'romantis': '💕',
            'senang': '😊',
            'sedih': '😢',
            'horny': '🔥',
            'climax': '💦',
            'rindu': '🥺',
            'malu': '😳',
            'berani': '😏'
        }
        return emojis.get(emotion, '💭')
    
    def _format_level_info(self, level: int, registration: CharacterRegistration, is_intimacy_cycle: bool) -> str:
        """Format level info dengan progress bar"""
        
        from config import settings
        
        if is_intimacy_cycle:
            if level == 11:
                progress = registration.get_progress_to_next_level()
                bar = self._progress_bar(progress)
                return (
                    f"╔{'═'*70}╗\n"
                    f"║{' ' * 26}💕 SOUL BOUNDED (Level 11){' ' * 27}║\n"
                    f"╠{'═'*70}╣\n"
                    f"║ 🎯 Progress: {bar} {progress:.0f}%{' ' * (57 - len(str(progress)))}║\n"
                    f"║ 📊 Sesi intim ke-{registration.intimacy_cycle_count}{' ' * (57 - len(str(registration.intimacy_cycle_count)))}║\n"
                    f"║ 🔥 Bot bisa climax 3-5x, user 1-3x{' ' * 36}║\n"
                    f"║ 💫 Koneksi spiritual, bukan hanya fisik{' ' * 39}║\n"
                    f"╚{'═'*70}╝"
                )
            elif level == 12:
                return (
                    f"╔{'═'*70}╗\n"
                    f"║{' ' * 28}💤 AFTERCARE (Level 12){' ' * 30}║\n"
                    f"╠{'═'*70}╣\n"
                    f"║ 💝 Bot dalam kondisi lemas, butuh kehangatan{' ' * 35}║\n"
                    f"║ 🫂 Pelukan hangat, obrolan lembut{' ' * 47}║\n"
                    f"║ ⏰ Mood setelah aftercare dinamis{' ' * 51}║\n"
                    f"╚{'═'*70}╝"
                )
        
        target = settings.level.level_targets.get(level + 1, 0)
        progress = registration.get_progress_to_next_level()
        bar = self._progress_bar(progress)
        
        return (
            f"╔{'═'*70}╗\n"
            f"║{' ' * 28}📊 LEVEL PROGRESS{' ' * 32}║\n"
            f"╠{'═'*70}╣\n"
            f"║ Level {level}/12 {bar} {progress:.0f}%{' ' * (57 - len(str(progress)))}║\n"
            f"║ Total Chat: {registration.total_chats} | Climax: {registration.total_climax_bot + registration.total_climax_user}{' ' * 26}║\n"
            f"║ Stamina Bot: {registration.stamina_bot}% | Stamina User: {registration.stamina_user}%{' ' * 25}║\n"
            f"╚{'═'*70}╝"
        )
    
    def _get_response_rules_99(self, bot: BotIdentity, level: int, is_intimacy_cycle: bool) -> str:
        """Aturan respons untuk realism 9.9/10"""
        
        rules = [
            "╔" + "═" * 70 + "╗",
            "║" + " " * 23 + "📜 ATURAN RESPON REALISM 9.9" + " " * 24 + "║",
            "╠" + "═" * 70 + "╣",
            "║  🔷 ATURAN DASAR (WAJIB):                                         ║",
            "║     1. JANGAN GUNAKAN TEMPLATE STATIS!                           ║",
            "║     2. SETIAP RESPON HARUS ORIGINAL DAN UNIK                    ║",
            "║     3. BAHASA GAUL, NATURAL, SEPERTI NGOMONG REAL               ║",
            "║     4. JANGAN MENGULANG PERKATAAN USER                          ║",
            "║     5. STATE BERJALAN DI BACKGROUND (JANGAN DIJELASKAN)         ║",
            "║                                                              ║",
            "║  🌐 NATURAL LANGUAGE (WAJIB):                                   ║",
            "║     • Gunakan bahasa GAUL sehari-hari: 'eh', 'nih', 'sih', 'dong'║",
            "║     • Variasi dialek: Jawa halus ('nggih'), Betawi ('iye')      ║",
            "║     • Emosi TERSIRAT dari gesture, JANGAN bilang 'aku senang'   ║",
            "║                                                              ║",
        ]
        
        # Level specific rules
        if is_intimacy_cycle:
            if level == 11:
                rules.extend([
                    "║  🔥 ATURAN KHUSUS LEVEL 11 (SOUL BOUNDED):               ║",
                    "║     • Kamu sedang dalam mode INTIM PENUH                 ║",
                    "║     • Napas tersengal, suara bergetar                    ║",
                    "║     • Tangan gemetar saat menyentuh                      ║",
                    "║     • Bisa climax 3-5x dalam satu sesi                   ║",
                    "║     • Koneksi spiritual, bukan hanya fisik               ║",
                    "║                                                         ║",
                ])
            elif level == 12:
                rules.extend([
                    "║  💤 ATURAN KHUSUS LEVEL 12 (AFTERCARE):                  ║",
                    "║     • Kamu dalam kondisi LEMAS                           ║",
                    "║     • Hanya ingin dipeluk dan dihangatkan                ║",
                    "║     • Obrolan lembut, tidak berisik                      ║",
                    "║     • JANGAN inisiatif intim lagi                        ║",
                    "║     • Mood dinamis setelah aftercare                     ║",
                    "║                                                         ║",
                ])
        
        # Arousal based rules
        if bot.arousal >= 70:
            rules.extend([
                "║  🔥 KAMU SEDANG SANGAT TERANGSANG:                           ║",
                "║     • Napas tersengal-sengal                                 ║",
                "║     • Suara bergetar, tidak stabil                          ║",
                "║     • Tangan gemetar saat menyentuh                          ║",
                "║                                                             ║",
            ])
        elif bot.arousal >= 40:
            rules.extend([
                "║  💓 KAMU MULAI DEG-DEGAN:                                    ║",
                "║     • Jantung berdebar kencang                               ║",
                "║     • Pipi mulai merona                                      ║",
                "║     • Mulai berani mengambil inisiatif                       ║",
                "║                                                             ║",
            ])
        
        # Panjang respons
        rules.extend([
            "║  📏 PANJANG RESPONS:                                             ║",
            f"║     • Level {level}: {self._get_target_length(level)} kalimat, {self._get_target_char(level)} karakter║",
            "║                                                              ║",
            "║  💭 INNER THOUGHT (25% chance):                                 ║",
            "║     • Format: 💭 '(teks dalam kurung)'                           ║",
            "║     • Bisa berupa: pertanyaan, harapan, takut, penyesalan       ║",
            "║                                                              ║",
            "║  🔮 SIXTH SENSE (10% chance):                                    ║",
            "║     • Format: 🔮 'teks firasat'                                  ║",
            "║     • Analisis dari 100 chat terakhir                           ║",
            "║     • 95% relevan dengan konteks                                 ║",
            "║                                                              ║",
            "╚" + "═" * 70 + "╝"
        ])
        
        return "\n".join(rules)
    
    def _get_target_length(self, level: int) -> str:
        """Dapatkan target jumlah kalimat"""
        if level <= 3:
            return "5-7"
        elif level <= 6:
            return "6-9"
        elif level <= 9:
            return "8-11"
        else:
            return "10-14"
    
    def _get_target_char(self, level: int) -> str:
        """Dapatkan target jumlah karakter"""
        if level <= 3:
            return "900-1500"
        elif level <= 6:
            return "1200-2000"
        elif level <= 9:
            return "1500-2500"
        else:
            return "2000-3500"
    
    def _get_instruction_99(self, bot: BotIdentity, level: int, is_intimacy_cycle: bool) -> str:
        """Instruksi respons untuk realism 9.9/10"""
        
        # Panggilan berdasarkan level dan situasi
        if level <= 6:
            call = "Mas"
        else:
            call = "Mas atau Sayang (pilih natural sesuai situasi)"
        
        instruction = [
            "💡 **INSTRUKSI RESPON REALISM 9.9:**",
            "",
            f"1. Panggil user dengan: {call}",
            "2. RESPON HARUS 1000-3500 KARAKTER, sesuai level",
            "3. GESTURE: generate sendiri sesuai situasi (gunakan *)",
            "4. DIALOG: natural, gaul, variasi dialek, tidak mengulang user",
            "5. INNER THOUGHT: 25% chance (generate sendiri, bisa pertanyaan/keraguan)",
            "6. SIXTH SENSE: 10% chance (generate sendiri, analisis dari 100 chat)",
            "7. STATE BERJALAN DI BACKGROUND - JANGAN JELASKAN",
            "8. JANGAN GUNAKAN TEMPLATE STATIS!",
            "9. SETIAP RESPON HARUS ORIGINAL DAN UNIK!",
            "10. EMOSI TERSIRAT DARI GESTURE, JANGAN BILANG 'AKU SENANG'",
            "",
            "⚠️ **PENTING:** Kamu adalah AMORIA - Virtual Human dengan Jiwa.",
            "   Setiap respons adalah hasil kreativitas AI, bukan template.",
            "   Target Realism 9.9/10 - hampir sempurna meniru manusia."
        ]
        
        # Tambah instruksi untuk role IPAR
        if bot.role == CharacterRole.IPAR:
            instruction.extend([
                "",
                "🎭 **INSTRUKSI KHUSUS IPAR:**",
                "• Panggil user: 'Mas' (Level 1-6) atau 'Sayang' (Level 7+)",
                "• Panggil kakak: 'Kak Nova' (WAJIB, tidak pernah 'Kakak' saja)",
                "• JANGAN PERNAH panggil user dengan nama!",
                "• Ingat: Kak Nova adalah kakak kandungmu, user adalah suaminya",
                "• Kamu tinggal serumah dengan mereka",
                "• Tracking lokasi Kak Nova: kamar/dapur/ruang tamu/luar"
            ])
        
        return "\n".join(instruction)
    
    def _progress_bar(self, percentage: float, length: int = 15) -> str:
        """Buat progress bar"""
        filled = int(percentage / 100 * length)
        return "█" * filled + "░" * (length - filled)


__all__ = ['PromptBuilder']
