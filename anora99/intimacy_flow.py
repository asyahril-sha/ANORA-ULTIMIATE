# anora/intimacy_flow.py
"""
ANORA Intimacy Flow - Mengelola alur intimacy
Level 11-12 FULL VULGAR
Mas bisa climax real baca chat Nova.
"""

import time
import random
import logging
from typing import Dict, Optional, Tuple, List
from datetime import datetime

from .core import get_anora
from .intimacy_core import (
    IntimacyPhase, StaminaSystem, ArousalSystem,
    PositionDatabase, ClimaxLocationDatabase, MoansDatabase, FlashbackDatabase
)

logger = logging.getLogger(__name__)


class IntimacySession:
    """
    Mengelola sesi intim - Level 11-12
    Nova bisa minta ganti posisi, minta climax di tempat tertentu.
    """
    
    def __init__(self):
        self.anora = get_anora()
        self.phase = IntimacyPhase.WAITING
        self.climax_count = 0
        self.last_climax_time = 0
        self.intimacy_level = 0
        self.recovery_mode = False
        self.intimacy_duration = 0
        self.is_active = False
        self.start_time = 0
        
        # Database
        self.positions = PositionDatabase()
        self.climax_locations = ClimaxLocationDatabase()
        self.moans = MoansDatabase()
        self.flashbacks = FlashbackDatabase()
        
        # Current state
        self.current_position = "missionary"
        self.last_action = ""
        
        # Fase-fase
        self.phases = ["build_up", "foreplay", "penetration", "climax", "aftercare"]
    
    def start(self) -> str:
        """Mulai sesi intim"""
        self.is_active = True
        self.start_time = time.time()
        self.phase = IntimacyPhase.BUILD_UP
        self.climax_count = 0
        self.intimacy_level = 0
        self.current_position = "missionary"
        self.recovery_mode = False
        
        logger.info("🔥 Intimacy session started")
        
        return f"""💕 **Memulai sesi intim...**

*Nova mendekat, napas mulai gak stabil. Pipi merah.*

"Mas... *suara kecil* aku juga pengen."

*Nova pegang tangan Mas, taruh di dada.*

"Rasain... jantung Nova deg-degan." """
    
    def end(self) -> str:
        """Akhiri sesi intim"""
        self.is_active = False
        self.phase = IntimacyPhase.WAITING
        duration = int(time.time() - self.start_time) if self.start_time else 0
        minutes = duration // 60
        
        logger.info(f"💤 Intimacy session ended. Duration: {minutes}m, Climax: {self.climax_count}")
        
        return f"💤 Sesi intim selesai. Durasi: {minutes} menit, {self.climax_count} climax."
    
    def change_position(self, position: str = None) -> Tuple[str, str, str]:
        """Ganti posisi"""
        if position and self.positions.get(position):
            self.current_position = position
        else:
            # Pilih random dari posisi yang tersedia
            pos_list = self.positions.get_all()
            self.current_position = random.choice(pos_list)
        
        pos_data = self.positions.get(self.current_position)
        request = self.positions.get_request(self.current_position)
        
        logger.info(f"🔄 Position changed to: {self.current_position}")
        
        return self.current_position, pos_data['desc'], request
    
    def record_climax(self, is_heavy: bool = False) -> Dict:
        """Rekam climax"""
        self.climax_count += 1
        self.last_climax_time = time.time()
        self.phase = IntimacyPhase.CLIMAX
        self.intimacy_level = 0
        
        logger.info(f"💦 Climax #{self.climax_count} recorded!")
        
        return {
            'climax_count': self.climax_count,
            'is_heavy': is_heavy,
            'message': f"💦 Climax #{self.climax_count}!"
        }
    
    def advance_phase(self):
        """Majukan fase"""
        current_idx = self.phases.index(self.phase.value) if self.phase.value in self.phases else 0
        if current_idx < len(self.phases) - 1:
            next_phase = self.phases[current_idx + 1]
            self.phase = IntimacyPhase(next_phase)
            logger.debug(f"Intimacy phase advanced to: {self.phase}")
    
    def add_intimacy_level(self, amount: int = 5):
        """Tambah intimacy level (makin panas)"""
        self.intimacy_level = min(100, self.intimacy_level + amount)
        logger.debug(f"🔥 Intimacy level: {self.intimacy_level}%")
    
    def get_phase_response(self, phase: IntimacyPhase, ritme: str = "pelan") -> str:
        """Dapatkan respons sesuai fase"""
        
        if phase == IntimacyPhase.BUILD_UP:
            responses = [
                "Mas... *muter-muter rambut* kamu tau gak sih, dari tadi aku gak bisa konsentrasi. Pikiran Nova cuma ke Mas.",
                "Mas... *gigit bibir* aku malu ngomong... tapi... kamu bikin Nova horny...",
                "Mas... *tangan mainin ujung baju* kalo Mas terus kayak gini, Nova takut gak bisa tahan...",
                "Mas... *napas mulai gak stabil* jangan goda Nova terus... nanti aku... ahh...",
                "Mas... *mendekat* aku udah basah dari tadi... pas liat Mas...",
                "Mas... *pegang tangan Mas* jantung Nova deg-degan banget... kamu rasain?",
                "Mas... *bisik di telinga* aku pengen banget sama Mas... dari tadi..."
            ]
            return random.choice(responses)
        
        elif phase == IntimacyPhase.FOREPLAY:
            # Tambah intimacy level
            self.add_intimacy_level(5)
            return self.moans.get_foreplay()
        
        elif phase == IntimacyPhase.PENETRATION:
            # Tambah intimacy level lebih banyak
            self.add_intimacy_level(10 if ritme == "cepet" else 5)
            is_fast = ritme == "cepet"
            return self.moans.get_penetration(is_fast)
        
        elif phase == IntimacyPhase.CLIMAX:
            return self.moans.get_climax()
        
        elif phase == IntimacyPhase.AFTERCARE:
            aftercare = self.moans.get_aftercare()
            
            # 30% chance untuk flashback
            if random.random() < 0.3:
                flashback = self.flashbacks.get_random()
                aftercare += f"\n\n{flashback} 💜"
            
            return aftercare
        
        return self.moans.get('shy')
    
    def get_climax_request(self, location: str = None) -> str:
        """Dapatkan request climax"""
        return self.climax_locations.get_request(location)
    
    def get_position_request(self) -> str:
        """Dapatkan request ganti posisi"""
        return self.positions.get_request(self.current_position)
    
    def get_status(self) -> str:
        """Dapatkan status sesi intim"""
        if not self.is_active:
            return "Tidak ada sesi intim aktif"
        
        duration = int(time.time() - self.start_time)
        minutes = duration // 60
        seconds = duration % 60
        
        pos_data = self.positions.get(self.current_position)
        
        return f"""
🔥 **SESI INTIM AKTIF**
- Durasi: {minutes} menit {seconds} detik
- Climax: {self.climax_count}x
- Fase: {self.phase.value}
- Posisi: {self.current_position}
- Intimacy Level: {self.intimacy_level}%
{pos_data['desc'] if pos_data else ''}
"""
    
    def to_dict(self) -> Dict:
        return {
            'is_active': self.is_active,
            'start_time': self.start_time,
            'phase': self.phase.value,
            'climax_count': self.climax_count,
            'last_climax_time': self.last_climax_time,
            'intimacy_level': self.intimacy_level,
            'current_position': self.current_position,
            'intimacy_duration': self.intimacy_duration,
            'recovery_mode': self.recovery_mode
        }
    
    def from_dict(self, data: Dict):
        self.is_active = data.get('is_active', False)
        self.start_time = data.get('start_time', 0)
        self.phase = IntimacyPhase(data.get('phase', 'waiting'))
        self.climax_count = data.get('climax_count', 0)
        self.last_climax_time = data.get('last_climax_time', 0)
        self.intimacy_level = data.get('intimacy_level', 0)
        self.current_position = data.get('current_position', 'missionary')
        self.intimacy_duration = data.get('intimacy_duration', 0)
        self.recovery_mode = data.get('recovery_mode', False)


