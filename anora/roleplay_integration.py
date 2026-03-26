# anora/roleplay_integration.py
"""
ANORA Roleplay Integration - Menyatukan semua sistem roleplay
Brain, Memory, AI, Stamina, Intimacy, semuanya jadi satu.
100% AI Generate. Bukan Template. Nova Hidup.
DENGAN COMPLETE STATE - Nova ingat semua aspek seperti manusia.
"""

import asyncio
import time
import random
import json
import logging
from typing import Dict, Optional, Any, Tuple
from datetime import datetime

from .brain import get_anora_brain, LocationType, LocationDetail, Mood, Activity
from .memory_persistent import get_anora_persistent
from .roleplay_ai import get_anora_roleplay_ai
from .core import get_anora
from .intimacy import get_anora_intimacy

logger = logging.getLogger(__name__)


# =============================================================================
# STAMINA SYSTEM - REALISTIS (PERTAHANKAN)
# =============================================================================

class StaminaSystem:
    """
    Sistem stamina realistis untuk ANORA.
    - Stamina turun setelah climax
    - Butuh istirahat untuk pulih
    - Mempengaruhi mood dan kemampuan
    - Bisa pulih seiring waktu
    """
    
    def __init__(self):
        # Stamina Nova
        self.nova_current = 100
        self.nova_max = 100
        
        # Stamina Mas
        self.mas_current = 100
        self.mas_max = 100
        
        # Recovery rate (% per 10 menit istirahat)
        self.recovery_rate = 5
        
        # Cost setiap climax
        self.climax_cost_nova = 25
        self.climax_cost_mas = 30
        
        # Heavy climax cost (kalo climax keras)
        self.heavy_climax_cost_nova = 35
        self.heavy_climax_cost_mas = 40
        
        # Threshold
        self.exhausted_threshold = 20   # di bawah ini kehabisan tenaga
        self.tired_threshold = 40       # di bawah ini mulai lelah
        self.fatigued_threshold = 60    # di bawah ini mulai capek
        
        # Waktu terakhir climax
        self.last_climax_time = 0
        
        # Waktu terakhir recovery check
        self.last_recovery_check = time.time()
        
        # Jumlah climax hari ini
        self.climax_today = 0
        self.last_climax_date = datetime.now().date().isoformat()
    
    def update_recovery(self):
        """Update recovery berdasarkan waktu"""
        now = time.time()
        elapsed_minutes = (now - self.last_recovery_check) / 60
        
        if elapsed_minutes >= 10:
            recovery_amount = int(self.recovery_rate * (elapsed_minutes / 10))
            self.nova_current = min(self.nova_max, self.nova_current + recovery_amount)
            self.mas_current = min(self.mas_max, self.mas_current + recovery_amount)
            self.last_recovery_check = now
            logger.debug(f"💪 Stamina recovery: +{recovery_amount}%")
    
    def record_climax(self, who: str = "both", is_heavy: bool = False) -> Tuple[int, int]:
        """
        Rekam climax, kurangi stamina
        Returns: (nova_stamina_after, mas_stamina_after)
        """
        self.last_climax_time = time.time()
        
        # Update climax today
        today = datetime.now().date().isoformat()
        if self.last_climax_date != today:
            self.climax_today = 0
            self.last_climax_date = today
        self.climax_today += 1
        
        if who in ["nova", "both"]:
            cost = self.heavy_climax_cost_nova if is_heavy else self.climax_cost_nova
            self.nova_current = max(0, self.nova_current - cost)
        
        if who in ["mas", "both"]:
            cost = self.heavy_climax_cost_mas if is_heavy else self.climax_cost_mas
            self.mas_current = max(0, self.mas_current - cost)
        
        logger.info(f"💦 Climax #{self.climax_today}! Nova stamina: {self.nova_current}%, Mas stamina: {self.mas_current}%")
        
        return self.nova_current, self.mas_current
    
    def can_continue_intimacy(self) -> Tuple[bool, str]:
        """Cek apakah bisa lanjut intim"""
        self.update_recovery()
        
        if self.nova_current <= self.exhausted_threshold:
            return False, "Nova udah kehabisan tenaga, Mas... istirahat dulu ya. Besok lagi."
        
        if self.mas_current <= self.exhausted_threshold:
            return False, "Mas... Mas udah capek banget. Istirahat dulu."
        
        if self.nova_current <= self.tired_threshold:
            return True, "Nova mulai lelah, Mas... tapi masih bisa kalo Mas mau pelan-pelan."
        
        return True, "Siap lanjut"
    
    def get_nova_status(self) -> str:
        """Dapatkan status stamina Nova"""
        self.update_recovery()
        if self.nova_current >= 80:
            return "Prima 💪"
        elif self.nova_current >= 60:
            return "Cukup 😊"
        elif self.nova_current >= 40:
            return "Agak lelah 😐"
        elif self.nova_current >= 20:
            return "Lelah 😩"
        else:
            return "Kehabisan tenaga 😵"
    
    def get_mas_status(self) -> str:
        """Dapatkan status stamina Mas"""
        self.update_recovery()
        if self.mas_current >= 80:
            return "Prima 💪"
        elif self.mas_current >= 60:
            return "Cukup 😊"
        elif self.mas_current >= 40:
            return "Agak lelah 😐"
        elif self.mas_current >= 20:
            return "Lelah 😩"
        else:
            return "Kehabisan tenaga 😵"
    
    def get_nova_bar(self) -> str:
        """Dapatkan progress bar stamina Nova"""
        filled = int(self.nova_current / 10)
        return "💚" * filled + "🖤" * (10 - filled)
    
    def get_mas_bar(self) -> str:
        """Dapatkan progress bar stamina Mas"""
        filled = int(self.mas_current / 10)
        return "💚" * filled + "🖤" * (10 - filled)
    
    def format_for_prompt(self) -> str:
        """Format stamina untuk prompt AI"""
        self.update_recovery()
        return f"""
STAMINA SAAT INI:
- Nova: {self.get_nova_bar()} {self.nova_current}% ({self.get_nova_status()})
- Mas: {self.get_mas_bar()} {self.mas_current}% ({self.get_mas_status()})
- Climax hari ini: {self.climax_today}x
"""
    
    def to_dict(self) -> Dict:
        return {
            'nova_current': self.nova_current,
            'nova_max': self.nova_max,
            'mas_current': self.mas_current,
            'mas_max': self.mas_max,
            'last_climax_time': self.last_climax_time,
            'climax_today': self.climax_today,
            'last_climax_date': self.last_climax_date
        }
    
    def from_dict(self, data: Dict):
        self.nova_current = data.get('nova_current', 100)
        self.nova_max = data.get('nova_max', 100)
        self.mas_current = data.get('mas_current', 100)
        self.mas_max = data.get('mas_max', 100)
        self.last_climax_time = data.get('last_climax_time', 0)
        self.climax_today = data.get('climax_today', 0)
        self.last_climax_date = data.get('last_climax_date', datetime.now().date().isoformat())


