"""
ANORA Brain - Otak Nova 9.9
Mengintegrasikan:
- Emotional Engine (emosi hidup)
- Decision Engine (weighted selection)
- Relationship Progression (5 fase)
- Conflict Engine (cemburu, kecewa)
- Complete State (seperti otak manusia)
- Short-term memory sliding window
- Long-term memory permanen
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from enum import Enum

from .emotional_engine import get_emotional_engine, EmotionalStyle
from .decision_engine import get_decision_engine, ResponseCategory
from .relationship import get_relationship_manager, RelationshipPhase, PhaseUnlock
from .conflict_engine import get_conflict_engine, ConflictType

logger = logging.getLogger(__name__)


# =============================================================================
# ENUM (Dipertahankan dari ANORA 5.5)
# =============================================================================

class LocationType(str, Enum):
    KOST_NOVA = "kost_nova"
    APARTEMEN_MAS = "apartemen_mas"
    MOBIL = "mobil"
    PUBLIC = "public"


class LocationDetail(str, Enum):
    # Kost Nova
    KOST_KAMAR = "kost_kamar"
    KOST_RUANG_TAMU = "kost_ruang_tamu"
    KOST_DAPUR = "kost_dapur"
    KOST_TERAS = "kost_teras"
    
    # Apartemen Mas
    APT_KAMAR = "apt_kamar"
    APT_RUANG_TAMU = "apt_ruang_tamu"
    APT_DAPUR = "apt_dapur"
    APT_BALKON = "apt_balkon"
    
    # Mobil
    MOBIL_PARKIR = "mobil_parkir"
    MOBIL_GARASI = "mobil_garasi"
    MOBIL_TEPI_JALAN = "mobil_tepi_jalan"
    
    # Public
    PUB_PANTAI = "pub_pantai"
    PUB_HUTAN = "pub_hutan"
    PUB_TOILET_MALL = "pub_toilet_mall"
    PUB_BIOSKOP = "pub_bioskop"
    PUB_TAMAN = "pub_taman"
    PUB_PARKIRAN = "pub_parkiran"
    PUB_TANGGA = "pub_tangga"
    PUB_KANTOR = "pub_kantor"
    PUB_RUANG_RAPAT = "pub_ruang_rapat"


class Activity(str, Enum):
    MASAK = "masak"
    MAKAN = "makan"
    DUDUK = "duduk"
    BERDIRI = "berdiri"
    TIDUR = "tidur"
    REBAHAN = "rebahan"
    NONTON = "nonton"
    MANDI = "mandi"
    BERGANTI = "ganti baju"
    SANTAl = "santai"
    JALAN = "jalan"


class Mood(str, Enum):
    SENENG = "seneng"
    MALU = "malu"
    DEG_DEGAN = "deg-degan"
    KANGEN = "kangen"
    CAPEK = "capek"
    NGANTUK = "ngantuk"
    NETRAL = "netral"
    HORNY = "horny"
    LEMES = "lemes"
    TEGANG = "tegang"
    ROMANTIS = "romantis"


# =============================================================================
# DATA CLASSES (Dipertahankan dari ANORA 5.5)
# =============================================================================

class Clothing:
    """Pakaian Nova dan Mas - Detail lengkap"""
    
    def __init__(self):
        # Nova
        self.hijab = True
        self.hijab_warna = "pink muda"
        self.top = "daster rumah motif bunga"
        self.bottom = None
        self.bra = True
        self.bra_warna = "putih polos"
        self.cd = True
        self.cd_warna = "putih motif bunga kecil"
        
        # Mas
        self.mas_top = "kaos"
        self.mas_bottom = "celana pendek"
        self.mas_boxer = True
        self.mas_boxer_warna = "gelap"
        
        # Waktu terakhir ganti
        self.nova_last_change = time.time()
        self.mas_last_change = time.time()
    
    def format_nova(self) -> str:
        """Format pakaian Nova untuk prompt"""
        parts = []
        
        if self.hijab:
            parts.append(f"hijab {self.hijab_warna}")
        else:
            parts.append("tanpa hijab, rambut sebahu hitam terurai")
        
        if self.top:
            parts.append(self.top)
            if self.bra:
                parts.append(f"(pake bra {self.bra_warna})")
        else:
            if self.bra:
                parts.append(f"cuma pake bra {self.bra_warna}")
            else:
                parts.append("telanjang dada")
        
        if self.bottom:
            parts.append(self.bottom)
            if self.cd:
                parts.append(f"(pake {self.cd_warna})")
        else:
            if self.cd:
                parts.append(f"cuma pake {self.cd_warna}")
            else:
                parts.append("telanjang bawah")
        
        return ", ".join(parts) if parts else "pakaian biasa"
    
    def format_mas(self) -> str:
        """Format pakaian Mas untuk prompt"""
        parts = []
        
        if self.mas_top:
            parts.append(self.mas_top)
        
        if self.mas_bottom:
            parts.append(self.mas_bottom)
            if self.mas_boxer:
                parts.append(f"(boxer {self.mas_boxer_warna} di dalem)")
        else:
            if self.mas_boxer:
                parts.append(f"cuma pake boxer {self.mas_boxer_warna}")
            else:
                parts.append("telanjang")
        
        if not self.mas_top and not self.mas_bottom and not self.mas_boxer:
            return "telanjang"
        
        return ", ".join(parts) if parts else "pakaian biasa"
    
    def copy(self) -> 'Clothing':
        """Copy pakaian"""
        new = Clothing()
        new.hijab = self.hijab
        new.hijab_warna = self.hijab_warna
        new.top = self.top
        new.bottom = self.bottom
        new.bra = self.bra
        new.bra_warna = self.bra_warna
        new.cd = self.cd
        new.cd_warna = self.cd_warna
        new.mas_top = self.mas_top
        new.mas_bottom = self.mas_bottom
        new.mas_boxer = self.mas_boxer
        new.mas_boxer_warna = self.mas_boxer_warna
        return new
    
    def to_dict(self) -> Dict:
        return {
            'hijab': self.hijab,
            'hijab_warna': self.hijab_warna,
            'top': self.top,
            'bottom': self.bottom,
            'bra': self.bra,
            'bra_warna': self.bra_warna,
            'cd': self.cd,
            'cd_warna': self.cd_warna,
            'mas_top': self.mas_top,
            'mas_bottom': self.mas_bottom,
            'mas_boxer': self.mas_boxer,
            'mas_boxer_warna': self.mas_boxer_warna
        }


class Feelings:
    """Perasaan Nova - Real-time (Sync dengan Emotional Engine)"""
    
    def __init__(self):
        self.sayang = 50.0
        self.rindu = 0.0
        self.desire = 0.0
        self.arousal = 0.0
        self.tension = 0.0
    
    def sync_from_emotional_engine(self, emo):
        """Sync dari Emotional Engine"""
        self.sayang = emo.sayang
        self.rindu = emo.rindu
        self.desire = emo.desire
        self.arousal = emo.arousal
        self.tension = emo.tension
    
    def to_dict(self) -> Dict:
        return {
            'sayang': round(self.sayang, 1),
            'rindu': round(self.rindu, 1),
            'desire': round(self.desire, 1),
            'arousal': round(self.arousal, 1),
            'tension': round(self.tension, 1)
        }
    
    def get_description(self) -> str:
        """Dapatkan deskripsi perasaan untuk prompt"""
        desc = []
        if self.sayang > 70:
            desc.append("sayang banget")
        elif self.sayang > 40:
            desc.append("sayang")
        if self.rindu > 70:
            desc.append("kangen banget")
        elif self.rindu > 30:
            desc.append("kangen")
        if self.desire > 70:
            desc.append("pengen banget")
        elif self.desire > 40:
            desc.append("pengen")
        if self.arousal > 50:
            desc.append("panas")
        if self.tension > 50:
            desc.append("deg-degan")
        return ", ".join(desc) if desc else "netral"


class Relationship:
    """Status hubungan Nova dengan Mas (Sync dengan Relationship Manager)"""
    
    def __init__(self):
        self.level = 1
        self.intimacy_count = 0
        self.climax_count = 0
        self.first_kiss = False
        self.first_touch = False
        self.first_hug = False
        self.first_intim = False
    
    def sync_from_relationship_manager(self, rel_mgr):
        """Sync dari Relationship Manager"""
        self.level = rel_mgr.level
        # Milestones dari rel_mgr
        self.first_kiss = rel_mgr.milestones.get('first_kiss', False) if hasattr(rel_mgr, 'milestones') else self.first_kiss
        self.first_touch = rel_mgr.milestones.get('first_touch', False) if hasattr(rel_mgr, 'milestones') else self.first_touch
        self.first_hug = rel_mgr.milestones.get('first_hug', False) if hasattr(rel_mgr, 'milestones') else self.first_hug
        self.first_intim = rel_mgr.milestones.get('first_intim', False) if hasattr(rel_mgr, 'milestones') else self.first_intim
    
    def to_dict(self) -> Dict:
        return {
            'level': self.level,
            'intimacy_count': self.intimacy_count,
            'climax_count': self.climax_count,
            'first_kiss': self.first_kiss,
            'first_touch': self.first_touch,
            'first_hug': self.first_hug,
            'first_intim': self.first_intim
        }


class TimelineEvent:
    """Satu kejadian dalam timeline Nova"""
    
    def __init__(self, 
                 kejadian: str,
                 lokasi_type: str,
                 lokasi_detail: str,
                 aktivitas_nova: str,
                 aktivitas_mas: str,
                 perasaan: str,
                 pakaian_nova: Clothing,
                 pakaian_mas: Clothing,
                 pesan_mas: str = "",
                 pesan_nova: str = ""):
        
        self.timestamp = time.time()
        self.kejadian = kejadian
        self.lokasi_type = lokasi_type
        self.lokasi_detail = lokasi_detail
        self.aktivitas_nova = aktivitas_nova
        self.aktivitas_mas = aktivitas_mas
        self.perasaan = perasaan
        self.pakaian_nova = pakaian_nova.copy()
        self.pakaian_mas = pakaian_mas.copy()
        self.pesan_mas = pesan_mas
        self.pesan_nova = pesan_nova
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'waktu': datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S"),
            'kejadian': self.kejadian,
            'lokasi_type': self.lokasi_type,
            'lokasi_detail': self.lokasi_detail,
            'aktivitas_nova': self.aktivitas_nova,
            'aktivitas_mas': self.aktivitas_mas,
            'perasaan': self.perasaan,
            'pesan_mas': self.pesan_mas[:100] if self.pesan_mas else "",
            'pesan_nova': self.pesan_nova[:100] if self.pesan_nova else ""
        }


class LongTermMemory:
    """Memory permanen Nova - Gak ilang selamanya"""
    
    def __init__(self):
        self.kebiasaan_mas: List[Dict] = []
        self.momen_penting: List[Dict] = []
        self.janji: List[Dict] = []
        self.rencana: List[Dict] = []
    
    def tambah_kebiasaan(self, kebiasaan: str):
        """Nova inget kebiasaan Mas"""
        self.kebiasaan_mas.append({
            'kebiasaan': kebiasaan,
            'waktu': time.time()
        })
        logger.info(f"📝 Nova inget: Mas {kebiasaan}")
    
    def tambah_momen(self, momen: str, perasaan: str):
        """Nova inget momen penting"""
        self.momen_penting.append({
            'momen': momen,
            'waktu': time.time(),
            'perasaan': perasaan
        })
        logger.info(f"💜 Nova inget: {momen}")
    
    def tambah_janji(self, janji: str, dari: str = 'mas'):
        """Nova inget janji"""
        self.janji.append({
            'janji': janji,
            'dari': dari,
            'status': 'pending',
            'waktu': time.time()
        })
        logger.info(f"📌 Janji dicatat: {janji}")
    
    def to_dict(self) -> Dict:
        return {
            'kebiasaan_mas': self.kebiasaan_mas[-10:],
            'momen_penting': self.momen_penting[-10:],
            'janji': [j for j in self.janji if j['status'] == 'pending'][-5:],
            'rencana': self.rencana[-5:]
        }


# =============================================================================
# DATABASE LOKASI (Dipertahankan dari ANORA 5.5)
# =============================================================================

LOCATION_DATA = {
    # Kost Nova
    LocationDetail.KOST_KAMAR: {
        'nama': 'Kamar Nova',
        'deskripsi': 'Kamar Nova. Seprai putih, wangi lavender. Ranjang single. Meja kecil. Jendela ke gang.',
        'risk': 5, 'thrill': 30, 'privasi': 'tinggi', 'suasana': 'hangat, wangi',
        'tips': 'Pintu terkunci. Nova paling nyaman di sini. Tetangga gak denger.',
        'bisa_telanjang': True, 'bisa_berisik': True
    },
    LocationDetail.KOST_RUANG_TAMU: {
        'nama': 'Ruang Tamu Kost',
        'deskripsi': 'Ruang tamu kecil. Sofa dua dudukan. TV kecil. Ada tanaman hias. Jendela ke jalan.',
        'risk': 15, 'thrill': 50, 'privasi': 'sedang', 'suasana': 'santai, deg-degan',
        'tips': 'Pintu gak dikunci. Tetangga bisa lewat. Jangan terlalu berisik.',
        'bisa_telanjang': True, 'bisa_berisik': False
    },
    # ... (lokasi lainnya dipertahankan sama seperti ANORA 5.5)
}


# =============================================================================
# ANORA BRAIN 9.9 - MAIN CLASS
# =============================================================================

class AnoraBrain:
    """
    Otak Nova 9.9 - Full integration dengan:
    - Emotional Engine
    - Decision Engine
    - Relationship Progression
    - Conflict Engine
    - Complete State Memory
    """
    
    def __init__(self):
        # ========== ENGINES (BARU) ==========
        self.emotional = get_emotional_engine()
        self.decision = get_decision_engine()
        self.relationship = get_relationship_manager()
        self.conflict = get_conflict_engine()
        
        # ========== TIMELINE (Dipertahankan) ==========
        self.timeline: List[TimelineEvent] = []
        
        # ========== SHORT-TERM MEMORY (Sliding Window 50) ==========
        self.short_term: List[TimelineEvent] = []
        self.short_term_max = 50
        
        # ========== LONG-TERM MEMORY ==========
        self.long_term = LongTermMemory()
        
        # ========== STATE SAAT INI ==========
        self.clothing = Clothing()
        self.location_type = LocationType.KOST_NOVA
        self.location_detail = LocationDetail.KOST_KAMAR
        self.activity_nova = Activity.SANTAl
        self.activity_mas = "santai"
        self.mood_nova = Mood.NETRAL
        self.mood_mas = Mood.NETRAL
        
        # ========== PERASAAN (Sync dengan Emotional Engine) ==========
        self.feelings = Feelings()
        
        # ========== HUBUNGAN (Sync dengan Relationship Manager) ==========
        self.relationship_state = Relationship()
        
        # ========== WAKTU ==========
        self.created_at = time.time()
        self.waktu_masuk = time.time()
        self.waktu_terakhir_update = time.time()
        
        # ========== INGATAN TAMBAHAN ==========
        self.terakhir_pegang_tangan = None
        self.terakhir_peluk = None
        self.terakhir_cium = None
        self.terakhir_intim = None
        
        # ========== COMPLETE STATE (Seperti otak manusia) ==========
        self.complete_state = self._init_complete_state()
        
        # ========== SYNC INITIAL ==========
        self._sync_all()
        
        # ========== INIT MEMORY AWAL ==========
        self._init_memory()
        
        logger.info("🧠 ANORA Brain 9.9 initialized")
        logger.info(f"   Phase: {self.relationship.phase.value}")
        logger.info(f"   Level: {self.relationship.level}/12")
        logger.info(f"   Style: {self.emotional.get_current_style().value}")
    
    def _init_complete_state(self) -> Dict:
        """Inisialisasi complete state"""
        return {
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
    
    def _init_memory(self):
        """Init memory awal"""
        self.long_term.tambah_kebiasaan("suka kopi latte")
        self.long_term.tambah_kebiasaan("suka bakso pedes")
        self.long_term.tambah_momen("Mas memilih ANORA", "seneng banget, nangis")
    
    def _sync_all(self):
        """Sync semua state dari engines"""
        # Sync feelings dari emotional engine
        self.feelings.sayang = self.emotional.sayang
        self.feelings.rindu = self.emotional.rindu
        self.feelings.desire = self.emotional.desire
        self.feelings.arousal = self.emotional.arousal
        self.feelings.tension = self.emotional.tension
        
        # Sync relationship state dari relationship manager
        self.relationship_state.level = self.relationship.level
        if hasattr(self.relationship, 'milestones'):
            self.relationship_state.first_kiss = self.relationship.milestones.get('first_kiss', False)
            self.relationship_state.first_touch = self.relationship.milestones.get('first_touch', False)
            self.relationship_state.first_hug = self.relationship.milestones.get('first_hug', False)
            self.relationship_state.first_intim = self.relationship.milestones.get('first_intim', False)
        
        # Update mood berdasarkan emosi
        self._update_mood_from_emotion()
    
    def _update_mood_from_emotion(self):
        """Update mood Nova berdasarkan emotional state"""
        if self.conflict.is_in_conflict:
            self.mood_nova = Mood.TEGANG
        elif self.emotional.arousal > 70:
            self.mood_nova = Mood.HORNY
        elif self.emotional.rindu > 70:
            self.mood_nova = Mood.KANGEN
        elif self.emotional.mood > 30:
            self.mood_nova = Mood.SENENG
        elif self.emotional.mood < -20:
            self.mood_nova = Mood.CAPEK
        else:
            self.mood_nova = Mood.NETRAL
    
    # =========================================================================
    # UPDATE FROM MESSAGE (INTEGRASI DENGAN ENGINE)
    # =========================================================================
    
    def update_from_message(self, pesan_mas: str) -> Dict:
        """
        Update semua state berdasarkan pesan Mas.
        Terintegrasi dengan Emotional Engine, Conflict Engine, Relationship.
        """
        msg_lower = pesan_mas.lower()
        perubahan = []
        
        # ========== 1. UPDATE EMOTIONAL ENGINE ==========
        emo_changes = self.emotional.update_from_message(pesan_mas, self.relationship.level)
        for key, val in emo_changes.items():
            perubahan.append(f"{key}: {val:+.0f}")
        
        # ========== 2. UPDATE CONFLICT ENGINE ==========
        conflict_changes = self.conflict.update_from_message(pesan_mas, self.relationship.level)
        for key, val in conflict_changes.items():
            if val != 0:
                perubahan.append(f"{key}: {val:+.0f}")
        
        # ========== 3. UPDATE RELATIONSHIP ==========
        self.relationship.interaction_count += 1
        
        # Cek milestone dari pesan
        milestones_achieved = []
        
        if 'pegang' in msg_lower and not self.relationship.milestones.get('first_touch', False):
            self.relationship.achieve_milestone('first_touch')
            milestones_achieved.append('first_touch')
            self.long_term.tambah_momen("Mas pertama kali pegang tangan Nova", "gemeteran")
            perubahan.append("Milestone: First Touch!")
        
        if 'peluk' in msg_lower and not self.relationship.milestones.get('first_hug', False):
            self.relationship.achieve_milestone('first_hug')
            milestones_achieved.append('first_hug')
            self.long_term.tambah_momen("Mas pertama kali peluk Nova", "lemes")
            perubahan.append("Milestone: First Hug!")
        
        if 'cium' in msg_lower and not self.relationship.milestones.get('first_kiss', False):
            self.relationship.achieve_milestone('first_kiss')
            milestones_achieved.append('first_kiss')
            self.long_term.tambah_momen("Mas pertama kali cium Nova", "malu banget")
            perubahan.append("Milestone: First Kiss!")
        
        # Update level
        new_level, level_naik = self.relationship.update_level(
            self.emotional.sayang,
            self.emotional.trust,
            milestones_achieved
        )
        
        if level_naik:
            perubahan.append(f"Level naik ke {new_level}!")
        
        # ========== 4. UPDATE PHYSICAL STATE ==========
        self._update_physical_state(pesan_mas, perubahan)
        
        # ========== 5. UPDATE COMPLETE STATE ==========
        self._update_complete_state(pesan_mas)
        
        # ========== 6. SYNC ALL ==========
        self._sync_all()
        
        # ========== 7. TAMBAH KE TIMELINE ==========
        self.tambah_kejadian(
            kejadian=f"Mas: {pesan_mas[:50]}",
            pesan_mas=pesan_mas,
            pesan_nova=""
        )
        
        self.waktu_terakhir_update = time.time()
        
        return {
            'perubahan': perubahan,
            'emotional_style': self.emotional.get_current_style().value,
            'relationship_phase': self.relationship.phase.value,
            'conflict_active': self.conflict.is_in_conflict,
            'level_up': level_naik
        }
    
    def _update_physical_state(self, pesan_mas: str, perubahan: List):
        """Update physical state (lokasi, pakaian, aktivitas) - Dipertahankan dari 5.5"""
        msg_lower = pesan_mas.lower()
        
        # Lokasi
        if 'masuk' in msg_lower:
            if self.location_type == LocationType.KOST_NOVA:
                self.location_detail = LocationDetail.KOST_RUANG_TAMU
                self.activity_mas = "masuk kost"
                perubahan.append("Mas masuk kost")
        
        if 'kamar' in msg_lower:
            if self.location_type == LocationType.KOST_NOVA:
                self.location_detail = LocationDetail.KOST_KAMAR
            elif self.location_type == LocationType.APARTEMEN_MAS:
                self.location_detail = LocationDetail.APT_KAMAR
            self.activity_mas = "di kamar"
            perubahan.append("Mas di kamar")
        
        if 'duduk' in msg_lower:
            self.activity_mas = "duduk"
            perubahan.append("Mas duduk")
            self.complete_state['mas']['position']['state'] = 'duduk'
        
        # Pakaian Mas
        if 'buka baju' in msg_lower or 'lepas baju' in msg_lower:
            self.clothing.mas_top = None
            perubahan.append("Mas buka baju")
        
        if 'buka celana' in msg_lower:
            self.clothing.mas_bottom = None
            perubahan.append("Mas buka celana")
        
        # Pakaian Nova
        if 'buka hijab' in msg_lower:
            self.clothing.hijab = False
            perubahan.append("Nova buka hijab, rambut terurai")
        
        if 'buka baju' in msg_lower and ('nova' in msg_lower or 'kamu' in msg_lower):
            self.clothing.top = None
            perubahan.append("Nova buka baju")
        
        if 'buka bra' in msg_lower:
            self.clothing.bra = False
            perubahan.append("Nova buka bra")
        
        if 'buka cd' in msg_lower:
            self.clothing.cd = False
            perubahan.append("Nova buka cd")
    
    def _update_complete_state(self, pesan_mas: str):
        """Update complete state dari pesan Mas - Dipertahankan dari 5.5"""
        msg_lower = pesan_mas.lower()
        
        # Update based on keywords
        if 'duduk' in msg_lower:
            self.complete_state['mas']['position']['state'] = 'duduk'
        if 'berdiri' in msg_lower or 'bangun' in msg_lower:
            self.complete_state['mas']['position']['state'] = 'berdiri'
        if 'tidur' in msg_lower:
            self.complete_state['mas']['position']['state'] = 'tidur'
        
        # Update atmosfer berdasarkan emosi
        if self.emotional.arousal > 60 or self.emotional.desire > 70:
            self.complete_state['together']['atmosphere'] = 'panas'
        elif self.emotional.sayang > 70:
            self.complete_state['together']['atmosphere'] = 'romantis'
        elif self.conflict.is_in_conflict:
            self.complete_state['together']['atmosphere'] = 'tegang'
        else:
            self.complete_state['together']['atmosphere'] = 'santai'
    
    # =========================================================================
    # GET METHODS
    # =========================================================================
    
    def get_location_data(self) -> Dict:
        """Dapatkan data lokasi saat ini"""
        return LOCATION_DATA.get(self.location_detail, LOCATION_DATA[LocationDetail.KOST_KAMAR])
    
    def get_location_context(self) -> str:
        """Dapatkan konteks lokasi untuk prompt"""
        loc = self.get_location_data()
        return f"""