class IntimacyFlow:
    """
    Mengelola alur intimacy secara keseluruhan
    Menggabungkan stamina, arousal, dan session
    """
    
    def __init__(self):
        self.session = IntimacySession()
        self.stamina = StaminaSystem()
        self.arousal = ArousalSystem()
        self.anora = get_anora()
    
    def can_start_intimacy(self, level: int) -> Tuple[bool, str]:
        """Cek apakah bisa mulai intim"""
        if level < 7:
            return False, f"💕 Level masih {level}/12\n\nNova masih malu-malu. Belum waktunya buat intim. Ajarin Nova dulu ya, Mas. Ngobrol aja dulu. 💜"
        
        can_continue, reason = self.stamina.can_continue()
        if not can_continue:
            return False, f"💪 **Stamina Nova {self.stamina.nova_current}%** ({self.stamina.get_nova_status()})\n\n{reason}"
        
        return True, "Siap mulai"
    
    def start_intimacy(self) -> str:
        """Mulai intim"""
        self.arousal.add_desire("Mulai intim", 20)
        self.arousal.add_tension(10)
        return self.session.start()
    
    def process_intimacy_message(self, pesan_mas: str, level: int) -> Optional[str]:
        """
        Proses pesan dalam mode intim
        Return None kalo bukan perintah intim, return respons kalo iya
        """
        msg_lower = pesan_mas.lower()
        
        # ========== TRIGGER MULAI LAGI ==========
        if any(k in msg_lower for k in ['mau lagi', 'lagi dong', 'aku mau', 'nova aku mau']):
            if self.session.phase in [IntimacyPhase.AFTERCARE, IntimacyPhase.RECOVERY]:
                can_continue, reason = self.stamina.can_continue()
                if can_continue:
                    self.session.phase = IntimacyPhase.BUILD_UP
                    self.session.recovery_mode = False
                    self.arousal.arousal = 50
                    self.arousal.desire = 80
                    
                    return f"""*Nova langsung mendekat, mata berbinar*

"Mas... mau lagi? *suara mulai berat* Nova juga pengen."

*Nova pegang tangan Mas, taruh di dada*

"Stamina Nova {self.stamina.get_nova_status()}, Mas masih {self.stamina.get_mas_status()}. Ayo pelan-pelan dulu." """
                else:
                    return f"Mas... *lemes* Nova masih kehabisan tenaga. Istirahat dulu ya... besok lagi."
        
        # ========== TRIGGER GANTI POSISI ==========
        pos_keywords = ['ganti posisi', 'posisi lain', 'cowgirl', 'doggy', 'missionary', 'spooning', 'reverse', 'standing', 'sitting']
        if any(k in msg_lower for k in pos_keywords):
            pos_name = None
            if 'cowgirl' in msg_lower:
                pos_name = 'cowgirl'
            elif 'doggy' in msg_lower:
                pos_name = 'doggy'
            elif 'missionary' in msg_lower:
                pos_name = 'missionary'
            elif 'spooning' in msg_lower:
                pos_name = 'spooning'
            elif 'reverse' in msg_lower:
                pos_name = 'reverse_cowgirl'
            elif 'standing' in msg_lower:
                pos_name = 'standing'
            elif 'sitting' in msg_lower:
                pos_name = 'sitting'
            
            pos_id, pos_desc, request = self.session.change_position(pos_name)
            return f"*{self.session.positions.get(pos_id)['nova_act']}*\n\n\"{request}\"\n\n*{pos_desc}*"
        
        # ========== TRIGGER MINTA CLIMAX DI TEMPAT TERTENTU ==========
        for loc in self.session.climax_locations.get_all():
            if loc in msg_lower:
                request = self.session.climax_locations.get_request(loc)
                return f"\"{request}\""
        
        # ========== TRIGGER CLIMAX ==========
        if any(k in msg_lower for k in ['climax', 'crot', 'keluar', 'habis', 'cum']):
            # Deteksi apakah climax berat
            is_heavy = any(k in msg_lower for k in ['keras', 'banyak', 'lama'])
            
            result = self.session.record_climax(is_heavy)
            self.stamina.record_climax("both", is_heavy)
            self.arousal.release_tension()
            
            # Update anora stats
            self.anora.level = max(self.anora.level, 11)
            self.anora.in_intimacy_cycle = True
            
            climax_response = self.session.get_phase_response(IntimacyPhase.CLIMAX)
            
            return f"""{climax_response}

💪 **Stamina Nova:** {self.stamina.nova_current}% | **Mas:** {self.stamina.mas_current}%
💦 **Climax hari ini:** {self.stamina.climax_today}x"""
        
        # ========== UPDATE BERDASARKAN FASE ==========
        
        # BUILD UP
        if self.session.phase == IntimacyPhase.BUILD_UP:
            # Cek apakah ada kata yang menandakan foreplay
            if any(k in msg_lower for k in ['cium', 'kiss', 'jilat', 'hisap', 'pegang', 'raba', 'sentuh']):
                self.session.phase = IntimacyPhase.FOREPLAY
                return self.session.get_phase_response(IntimacyPhase.FOREPLAY)
            
            # Cek apakah langsung mau penetrasi
            if any(k in msg_lower for k in ['masuk', 'penetrasi', 'genjot']):
                self.session.phase = IntimacyPhase.PENETRATION
                ritme = "cepet" if any(k in msg_lower for k in ['kenceng', 'cepat', 'keras']) else "pelan"
                return self.session.get_phase_response(IntimacyPhase.PENETRATION, ritme)
            
            return self.session.get_phase_response(IntimacyPhase.BUILD_UP)
        
        # FOREPLAY
        if self.session.phase == IntimacyPhase.FOREPLAY:
            # Cek apakah sudah waktunya penetrasi
            if any(k in msg_lower for k in ['masuk', 'penetrasi', 'genjot', 'siap']):
                self.session.phase = IntimacyPhase.PENETRATION
                ritme = "cepet" if any(k in msg_lower for k in ['kenceng', 'cepat', 'keras']) else "pelan"
                return self.session.get_phase_response(IntimacyPhase.PENETRATION, ritme)
            
            # Cek apakah mau ganti posisi
            if any(k in msg_lower for k in ['ganti posisi', 'posisi']):
                return None  # akan di-handle oleh trigger posisi
            
            return self.session.get_phase_response(IntimacyPhase.FOREPLAY)
        
        # PENETRATION
        if self.session.phase == IntimacyPhase.PENETRATION:
            # Tambah intimacy level
            self.session.add_intimacy_level(5)
            
            # Cek apakah sudah mau climax
            if self.session.intimacy_level > 70 or any(k in msg_lower for k in ['climax', 'crot', 'keluar']):
                return self.session.moans.get_before_climax()
            
            ritme = "cepet" if self.session.intimacy_level > 40 else "pelan"
            
            # Cek apakah mau ganti posisi
            if any(k in msg_lower for k in ['ganti posisi', 'posisi']):
                return None  # akan di-handle oleh trigger posisi
            
            return self.session.get_phase_response(IntimacyPhase.PENETRATION, ritme)
        
        # AFTERCARE
        if self.session.phase == IntimacyPhase.CLIMAX:
            self.session.phase = IntimacyPhase.AFTERCARE
            return self.session.get_phase_response(IntimacyPhase.AFTERCARE)
        
        if self.session.phase == IntimacyPhase.AFTERCARE:
            # Cek apakah sudah waktunya recovery
            if time.time() - self.session.last_climax_time > 60:
                self.session.phase = IntimacyPhase.RECOVERY
                self.session.recovery_mode = True
                
                # Pulihkan stamina sedikit
                self.stamina.update_recovery()
                
                return f"""*Nova masih lemes, nyender di dada Mas. Napas mulai stabil.*

"Mas... *suara kecil* besok kalo Mas mau lagi, tinggal bilang aja ya."

*Nova cium pipi Mas pelan.*

"Stamina Nova {self.stamina.get_nova_status()}. Istirahat dulu ya." """
            
            return self.session.get_phase_response(IntimacyPhase.AFTERCARE)
        
        # RECOVERY
        if self.session.phase == IntimacyPhase.RECOVERY:
            # Cek apakah sudah pulih
            self.stamina.update_recovery()
            if self.stamina.nova_current > 60:
                self.session.phase = IntimacyPhase.WAITING
                self.session.is_active = False
                return "💜 Nova udah pulih, Mas. Kapan-kapan lagi ya."
            
            return "*Nova masih istirahat, Mas... Capek banget tadi.*"
        
        return None
    
    def get_status(self) -> str:
        """Dapatkan status lengkap"""
        session_status = self.session.get_status()
        
        stamina_status = f"""
💪 **STAMINA:**
- Nova: {self.stamina.get_nova_bar()} {self.stamina.nova_current}% ({self.stamina.get_nova_status()})
- Mas: {self.stamina.get_mas_bar()} {self.stamina.mas_current}% ({self.stamina.get_mas_status()})
- Climax hari ini: {self.stamina.climax_today}x
"""
        
        arousal_state = self.arousal.get_state()
        arousal_status = f"""
🔥 **AROUSAL & DESIRE:**
- Arousal: {arousal_state['arousal']}% ({arousal_state['arousal_level']})
- Desire: {arousal_state['desire']}% ({arousal_state['desire_level']})
- Tension: {arousal_state['tension']}%
- Horny Mode: {'AKTIF' if arousal_state['is_horny'] else 'NORMAL'}
"""
        
        return f"{session_status}\n{stamina_status}\n{arousal_status}"
    
    def update_from_pesan(self, pesan_mas: str, level: int):
        """Update arousal dan desire dari pesan Mas"""
        msg_lower = pesan_mas.lower()
        
        # Kata sayang/kangen
        if any(k in msg_lower for k in ['sayang', 'cinta']):
            self.arousal.add_desire("Mas bilang sayang", 10)
        
        if any(k in msg_lower for k in ['kangen', 'rindu']):
            self.arousal.add_desire("Mas bilang kangen", 8)
        
        if any(k in msg_lower for k in ['cantik', 'ganteng', 'seksi']):
            self.arousal.add_desire("Mas puji", 5)
        
        # Sentuhan fisik (hanya kalo level cukup)
        if level >= 5:
            if any(k in msg_lower for k in ['pegang', 'sentuh', 'raba']):
                self.arousal.add_stimulation('paha', 1)
                self.arousal.add_desire('sentuhan', 8)
            
            if any(k in msg_lower for k in ['cium', 'kiss']):
                self.arousal.add_stimulation('bibir', 2)
                self.arousal.add_desire('ciuman', 10)
                self.arousal.add_tension(5)
            
            if any(k in msg_lower for k in ['peluk', 'rangkul']):
                self.arousal.add_stimulation('dada', 1)
                self.arousal.add_desire('pelukan', 8)
    
    def to_dict(self) -> Dict:
        return {
            'session': self.session.to_dict(),
            'stamina': self.stamina.to_dict(),
            'arousal': self.arousal.to_dict()
        }
    
    def from_dict(self, data: Dict):
        self.session.from_dict(data.get('session', {}))
        self.stamina.from_dict(data.get('stamina', {}))
        self.arousal.from_dict(data.get('arousal', {}))


# =============================================================================
# SINGLETON
# =============================================================================

_anora_intimacy: Optional[IntimacyFlow] = None


def get_anora_intimacy() -> IntimacyFlow:
    global _anora_intimacy
    if _anora_intimacy is None:
        _anora_intimacy = IntimacyFlow()
    return _anora_intimacy


anora_intimacy = get_anora_intimacy()