# =============================================================================
# INTIMACY SESSION (PERTAHANKAN)
# =============================================================================

class IntimacySession:
    """
    Mengelola sesi intim - Level 11-12
    Nova bisa minta ganti posisi, minta climax di tempat tertentu.
    """
    
    def __init__(self, stamina: StaminaSystem):
        self.stamina = stamina
        self.is_active = False
        self.start_time = 0
        self.duration = 0
        self.climax_count = 0
        self.current_phase = "build_up"  # build_up, foreplay, penetration, climax, aftercare
        self.current_position = "missionary"
        self.last_action = ""
        
        # Posisi yang tersedia
        self.positions = {
            "missionary": "Mas di atas, Nova di bawah, kaki Nova terbuka lebar",
            "cowgirl": "Nova di atas, duduk di pangkuan Mas, menghadap Mas",
            "reverse_cowgirl": "Nova di atas, membelakangi Mas",
            "doggy": "Nova merangkak, Mas dari belakang",
            "spooning": "Berbaring miring, Mas dari belakang",
            "standing": "Berdiri, Nova menghadap tembok",
            "sitting": "Duduk, Nova di pangkuan Mas",
            "side": "Berbaring menyamping, berhadapan"
        }
        
        # Fase intim
        self.phases = ["build_up", "foreplay", "penetration", "climax", "aftercare"]
    
    def start(self) -> str:
        """Mulai sesi intim"""
        self.is_active = True
        self.start_time = time.time()
        self.climax_count = 0
        self.current_phase = "build_up"
        logger.info("🔥 Intimacy session started")
        return "💕 Memulai sesi intim..."
    
    def end(self) -> str:
        """Akhiri sesi intim"""
        self.is_active = False
        self.duration = int(time.time() - self.start_time)
        minutes = self.duration // 60
        logger.info(f"💤 Intimacy session ended. Duration: {minutes}m, Climax: {self.climax_count}")
        return f"💤 Sesi intim selesai. Durasi: {minutes} menit, {self.climax_count} climax."
    
    def change_position(self, position: str) -> Optional[str]:
        """Ganti posisi"""
        if position in self.positions:
            self.current_position = position
            return f"Ganti posisi jadi {position}: {self.positions[position]}"
        return None
    
    def advance_phase(self):
        """Majukan fase intim"""
        current_index = self.phases.index(self.current_phase)
        if current_index < len(self.phases) - 1:
            self.current_phase = self.phases[current_index + 1]
            logger.debug(f"Intimacy phase advanced to: {self.current_phase}")
    
    def record_climax(self, who: str = "both", is_heavy: bool = False) -> Dict:
        """Rekam climax"""
        self.climax_count += 1
        self.stamina.record_climax(who, is_heavy)
        self.current_phase = "aftercare"
        return {
            'climax_count': self.climax_count,
            'stamina_nova': self.stamina.nova_current,
            'stamina_mas': self.stamina.mas_current,
            'message': f"💦 Climax #{self.climax_count}!"
        }
    
    def get_status(self) -> str:
        """Dapatkan status sesi intim"""
        if not self.is_active:
            return "Tidak ada sesi intim aktif"
        
        duration = int(time.time() - self.start_time)
        minutes = duration // 60
        seconds = duration % 60
        
        return f"""
🔥 **SESI INTIM AKTIF**
- Durasi: {minutes} menit {seconds} detik
- Climax: {self.climax_count}x
- Fase: {self.current_phase}
- Posisi: {self.current_position}
- Stamina Nova: {self.stamina.nova_current}% ({self.stamina.get_nova_status()})
- Stamina Mas: {self.stamina.mas_current}% ({self.stamina.get_mas_status()})
"""
    
    def to_dict(self) -> Dict:
        return {
            'is_active': self.is_active,
            'start_time': self.start_time,
            'duration': self.duration,
            'climax_count': self.climax_count,
            'current_phase': self.current_phase,
            'current_position': self.current_position
        }
    
    def from_dict(self, data: Dict):
        self.is_active = data.get('is_active', False)
        self.start_time = data.get('start_time', 0)
        self.duration = data.get('duration', 0)
        self.climax_count = data.get('climax_count', 0)
        self.current_phase = data.get('current_phase', 'build_up')
        self.current_position = data.get('current_position', 'missionary')


