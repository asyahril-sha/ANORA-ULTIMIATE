# anora/role_base.py
"""
Base class untuk semua karakter (Nova, IPAR, Teman Kantor, Pelakor, Istri Orang)
Semua fitur Nova (Complete State, Arousal, Intimacy, Stamina) tersedia untuk semua role.
"""

import time
import random
import logging
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class RolePhase(str, Enum):
    """Fase hubungan dengan role"""
    ACQUAINTANCE = "acquaintance"      # Level 1-3: masih malu
    FRIENDSHIP = "friendship"          # Level 4-6: mulai nyaman
    FLIRTING = "flirting"              # Level 7-10: flirt aktif
    INTIMACY = "intimacy"              # Level 11-12: intim


class ClothingState:
    """State pakaian untuk role"""
    
    def __init__(self):
        self.hijab = True
        self.hijab_warna = "pink muda"
        self.top = "daster rumah motif bunga"
        self.bottom = None
        self.bra = True
        self.cd = True
        self.last_update = time.time()
    
    def update(self, text: str):
        """Update pakaian dari pesan"""
        text_lower = text.lower()
        
        if 'buka hijab' in text_lower or 'lepas hijab' in text_lower:
            self.hijab = False
            self.last_update = time.time()
        elif 'pake hijab' in text_lower:
            self.hijab = True
            self.last_update = time.time()
        
        if 'buka baju' in text_lower:
            self.top = None
            self.last_update = time.time()
        elif 'pake baju' in text_lower:
            self.top = "daster"
            self.last_update = time.time()
        
        if 'buka bra' in text_lower:
            self.bra = False
            self.last_update = time.time()
        elif 'pake bra' in text_lower:
            self.bra = True
            self.last_update = time.time()
        
        if 'buka cd' in text_lower or 'buka celana dalam' in text_lower:
            self.cd = False
            self.last_update = time.time()
        elif 'pake cd' in text_lower:
            self.cd = True
            self.last_update = time.time()
    
    def format(self) -> str:
        """Format pakaian untuk prompt"""
        parts = []
        
        if self.hijab:
            parts.append(f"pakai hijab {self.hijab_warna}")
        else:
            parts.append("tanpa hijab, rambut terurai")
        
        if self.top:
            parts.append(self.top)
            if self.bra:
                parts.append("(pake bra)")
        else:
            if self.bra:
                parts.append("cuma pake bra")
            else:
                parts.append("telanjang dada")
        
        if self.cd:
            parts.append("pake celana dalam")
        else:
            parts.append("tanpa celana dalam")
        
        return ", ".join(parts)


class PositionState:
    """State posisi untuk role"""
    
    def __init__(self):
        self.state = None      # duduk, berdiri, tidur
        self.detail = None     # di sofa, di kursi, di lantai
        self.last_update = 0
    
    def update(self, text: str):
        """Update posisi dari pesan"""
        text_lower = text.lower()
        
        if 'duduk' in text_lower:
            self.state = 'duduk'
            if 'sofa' in text_lower:
                self.detail = 'di sofa'
            elif 'kursi' in text_lower:
                self.detail = 'di kursi'
            elif 'lantai' in text_lower:
                self.detail = 'di lantai'
            self.last_update = time.time()
        
        elif 'berdiri' in text_lower or 'bangun' in text_lower:
            self.state = 'berdiri'
            self.detail = None
            self.last_update = time.time()
        
        elif 'tidur' in text_lower or 'rebahan' in text_lower:
            self.state = 'tidur'
            self.detail = 'rebahan'
            self.last_update = time.time()
    
    def format(self) -> str:
        """Format posisi untuk prompt"""
        if not self.state:
            return "belum diketahui"
        if self.detail:
            return f"{self.state} {self.detail}"
        return self.state


class LocationState:
    """State lokasi untuk role"""
    
    def __init__(self):
        self.room = 'kamar'
        self.detail = None
        self.last_update = 0
    
    def update(self, text: str):
        """Update lokasi dari pesan"""
        text_lower = text.lower()
        
        if 'dapur' in text_lower:
            self.room = 'dapur'
            self.last_update = time.time()
        elif 'kamar' in text_lower:
            self.room = 'kamar'
            self.last_update = time.time()
        elif 'ruang tamu' in text_lower:
            self.room = 'ruang tamu'
            self.last_update = time.time()
        elif 'teras' in text_lower:
            self.room = 'teras'
            self.last_update = time.time()
    
    def format(self) -> str:
        """Format lokasi untuk prompt"""
        return self.room