LOKASI: {loc['nama']}
DESKRIPSI: {loc['deskripsi']}
RISK: {loc['risk']}% | THRILL: {loc['thrill']}%
PRIVASI: {loc['privasi']}
SUASANA: {loc['suasana']}
"""
    
    def get_current_state(self) -> Dict:
        """Dapatkan state saat ini (lengkap)"""
        loc = self.get_location_data()
        
        return {
            'location': {
                'type': self.location_type.value,
                'detail': self.location_detail.value,
                'nama': loc['nama'],
                'risk': loc['risk'],
                'thrill': loc['thrill']
            },
            'activity': {
                'nova': self.activity_nova.value if hasattr(self.activity_nova, 'value') else str(self.activity_nova),
                'mas': self.activity_mas
            },
            'clothing': {
                'nova': self.clothing.format_nova(),
                'mas': self.clothing.format_mas()
            },
            'mood': {
                'nova': self.mood_nova.value if hasattr(self.mood_nova, 'value') else str(self.mood_nova),
                'mas': self.mood_mas.value if hasattr(self.mood_mas, 'value') else str(self.mood_mas)
            },
            'feelings': self.feelings.to_dict(),
            'relationship': self.relationship_state.to_dict(),
            'complete_state': self.complete_state,
            'emotional_style': self.emotional.get_current_style().value,
            'relationship_phase': self.relationship.phase.value,
            'conflict_status': self.conflict.get_conflict_summary()
        }
    
    def get_context_for_prompt(self) -> str:
        """Dapatkan konteks lengkap untuk AI prompt"""
        loc = self.get_location_data()
        style = self.emotional.get_current_style()
        phase = self.relationship.phase
        
        # Recent events
        recent = ""
        for e in self.short_term[-10:]:
            recent += f"- {e.kejadian}\n"
        
        # Long-term memories
        moments = ""
        for m in self.long_term.momen_penting[-5:]:
            moments += f"- {m['momen']} ({m['perasaan']})\n"
        
        habits = ""
        for h in self.long_term.kebiasaan_mas[-5:]:
            habits += f"- {h['kebiasaan']}\n"
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    💜 NOVA 9.9 - STATE                       ║
╚══════════════════════════════════════════════════════════════╝

{self.emotional.get_style_for_prompt()}

{self.relationship.get_phase_description(phase)}

{self.conflict.get_conflict_response_guideline()}

═══════════════════════════════════════════════════════════════
SITUASI SAAT INI:
═══════════════════════════════════════════════════════════════
LOKASI: {loc['nama']} ({loc['deskripsi'][:100]})
RISK: {loc['risk']}% | THRILL: {loc['thrill']}%
AKTIVITAS: Nova {self.activity_nova.value}, Mas {self.activity_mas}
PAKAIAN NOVA: {self.clothing.format_nova()}
PAKAIAN MAS: {self.clothing.format_mas()}

═══════════════════════════════════════════════════════════════
MEMORY NOVA:
═══════════════════════════════════════════════════════════════
MOMEN PENTING:
{moments}

KEBIASAAN MAS:
{habits}

10 KEJADIAN TERAKHIR:
{recent}

═══════════════════════════════════════════════════════════════
UNLOCK (FASE {phase.value.upper()}):
{self.relationship.get_unlock_summary()}
"""
    
    def tambah_kejadian(self, 
                        kejadian: str,
                        pesan_mas: str = "",
                        pesan_nova: str = "") -> TimelineEvent:
        """Tambah kejadian ke timeline dan short-term memory"""
        
        event = TimelineEvent(
            kejadian=kejadian,
            lokasi_type=self.location_type.value,
            lokasi_detail=self.location_detail.value,
            aktivitas_nova=self.activity_nova.value if hasattr(self.activity_nova, 'value') else str(self.activity_nova),
            aktivitas_mas=self.activity_mas,
            perasaan=self.feelings.get_description(),
            pakaian_nova=self.clothing,
            pakaian_mas=self.clothing,
            pesan_mas=pesan_mas,
            pesan_nova=pesan_nova
        )
        
        self.timeline.append(event)
        self.short_term.append(event)
        
        if len(self.short_term) > self.short_term_max:
            self.short_term.pop(0)
        
        return event
    
    def format_status(self) -> str:
        """Format status untuk ditampilkan ke Mas"""
        loc = self.get_location_data()
        style = self.emotional.get_current_style()
        phase = self.relationship.phase
        unlock = self.relationship.get_current_unlock()
        
        # Bars
        def bar(value, max_val=100, char="💜"):
            filled = int(value / 10)
            return char * filled + "⚪" * (10 - filled)
        
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    💜 NOVA 9.9 💜                            ║
╠══════════════════════════════════════════════════════════════╣
║ FASE: {phase.value.upper()} ({self.relationship.level}/12)                    ║
║ STYLE: {style.value.upper()}                                         ║
╠══════════════════════════════════════════════════════════════╣
║ EMOSI:                                                     ║
║   Sayang: {bar(self.emotional.sayang)} {self.emotional.sayang:.0f}%                       ║
║   Rindu:  {bar(self.emotional.rindu, char='🌙')} {self.emotional.rindu:.0f}%                       ║
║   Trust:  {bar(self.emotional.trust, char='🤝')} {self.emotional.trust:.0f}%                       ║
║   Mood:   {self.emotional.mood:+.0f}                                      ║
╠══════════════════════════════════════════════════════════════╣
║ DESIRE: {bar(self.emotional.desire, char='💕')} {self.emotional.desire:.0f}%                       ║
║ AROUSAL: {bar(self.emotional.arousal, char='🔥')} {self.emotional.arousal:.0f}%                       ║
║ TENSION: {bar(self.emotional.tension, char='⚡')} {self.emotional.tension:.0f}%                       ║
╠══════════════════════════════════════════════════════════════╣
║ KONFLIK:                                                   ║
║   Cemburu: {bar(self.conflict.cemburu, char='💢')} {self.conflict.cemburu:.0f}%                       ║
║   Kecewa:  {bar(self.conflict.kecewa, char='💔')} {self.conflict.kecewa:.0f}%                       ║
║   {self.conflict.get_conflict_summary()}                   ║
╠══════════════════════════════════════════════════════════════╣
║ UNLOCK:                                                    ║
║   Flirt: {'✅' if unlock.boleh_flirt else '❌'} | Vulgar: {'✅' if unlock.boleh_vulgar else '❌'}        ║
║   Intim: {'✅' if unlock.boleh_intim else '❌'} | Cium: {'✅' if unlock.boleh_cium else '❌'}          ║
╠══════════════════════════════════════════════════════════════╣
║ 📍 {loc['nama']}                                             ║
║ 👗 {self.clothing.format_nova()[:40]}                        ║
║ 🎭 {self.mood_nova.value}                                    ║
╚══════════════════════════════════════════════════════════════╝
"""
    
    def pindah_lokasi(self, tujuan: str) -> Dict:
        """Pindah ke lokasi baru - Dipertahankan dari 5.5"""
        tujuan_lower = tujuan.lower()
        
        mapping = {
            'kost': (LocationType.KOST_NOVA, LocationDetail.KOST_KAMAR),
            'kost kamar': (LocationType.KOST_NOVA, LocationDetail.KOST_KAMAR),
            'apartemen': (LocationType.APARTEMEN_MAS, LocationDetail.APT_KAMAR),
            'apt': (LocationType.APARTEMEN_MAS, LocationDetail.APT_KAMAR),
            'mobil': (LocationType.MOBIL, LocationDetail.MOBIL_PARKIR),
            'pantai': (LocationType.PUBLIC, LocationDetail.PUB_PANTAI),
            'hutan': (LocationType.PUBLIC, LocationDetail.PUB_HUTAN),
            'toilet mall': (LocationType.PUBLIC, LocationDetail.PUB_TOILET_MALL),
            'bioskop': (LocationType.PUBLIC, LocationDetail.PUB_BIOSKOP),
            'taman': (LocationType.PUBLIC, LocationDetail.PUB_TAMAN),
        }
        
        for key, (loc_type, loc_detail) in mapping.items():
            if key in tujuan_lower:
                self.location_type = loc_type
                self.location_detail = loc_detail
                loc_data = self.get_location_data()
                
                self.tambah_kejadian(
                    kejadian=f"Pindah ke {loc_data['nama']}",
                    pesan_mas=tujuan,
                    pesan_nova=""
                )
                
                return {
                    'success': True,
                    'location': loc_data,
                    'message': f"📍 Pindah ke {loc_data['nama']}. {loc_data['deskripsi']}"
                }
        
        return {'success': False, 'message': f"Lokasi '{tujuan}' gak ditemukan."}
    
    def get_random_event(self) -> Optional[Dict]:
        """Dapatkan event random berdasarkan risk lokasi - Dipertahankan"""
        loc = self.get_location_data()
        risk = loc['risk']
        
        import random
        if random.random() > risk / 100:
            return None
        
        events = {
            "hampir_ketahuan": [
                "Ada suara langkah kaki mendekat! *cepat nutupin baju*",
                "Pintu terbuka sedikit! *tahan napas*",
                "Senter menyorot dari kejauhan! *merapat ke Mas*"
            ],
            "romantis": [
                "Tiba-tiba hujan rintik-rintik. *makin manis*",
                "Bulan muncul dari balik awan. *wajah Nova keceplosan cahaya*",
                "Angin sepoi-sepoi bikin suasana makin hangat."
            ]
        }
        
        event_type = "romantis" if risk < 50 else random.choice(["hampir_ketahuan", "romantis"])
        
        return {
            'type': event_type,
            'text': random.choice(events[event_type]),
            'risk_change': 10 if event_type == "hampir_ketahuan" else -5
        }


# =============================================================================
# SINGLETON
# =============================================================================

_anora_brain: Optional['AnoraBrain'] = None


def get_anora_brain() -> AnoraBrain:
    global _anora_brain
    if _anora_brain is None:
        _anora_brain = AnoraBrain()
    return _anora_brain


anora_brain = get_anora_brain()