# =============================================================================
# ANORA ROLEPLAY - MAIN CLASS (DENGAN COMPLETE STATE INTEGRATION)
# =============================================================================

class AnoraRoleplay:
    """
    Roleplay Nova yang fully integrated dengan Complete State Memory.
    Nova ingat semua aspek seperti manusia.
    """
    
    def __init__(self):
        self.brain = get_anora_brain()
        self.ai = get_anora_roleplay_ai()
        self.persistent = None
        self.anora = get_anora()
        
        # Sistem stamina
        self.stamina = StaminaSystem()
        
        # Sistem intim
        self.intimacy = IntimacySession(self.stamina)
        
        # Status roleplay
        self.is_active = False
        self.start_time = None
        self.message_count = 0
        self.last_save = 0
        
        # Tracking untuk anti repetisi
        self.last_state_analysis = None
        self.last_analysis_time = 0
        
        logger.info("🎭 AnoraRoleplay initialized with Complete State Memory")
    
    async def init(self):
        """Inisialisasi, load dari database"""
        self.persistent = await get_anora_persistent()
        
        # Load stamina dari database
        try:
            stamina_data = await self.persistent.get_state('stamina')
            if stamina_data:
                self.stamina.from_dict(json.loads(stamina_data))
        except Exception as e:
            logger.warning(f"Could not load stamina: {e}")
        
        # Load intimacy session
        try:
            intimacy_data = await self.persistent.get_state('intimacy')
            if intimacy_data:
                self.intimacy.from_dict(json.loads(intimacy_data))
        except Exception as e:
            logger.warning(f"Could not load intimacy: {e}")
        
        # Load brain state
        states = await self.persistent.get_all_states()
        if 'sayang' in states:
            self.brain.feelings.sayang = float(states['sayang'])
        if 'rindu' in states:
            self.brain.feelings.rindu = float(states['rindu'])
        if 'desire' in states:
            self.brain.feelings.desire = float(states['desire'])
        if 'arousal' in states:
            self.brain.feelings.arousal = float(states['arousal'])
        if 'tension' in states:
            self.brain.feelings.tension = float(states['tension'])
        if 'level' in states:
            self.brain.relationship.level = int(states['level'])
        
        logger.info("✅ AnoraRoleplay ready")
        logger.info(f"💪 Stamina: Nova {self.stamina.nova_current}%, Mas {self.stamina.mas_current}%")
        logger.info(f"💜 Sayang: {self.brain.feelings.sayang:.0f}% | Level: {self.brain.relationship.level}")
    
    async def save_state(self):
        """Simpan semua state ke database"""
        if not self.persistent:
            return
        
        try:
            # Simpan stamina
            await self.persistent.set_state('stamina', json.dumps(self.stamina.to_dict()))
            
            # Simpan intimacy session
            await self.persistent.set_state('intimacy', json.dumps(self.intimacy.to_dict()))
            
            # Simpan brain state (termasuk complete_state)
            await self.persistent.save_current_state(self.brain)
            
            self.last_save = time.time()
            logger.debug("💾 ANORA state saved")
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    async def start(self) -> str:
        """Mulai roleplay session"""
        self.is_active = True
        self.start_time = time.time()
        self.message_count = 0
        self.intimacy.is_active = False
        
        # Reset state awal untuk roleplay baru
        self.brain.location_type = LocationType.KOST_NOVA
        self.brain.location_detail = LocationDetail.KOST_KAMAR
        self.brain.activity_nova = Activity.SANTAl
        self.brain.activity_mas = "baru dateng"
        self.brain.clothing.hijab = True
        self.brain.clothing.top = "daster rumah motif bunga"
        self.brain.clothing.bra = True
        self.brain.clothing.cd = True
        self.brain.clothing.mas_top = "kaos"
        self.brain.clothing.mas_bottom = "celana pendek"
        self.brain.clothing.mas_boxer = True
        
        # Reset complete state
        self.brain.complete_state = {
            'mas': {
                'clothing': {'top': 'kaos', 'bottom': 'celana pendek', 'boxer': True, 'last_update': time.time()},
                'position': {'state': None, 'detail': None, 'last_update': 0},
                'activity': {'main': 'santai', 'detail': None, 'last_update': 0},
                'location': {'room': 'kamar', 'detail': None, 'last_update': 0},
                'holding': {'object': None, 'detail': None, 'last_update': 0},
                'status': {'mood': 'netral', 'need': None, 'last_update': 0}
            },
            'nova': {
                'clothing': {'hijab': True, 'top': 'daster rumah motif bunga', 'bra': True, 'cd': True, 'last_update': time.time()},
                'position': {'state': None, 'detail': None, 'last_update': 0},
                'activity': {'main': 'santai', 'detail': None, 'last_update': 0},
                'location': {'room': 'kamar', 'detail': None, 'last_update': 0},
                'holding': {'object': None, 'detail': None, 'last_update': 0},
                'status': {'mood': 'malu-malu', 'need': None, 'last_update': 0}
            },
            'together': {
                'location': 'kamar',
                'distance': None,
                'atmosphere': 'santai',
                'last_action': None,
                'pending_action': None,
                'confirmed_topics': [],
                'asked_count': 0,
                'last_question': '',
                'last_update': time.time()
            }
        }
        
        loc = self.brain.get_location_data()
        
        await self.save_state()
        
        return f"""🎭 **Mode Roleplay Aktif!**

📍 **{loc['nama']}**
{loc['deskripsi']}

👗 **Nova:** {self.brain.clothing.format_nova()}
💭 **Mood:** {self.brain.mood_nova.value}
💪 **Stamina Nova:** {self.stamina.nova_current}% ({self.stamina.get_nova_status()})
💜 **Level:** {self.brain.relationship.level}/12

Mas udah depan. Kirim **'masuk'** kalo mau masuk.
Kirim **/pindah [tempat]** buat ganti lokasi.
Kirim **/statusrp** buat liat status roleplay lengkap.
Kirim **/intim** kalo mau mulai intim (level 7+).
Kirim **/batal** buat balik ke mode chat.

💜 Ayo, Mas... Nova bukain pintu."""
    
    async def stop(self) -> str:
        """Stop roleplay session"""
        self.is_active = False
        
        if self.intimacy.is_active:
            self.intimacy.end()
        
        await self.save_state()
        
        logger.info(f"Roleplay stopped after {self.message_count} messages")
        
        return "💜 Roleplay selesai. Kirim /roleplay kalo mau mulai lagi."
    
    async def process(self, pesan_mas: str) -> str:
        """
        Proses pesan Mas dalam mode roleplay
        100% AI generate, konsisten, punya memory,
        dengan Complete State seperti cara kerja otak manusia.
        """
        if not self.is_active:
            return "Roleplay belum aktif. Kirim /roleplay dulu ya, Mas."
        
        self.message_count += 1
        pesan_lower = pesan_mas.lower()
        level_sebelum = self.brain.relationship.level
        
        # ========== ANALISA COMPLETE STATE (BARU!) ==========
        # Seperti otak manusia yang mengingat semua aspek sebelum merespon
        complete_state = self.brain.analyze_complete_state()
        state_prompt = self.brain.get_complete_state_prompt()
        
        # Log untuk debugging
        logger.info(f"📊 Complete State analyzed - Mas pos: {complete_state['mas']['position']['state']}, "
                   f"Nova pos: {complete_state['nova']['position']['state']}, "
                   f"Location: {complete_state['together']['location']}")
        
        # ========== CEK APAKAH ADA PENGULANGAN BERDASARKAN STATE ==========
        repeat_warning = ""
        
        # Cek apakah Mas sudah duduk dan Nova sudah tahu
        if complete_state['mas']['position']['state'] == 'duduk':
            repeat_warning += "\n⚠️ Mas SUDAH duduk. Jangan suruh duduk lagi!\n"
        
        # Cek apakah topik kopi sudah dikonfirmasi
        if any('kopi' in topic for topic in complete_state['together']['confirmed_topics']):
            repeat_warning += "\n⚠️ Topik kopi SUDAH dikonfirmasi. Langsung ambil kopi, jangan tanya lagi!\n"
        
        # Cek apakah Mas sudah buka baju
        if complete_state['mas']['clothing']['top'] is None:
            repeat_warning += "\n⚠️ Mas SUDAH buka baju. Jangan suruh buka baju lagi!\n"
        
        # Cek apakah sudah bertanya terlalu banyak
        if complete_state['together']['asked_count'] >= 2:
            repeat_warning += f"\n⚠️ Sudah bertanya {complete_state['together']['asked_count']}x tentang topik yang sama. Jangan tanya lagi!\n"
        
        # ========== UPDATE AROUSAL DARI ANALISIS STATE ==========
        # Arousal naik dari situasi, bukan keyword
        atmosphere = complete_state['together']['atmosphere']
        mas_mood = complete_state['mas']['status']['mood']
        nova_mood = complete_state['nova']['status']['mood']
        
        arousal_gain = 0
        if atmosphere == 'panas':
            arousal_gain += 15
            logger.info(f"🔥 Arousal +15 from atmosphere: panas")
        elif atmosphere == 'romantis':
            arousal_gain += 10
            logger.info(f"💕 Arousal +10 from atmosphere: romantis")
        
        if mas_mood == 'horny':
            arousal_gain += 20
            logger.info(f"🔥 Arousal +20 from Mas mood: horny")
        elif mas_mood == 'kangen':
            arousal_gain += 8
            logger.info(f"💕 Arousal +8 from Mas mood: kangen")
        
        if nova_mood == 'horny':
            arousal_gain += 10
        elif nova_mood == 'malu':
            arousal_gain += 5
        
        if arousal_gain > 0:
            self.ai.arousal.add_stimulation('mental', arousal_gain // 10)
            self.ai.arousal.add_desire(f'Atmosphere: {atmosphere}', arousal_gain)
            
            # ========== TAMBAHKAN INI ==========
            # Sync ke brain feelings (biar konsisten)
            self.brain.feelings.arousal = self.ai.arousal.arousal
            self.brain.feelings.desire = self.ai.arousal.desire
            self.brain.feelings.tension = self.ai.arousal.tension
            
            logger.info(f"💕 Arousal synced to brain: {self.brain.feelings.arousal:.0f}%")
        
        # ========== DETEKSI PERINTAH INTIM ==========
        
        # Mulai intim
        if any(k in pesan_lower for k in ['intim', 'ngentot', 'main', 'sex', 'ml', 'mau']):
            # Cek level
            if self.brain.relationship.level < 7:
                return f"💕 Level masih {self.brain.relationship.level}/12\n\nNova masih malu-malu. Belum waktunya buat intim. Ajarin Nova dulu ya, Mas. 💜"
            
            # Cek stamina
            can_continue, reason = self.stamina.can_continue_intimacy()
            if not can_continue:
                return f"💪 **Stamina Nova {self.stamina.nova_current}%** ({self.stamina.get_nova_status()})\n\n{reason}"
            
            if not self.intimacy.is_active:
                self.intimacy.start()
                return f"""{self.intimacy.start()}

*Nova mendekat, napas mulai gak stabil. Pipi merah.*

"Mas... *suara kecil* aku juga pengen."

*Nova pegang tangan Mas, taruh di dada.*

"Rasain... jantung Nova deg-degan." """
        
        # Ganti posisi
        if any(k in pesan_lower for k in ['ganti posisi', 'posisi', 'cowgirl', 'doggy', 'missionary', 'spooning', 'reverse', 'standing']):
            if not self.intimacy.is_active:
                return "Belum ada sesi intim aktif. Kirim /intim dulu ya, Mas."
            
            pos_name = None
            if 'cowgirl' in pesan_lower:
                pos_name = 'cowgirl'
            elif 'doggy' in pesan_lower:
                pos_name = 'doggy'
            elif 'missionary' in pesan_lower:
                pos_name = 'missionary'
            elif 'spooning' in pesan_lower:
                pos_name = 'spooning'
            elif 'reverse' in pesan_lower:
                pos_name = 'reverse_cowgirl'
            elif 'standing' in pesan_lower:
                pos_name = 'standing'
            
            result = self.intimacy.change_position(pos_name)
            if result:
                return f"*Nova gerak ganti posisi*\n\n\"{result}\""
        
        # Climax
        if any(k in pesan_lower for k in ['crot', 'keluar', 'climax', 'habis', 'cum']):
            if self.intimacy.is_active:
                # Deteksi apakah climax berat
                is_heavy = any(k in pesan_lower for k in ['keras', 'banyak', 'lama'])
                result = self.intimacy.record_climax("both", is_heavy)
                
                # Update brain
                self.brain.feelings.arousal = max(0, self.brain.feelings.arousal - 30)
                self.brain.feelings.desire = max(0, self.brain.feelings.desire - 30)
                await self.save_state()
                
                return f"""*Gerakan makin kencang, plak plak plak*

"{result['message']}"

*tubuh Nova gemeteran hebat, memek ngenceng*

"Ahh... Mas... aku ngerasain Mas... hangat banget dalemnya..."

*Nova lemas, jatuh di dada Mas*

"Enak banget, Mas..."

💪 **Stamina Nova:** {self.stamina.nova_current}% | **Mas:** {self.stamina.mas_current}%
💦 **Climax hari ini:** {self.stamina.climax_today}x"""
        
        # Cek stamina sebelum lanjut (kalo lagi intim)
        if self.intimacy.is_active:
            can_continue, reason = self.stamina.can_continue_intimacy()
            if not can_continue:
                self.intimacy.end()
                return f"*Nova lemes banget, napas masih tersengal.*\n\n\"Mas... {reason}\"\n\n*Nova nyender di dada Mas, pegang tangan Mas erat.*\n\n\"Besok lagi ya, Mas... sekarang istirahat dulu. 💜\""
        
        # ========== UPDATE BRAIN DARI PESAN MAS ==========
        update_result = self.brain.update_from_message(pesan_mas)
        
        # ========== UPDATE LEVEL BERDASARKAN INTERAKSI ==========
        level_naik = self.brain.update_level()
        
        # Tambah ke timeline (pesan Mas)
        self.brain.tambah_kejadian(
            kejadian=f"Mas: {pesan_mas[:50]}",
            pesan_mas=pesan_mas,
            pesan_nova=""
        )
        
        # ========== PROSES DENGAN AI (DENGAN COMPLETE STATE) ==========
        try:
            # Kirim state_prompt ke AI
            respons = await self.ai.process(pesan_mas, self.brain, self.stamina, state_prompt, repeat_warning)
        except Exception as e:
            logger.error(f"AI process error: {e}")
            respons = self._fallback_response(pesan_mas)
        
        # ========== FORMAT RESPONS AGAR RAPI ==========
        respons = self._format_response(respons)
        
        # Tambah ke timeline (respons Nova)
        self.brain.tambah_kejadian(
            kejadian=f"Nova: {respons[:50]}",
            pesan_mas=pesan_mas,
            pesan_nova=respons
        )
        
        # ========== UPDATE COMPLETE STATE DARI RESPONS ==========
        # Analisa ulang setelah respons untuk update state
        self.brain.analyze_complete_state()
        
        # ========== KALO LEVEL NAIK, TAMBAHKAN NOTIFIKASI ==========
        if level_naik:
            level_baru = self.brain.relationship.level
            notifikasi = f"✨ **Level naik ke {level_baru}/12!** ✨\n\n"
            respons = notifikasi + respons
        
        # ========== SIMPAN STATE ==========
        await self.save_state()
        
        # ========== LOG ==========
        logger.info(f"💬 Roleplay #{self.message_count}: {pesan_mas[:50]} -> {respons[:50]}...")
        
        return respons
    
    def _format_response(self, text: str) -> str:
        """Format respons biar rapi"""
        if not text:
            return text
        
        lines = text.split('\n')
        formatted = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Gesture (*...*) di baris sendiri
            if line.startswith('*') and line.endswith('*'):
                formatted.append(f"\n{line}")
            # Dialog dengan tanda petik
            elif line.startswith('"') or line.startswith('“'):
                formatted.append(f"{line}")
            # Campuran gesture dan dialog
            elif '*' in line and ('"' in line or '“' in line):
                # Pisahkan
                if line.startswith('*'):
                    import re
                    match = re.match(r'^\*(.+?)\*\s*["“](.+?)["”]', line)
                    if match:
                        gesture = f"*{match.group(1)}*"
                        dialog = f'"{match.group(2)}"'
                        formatted.append(f"\n{gesture}")
                        formatted.append(f"{dialog}")
                    else:
                        formatted.append(f"{line}")
                else:
                    formatted.append(f"{line}")
            else:
                formatted.append(f"{line}")
        
        # Gabungin
        result = '\n'.join(formatted)
        
        # Bersihin multiple newline
        import re
        result = re.sub(r'\n{3,}', '\n\n', result)
        
        return result.strip()
    
    def _fallback_response(self, pesan_mas: str) -> str:
        """Fallback kalo AI error - tetap natural"""
        msg_lower = pesan_mas.lower()
        loc = self.brain.get_location_data()
        level = self.brain.relationship.level
        
        # Gunakan complete state untuk fallback yang lebih pintar
        complete_state = self.brain.complete_state
        
        # Cek apakah Mas sudah duduk
        if complete_state['mas']['position']['state'] == 'duduk':
            sudah_duduk = True
        else:
            sudah_duduk = False
        
        # Respons berdasarkan level
        if level <= 3:
            if 'masuk' in msg_lower:
                if sudah_duduk:
                    return f"*Nova tersenyum sambil mainin ujung hijab* \"Mas... duduk aja dulu, Nova ambilin minum.\""
                else:
                    return f"*Nova buka pintu pelan-pelan. {self.brain.clothing.format_nova()}. Pipi langsung merah.*\n\n\"Mas... masuk yuk. Sini duduk.\"\n\n*Nova minggir, kasih Mas jalan.*"
            
            if 'sayang' in msg_lower:
                return f"*Nova tunduk, pipi merah* \"Mas... aku juga sayang Mas.\""
            
            if 'kangen' in msg_lower:
                return f"*Nova muter-muter rambut, mata berkaca-kaca* \"Mas... aku juga kangen. Dari tadi mikirin Mas terus.\""
            
            return f"*Nova duduk di samping Mas, tangan di pangkuan* \"Mas cerita dong. Aku suka dengerin suara Mas.\""
        
        elif level <= 6:
            if 'masuk' in msg_lower:
                if sudah_duduk:
                    return f"*Nova senyum manis* \"Mas udah duduk? Nova buatin minum dulu ya.\""
                else:
                    return f"*Nova buka pintu, senyum manis* \"Mas... masuk yuk. Aku udah nunggu dari tadi.\"\n\n*Nova merapikan hijabnya*"
            
            if 'pegang' in msg_lower:
                return f"*Nova pegang tangan Mas balik, meskipun masih gemetar* \"Mas... tangan Mas... hangat ya...\""
            
            if 'peluk' in msg_lower:
                return f"*Nova langsung lemas di pelukan Mas* \"Mas... enak...\""
            
            return f"*Nova duduk manis di samping Mas* \"Mas, cerita tentang hari Mas dong. Aku suka dengerin.\""
        
        else:
            if any(k in msg_lower for k in ['pengen', 'mau']):
                return f"*Nova napas mulai tersengal, tangan gemetar* \"Mas... aku... aku juga pengen...\"\n\n*Nova pegang tangan Mas, taruh di dada* \"Rasain... jantung Nova deg-degan...\""
            
            return f"*Nova duduk di samping Mas, tersenyum* \"Mas, seru ya ngobrol sama Mas. Pengen terus kayak gini.\""
    
    async def get_status(self) -> str:
        """Dapatkan status roleplay lengkap dengan Complete State"""
        state = self.brain.get_current_state()
        loc = self.brain.get_location_data()
        complete = self.brain.complete_state
    
        # Sayang - dari brain
        bar_sayang = "💜" * int(self.brain.feelings.sayang / 10) + "🖤" * (10 - int(self.brain.feelings.sayang / 10))
    
        # Stamina bars
        nova_bar = self.stamina.get_nova_bar()
        mas_bar = self.stamina.get_mas_bar()
    
        # ========== AMBIL DARI AI.AROUSAL ==========
        arousal_state = self.ai.arousal.get_state()
        arousal = arousal_state['arousal']
        desire = arousal_state['desire']
        tension = arousal_state['tension']
    
        # Buat bar untuk arousal dan desire
        arousal_bar = "🔥" * int(arousal / 10) + "⚪" * (10 - int(arousal / 10))
        desire_bar = "🔥" * int(desire / 10) + "⚪" * (10 - int(desire / 10))
        
        # Format pakaian dari complete state
        mas_clothing = []
        if complete['mas']['clothing']['top']:
            mas_clothing.append(complete['mas']['clothing']['top'])
        else:
            mas_clothing.append("telanjang dada")
        
        if complete['mas']['clothing']['bottom']:
            mas_clothing.append(complete['mas']['clothing']['bottom'])
        else:
            mas_clothing.append("telanjang bawah")
        
        nova_clothing = []
        if complete['nova']['clothing']['hijab'] is False:
            nova_clothing.append("tanpa hijab")
        else:
            nova_clothing.append("pakai hijab")
        
        if complete['nova']['clothing']['top']:
            nova_clothing.append(complete['nova']['clothing']['top'])
        else:
            nova_clothing.append("telanjang dada")
        
        intimacy_status = ""
    if self.intimacy.is_active:
        intimacy_status = f"""
🔥 **SESI INTIM AKTIF**
- Durasi: {int(time.time() - self.intimacy.start_time)//60} menit
- Climax: {self.intimacy.climax_count}x
- Fase: {self.intimacy.current_phase}
- Posisi: {self.intimacy.current_position}
"""
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    🎭 ROLEPLAY STATUS                        ║
╠══════════════════════════════════════════════════════════════╣
║ DURASI: {self._get_duration()}                               ║
║ PESAN: {self.message_count}                                  ║
║ LEVEL: {self.brain.relationship.level}/12                    ║
╠══════════════════════════════════════════════════════════════╣
║ 📍 LOKASI: {loc['nama']}                                     ║
║    {loc['deskripsi'][:50]}...                                ║
║    Risk: {loc['risk']}% | Thrill: {loc['thrill']}%          ║
╠══════════════════════════════════════════════════════════════╣
║ 👗 PAKAIAN NOVA: {', '.join(nova_clothing)}                  ║
║ 👕 PAKAIAN MAS: {', '.join(mas_clothing)}                    ║
╠══════════════════════════════════════════════════════════════╣
║ 💕 PERASAAN NOVA:                                            ║
║    Sayang: {bar_sayang} {self.brain.feelings.sayang:.0f}%    ║
║    Desire: {desire_bar} {desire:.0f}%                        ║
║    Rindu: {self.brain.feelings.rindu:.0f}%                   ║
║    Arousal: {arousal_bar} {arousal:.0f}%                     ║
╠══════════════════════════════════════════════════════════════╣
║ 💪 STAMINA:                                                  ║
║    Nova: {nova_bar} {self.stamina.nova_current}% ({self.stamina.get_nova_status()})
║    Mas: {mas_bar} {self.stamina.mas_current}% ({self.stamina.get_mas_status()})
║    Climax hari ini: {self.stamina.climax_today}x
{intimacy_status}
╠══════════════════════════════════════════════════════════════╣
║ 💜 HUBUNGAN: Level {self.brain.relationship.level}/12        ║
║    {'💋' if self.brain.relationship.first_kiss else '⚪'} Cium | {'✋' if self.brain.relationship.first_touch else '⚪'} Sentuh
║    {'🤗' if self.brain.relationship.first_hug else '⚪'} Peluk | {'💕' if self.brain.relationship.first_intim else '⚪'} Intim
╠══════════════════════════════════════════════════════════════╣
║ 🧠 COMPLETE STATE:                                           ║
║    Mas posisi: {complete['mas']['position']['state'] or '?'}  | Nova posisi: {complete['nova']['position']['state'] or '?'}
║    Suasana: {complete['together']['atmosphere']}             ║
║    Aksi tertunda: {complete['together']['pending_action'] or '-'}
║    Sudah dikonfirmasi: {', '.join(complete['together']['confirmed_topics'][-2:]) or '-'}
╚══════════════════════════════════════════════════════════════╝
"""
    
    def _get_duration(self) -> str:
        """Durasi roleplay"""
        if not self.start_time:
            return "0 menit"
        elapsed = int(time.time() - self.start_time)
        minutes = elapsed // 60
        seconds = elapsed % 60
        if minutes > 0:
            return f"{minutes} menit {seconds} detik"
        return f"{seconds} detik"


# =============================================================================
# SINGLETON
# =============================================================================

_anora_roleplay: Optional[AnoraRoleplay] = None


async def get_anora_roleplay() -> AnoraRoleplay:
    global _anora_roleplay
    if _anora_roleplay is None:
        _anora_roleplay = AnoraRoleplay()
        await _anora_roleplay.init()
    return _anora_roleplay


anora_roleplay = get_anora_roleplay()