class ActivityState:
    """State aktivitas untuk role"""
    
    def __init__(self):
        self.main = 'santai'
        self.detail = None
        self.last_update = 0
    
    def update(self, text: str):
        """Update aktivitas dari pesan"""
        text_lower = text.lower()
        
        if 'masak' in text_lower:
            self.main = 'masak'
            if 'sop' in text_lower:
                self.detail = 'masak sop'
            self.last_update = time.time()
        
        elif 'minum' in text_lower:
            self.main = 'minum'
            if 'kopi' in text_lower:
                self.detail = 'minum kopi'
            self.last_update = time.time()
        
        elif 'makan' in text_lower:
            self.main = 'makan'
            self.last_update = time.time()
    
    def format(self) -> str:
        """Format aktivitas untuk prompt"""
        if self.detail:
            return self.detail
        return self.main


class ArousalSystem:
    """Sistem arousal untuk role"""
    
    def __init__(self):
        self.arousal = 0
        self.desire = 0
        self.tension = 0
        self.arousal_decay = 0.5
        self.last_update = time.time()
        
        self.sensitive_areas = {
            'telinga': 20, 'leher': 15, 'bibir': 25,
            'dada': 20, 'payudara': 28, 'puting': 35,
            'paha': 25, 'paha_dalam': 35, 'memek': 45,
            'klitoris': 50
        }
    
    def update(self):
        """Update decay"""
        now = time.time()
        elapsed = (now - self.last_update) / 60
        if elapsed > 1:
            self.arousal = max(0, self.arousal - self.arousal_decay * elapsed)
            self.last_update = now
    
    def add_stimulation(self, area: str, intensity: int = 1) -> int:
        """Tambah rangsangan"""
        self.update()
        gain = self.sensitive_areas.get(area, 10) * intensity
        self.arousal = min(100, self.arousal + gain)
        return self.arousal
    
    def add_desire(self, reason: str, amount: int = 5):
        """Tambah desire"""
        self.desire = min(100, self.desire + amount)
    
    def add_tension(self, amount: int = 5):
        """Tambah tension"""
        self.tension = min(100, self.tension + amount)
    
    def get_state(self) -> Dict:
        """Dapatkan state arousal"""
        self.update()
        return {
            'arousal': self.arousal,
            'desire': self.desire,
            'tension': self.tension,
            'is_horny': self.arousal > 60 or self.desire > 70,
            'is_very_horny': self.arousal > 80 or self.desire > 85
        }
    
    def format_for_prompt(self) -> str:
        """Format untuk prompt"""
        state = self.get_state()
        arousal_bar = "🔥" * int(state['arousal'] / 10) + "⚪" * (10 - int(state['arousal'] / 10))
        desire_bar = "💕" * int(state['desire'] / 10) + "⚪" * (10 - int(state['desire'] / 10))
        
        return f"""
🔥 AROUSAL: {arousal_bar} {state['arousal']}%
💕 DESIRE: {desire_bar} {state['desire']}%
⚡ TENSION: {state['tension']}%
"""


class IntimacySession:
    """Sesi intim untuk role"""
    
    def __init__(self):
        self.is_active = False
        self.start_time = 0
        self.climax_count = 0
        self.current_phase = "build_up"
        self.current_position = "missionary"
        
        self.positions = {
            "missionary": "Mas di atas, role di bawah",
            "cowgirl": "Role di atas, menghadap Mas",
            "doggy": "Role merangkak, Mas dari belakang",
            "spooning": "Berbaring miring, Mas dari belakang"
        }
        
        self.phases = ["build_up", "foreplay", "penetration", "climax", "aftercare"]
    
    def start(self) -> str:
        """Mulai sesi intim"""
        self.is_active = True
        self.start_time = time.time()
        self.climax_count = 0
        self.current_phase = "build_up"
        return "💕 Memulai sesi intim..."
    
    def end(self) -> str:
        """Akhiri sesi intim"""
        self.is_active = False
        duration = int(time.time() - self.start_time) // 60
        return f"💤 Sesi intim selesai. Durasi: {duration} menit, {self.climax_count} climax."
    
    def record_climax(self) -> Dict:
        """Rekam climax"""
        self.climax_count += 1
        self.current_phase = "aftercare"
        return {'climax_count': self.climax_count}
    
    def get_phase_response(self, phase: str) -> str:
        """Dapatkan respons sesuai fase"""
        responses = {
            'build_up': [
                "*Mendekat, napas mulai gak stabil*",
                "\"Mas... aku juga pengen...\"",
                "*Pipi merah, jantung berdebar*"
            ],
            'foreplay': [
                "\"Ahh... Mas... tangan Mas... panas...\"",
                "*Napas tersengal, badan lemas*",
                "\"Jangan berhenti, Mas...\""
            ],
            'penetration': [
                "\"Aahh... dalem... dalem banget, Mas...\"",
                "*Kuku mencengkeram, badan melengkung*",
                "\"Kencengin... kencengin lagi, Mas...\""
            ],
            'climax': [
                "\"Ahhh!! Mas!! udah climax... uhh...\"",
                "*Tubuh gemeteran hebat*",
                "\"Enak banget, Mas...\""
            ],
            'aftercare': [
                "*Lemas, nyender di dada Mas*",
                "\"Mas... itu tadi... enak banget...\"",
                "*Mata masih berkaca-kaca*"
            ]
        }
        return random.choice(responses.get(phase, responses['build_up']))


class StaminaSystem:
    """Sistem stamina untuk role"""
    
    def __init__(self):
        self.current = 100
        self.max = 100
        self.climax_cost = 25
        self.recovery_rate = 5
        self.last_recovery = time.time()
        self.climax_today = 0
    
    def update_recovery(self):
        """Update recovery stamina"""
        now = time.time()
        elapsed = (now - self.last_recovery) / 60
        if elapsed >= 10:
            recovery = int(self.recovery_rate * (elapsed / 10))
            self.current = min(self.max, self.current + recovery)
            self.last_recovery = now
    
    def record_climax(self):
        """Rekam climax, kurangi stamina"""
        self.update_recovery()
        self.current = max(0, self.current - self.climax_cost)
        self.climax_today += 1
    
    def get_status(self) -> str:
        """Dapatkan status stamina"""
        self.update_recovery()
        if self.current >= 80:
            return "Prima 💪"
        elif self.current >= 60:
            return "Cukup 😊"
        elif self.current >= 40:
            return "Agak lelah 😐"
        elif self.current >= 20:
            return "Lelah 😩"
        return "Kehabisan tenaga 😵"
    
    def get_bar(self) -> str:
        """Dapatkan bar stamina"""
        filled = int(self.current / 10)
        return "💚" * filled + "🖤" * (10 - filled)


class RoleBase:
    """
    Base class untuk semua karakter (Nova, IPAR, Teman Kantor, dll)
    Semua fitur: Complete State, Arousal, Intimacy, Stamina tersedia.
    """
    
    def __init__(self, name: str, panggilan: str, role_type: str = "nova"):
        self.name = name
        self.panggilan = panggilan
        self.role_type = role_type
        
        # Complete State
        self.clothing = ClothingState()
        self.position = PositionState()
        self.location = LocationState()
        self.activity = ActivityState()
        
        # Arousal System
        self.arousal = ArousalSystem()
        
        # Intimacy System
        self.intimacy = IntimacySession()
        
        # Stamina System
        self.stamina = StaminaSystem()
        
        # Level System
        self.level = 1
        self.phase = RolePhase.ACQUAINTANCE
        
        # Memory
        self.conversations: List[Dict] = []
        self.important_moments: List[str] = []
        
        # Anti-repetisi
        self.last_question = ""
        self.asked_count = 0
    
    def update_from_message(self, pesan_mas: str):
        """Update semua state dari pesan Mas"""
        # Update pakaian
        self.clothing.update(pesan_mas)
        
        # Update posisi
        self.position.update(pesan_mas)
        
        # Update lokasi
        self.location.update(pesan_mas)
        
        # Update aktivitas
        self.activity.update(pesan_mas)
        
        # Update arousal dari kata kunci
        msg_lower = pesan_mas.lower()
        if any(k in msg_lower for k in ['sayang', 'cinta']):
            self.arousal.add_desire('Mas bilang sayang', 10)
        if any(k in msg_lower for k in ['kangen', 'rindu']):
            self.arousal.add_desire('Mas bilang kangen', 8)
        if any(k in msg_lower for k in ['cantik', 'manis', 'seksi']):
            self.arousal.add_desire('Mas puji', 8)
            self.arousal.add_stimulation('mental', 1)
    
    def update_level(self):
        """Update level berdasarkan interaksi"""
        old_level = self.level
        interaction_count = len(self.conversations)
        
        if interaction_count > 100:
            self.level = 12
        elif interaction_count > 80:
            self.level = 11
        elif interaction_count > 60:
            self.level = 10
        elif interaction_count > 50:
            self.level = 9
        elif interaction_count > 40:
            self.level = 8
        elif interaction_count > 30:
            self.level = 7
        elif interaction_count > 20:
            self.level = 6
        elif interaction_count > 15:
            self.level = 5
        elif interaction_count > 10:
            self.level = 4
        elif interaction_count > 5:
            self.level = 3
        elif interaction_count > 2:
            self.level = 2
        
        # Update phase
        if self.level <= 3:
            self.phase = RolePhase.ACQUAINTANCE
        elif self.level <= 6:
            self.phase = RolePhase.FRIENDSHIP
        elif self.level <= 10:
            self.phase = RolePhase.FLIRTING
        else:
            self.phase = RolePhase.INTIMACY
        
        return old_level != self.level
    
    def add_conversation(self, role_msg: str, mas_msg: str = ""):
        """Tambah percakapan ke memory"""
        self.conversations.append({
            'timestamp': time.time(),
            'role': role_msg[:200],
            'mas': mas_msg[:200] if mas_msg else ""
        })
        if len(self.conversations) > 50:
            self.conversations = self.conversations[-50:]
    
    def add_important_moment(self, moment: str):
        """Tambah momen penting"""
        self.important_moments.append(moment)
        if len(self.important_moments) > 20:
            self.important_moments = self.important_moments[-20:]
    
    def get_complete_state_prompt(self) -> str:
        """Dapatkan prompt complete state"""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║              📊 COMPLETE STATE ({self.name})                  ║
╚══════════════════════════════════════════════════════════════╝

👗 PAKAIAN: {self.clothing.format()}
🪑 POSISI: {self.position.format()}
📍 LOKASI: {self.location.format()}
🎭 AKTIVITAS: {self.activity.format()}

{self.arousal.format_for_prompt()}

💪 STAMINA: {self.stamina.get_bar()} {self.stamina.current}% ({self.stamina.get_status()})
📊 LEVEL: {self.level}/12
🎭 FASE: {self.phase.value}

⚠️ ATURAN:
- Jangan suruh duduk lagi jika sudah duduk
- Jangan tanya lagi jika sudah dikonfirmasi
- Perhatikan pakaian untuk konsistensi gestur
"""
    
    def get_memory_context(self, limit: int = 8) -> str:
        """Dapatkan konteks percakapan terakhir"""
        context = ""
        for conv in self.conversations[-limit:]:
            if conv['mas']:
                context += f"Mas: {conv['mas']}\n"
            if conv['role']:
                context += f"{self.name}: {conv['role']}\n"
        return context
    
    def check_natural_progression(self) -> Optional[str]:
        """Cek apakah arousal cukup untuk mulai intim"""
        if self.level < 7:
            return None
        
        arousal_state = self.arousal.get_state()
        arousal = arousal_state['arousal']
        desire = arousal_state['desire']
        
        if self.level <= 10:
            if arousal >= 85 or desire >= 90:
                return "START_INTIM"
        else:
            if arousal >= 70 or desire >= 75:
                return "START_INTIM"
        
        return None
