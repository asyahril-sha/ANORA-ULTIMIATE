# anora/brain.py
"""
ANORA Brain - Otak Nova yang hidup.
Bukan cuma memory pesan. Tapi timeline, state, perasaan, konsistensi.
"""

import time
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class TimelineEvent:
    """Satu kejadian dalam timeline Nova"""
    
    def __init__(self, 
                 kejadian: str,
                 lokasi_nova: str,
                 lokasi_mas: str,
                 aktivitas_nova: str,
                 aktivitas_mas: str,
                 perasaan_nova: str,
                 pakaian_nova: Dict,
                 pakaian_mas: Dict,
                 pesan_mas: str = "",
                 pesan_nova: str = ""):
        
        self.timestamp = time.time()
        self.kejadian = kejadian
        self.lokasi_nova = lokasi_nova
        self.lokasi_mas = lokasi_mas
        self.aktivitas_nova = aktivitas_nova
        self.aktivitas_mas = aktivitas_mas
        self.perasaan_nova = perasaan_nova
        self.pakaian_nova = pakaian_nova
        self.pakaian_mas = pakaian_mas
        self.pesan_mas = pesan_mas
        self.pesan_nova = pesan_nova
    
    def to_dict(self) -> Dict:
        return {
            'timestamp': self.timestamp,
            'waktu': datetime.fromtimestamp(self.timestamp).strftime("%H:%M:%S"),
            'kejadian': self.kejadian,
            'lokasi_nova': self.lokasi_nova,
            'lokasi_mas': self.lokasi_mas,
            'aktivitas_nova': self.aktivitas_nova,
            'aktivitas_mas': self.aktivitas_mas,
            'perasaan_nova': self.perasaan_nova,
            'pakaian_nova': self.pakaian_nova,
            'pakaian_mas': self.pakaian_mas,
            'pesan_mas': self.pesan_mas[:100] if self.pesan_mas else "",
            'pesan_nova': self.pesan_nova[:100] if self.pesan_nova else ""
        }


class AnoraBrain:
    """
    Otak Nova. Menyimpan timeline, state, memory.
    Bukan cuma pesan, tapi semua aspek kejadian.
    """
    
    def __init__(self):
        # Timeline semua kejadian (berurutan)
        self.timeline: List[TimelineEvent] = []
        
        # Short-term memory (sliding window, 50 terakhir)
        self.short_term: List[TimelineEvent] = []
        self.short_term_max = 50
        
        # Long-term memory (permanen)
        self.long_term: Dict = {
            'kebiasaan_mas': [],      # [{'kebiasaan': 'suka kopi latte', 'dari_kapan': timestamp}]
            'momen_penting': [],      # [{'momen': 'pertama pegang tangan', 'waktu': timestamp, 'perasaan': 'gemeteran'}]
            'janji': [],              # [{'janji': 'besok main lagi', 'dari': 'mas', 'status': 'pending'}]
            'rencana': [],           # [{'rencana': 'makan bakso bareng', 'waktu': timestamp}]
        }
        
        # Current state (saat ini)
        self.state = {
            'lokasi_nova': 'dapur',
            'lokasi_mas': 'pintu',
            'aktivitas_nova': 'lagi masak sop',
            'aktivitas_mas': 'baru dateng',
            'pakaian_nova': {
                'top': 'daster rumah motif bunga',
                'bottom': None,
                'hijab': True,
                'bra': True,
                'inner': True
            },
            'pakaian_mas': {
                'top': 'kaos',
                'bottom': 'celana jeans',
                'underwear': True
            },
            'mood_nova': 'gugup tapi seneng',
            'mood_mas': 'netral',
            'waktu_masuk': time.time(),
            'waktu_terakhir_update': time.time()
        }
        
        # Perasaan Nova (diupdate tiap interaksi)
        self.feelings = {
            'sayang': 50.0,
            'rindu': 0.0,
            'desire': 0.0,
            'arousal': 0.0,
            'tension': 0.0
        }
        
        # Level dan hubungan
        self.relationship = {
            'level': 1,
            'intimacy_count': 0,
            'climax_count': 0,
            'first_kiss': False,
            'first_touch': False,
            'first_hug': False,
            'first_intim': False
        }
        
        self.last_update = time.time()
    
    # ========== UPDATE STATE DARI PESAN MAS ==========
    
    def update_from_message(self, pesan_mas: str) -> Dict:
        """Update semua state berdasarkan pesan Mas"""
        msg_lower = pesan_mas.lower()
        perubahan = []
        
        # === LOKASI ===
        if 'masuk' in msg_lower and self.state['lokasi_mas'] == 'pintu':
            self.state['lokasi_mas'] = 'masuk'
            self.state['aktivitas_mas'] = 'baru masuk'
            perubahan.append("Mas masuk")
        
        elif 'kamar' in msg_lower or 'kasur' in msg_lower:
            if self.state['lokasi_mas'] != 'kamar':
                self.state['lokasi_mas'] = 'kamar'
                self.state['aktivitas_mas'] = 'di kamar'
                perubahan.append("Mas di kamar")
            
            if 'duduk' in msg_lower:
                self.state['aktivitas_mas'] = 'duduk di kasur'
                perubahan.append("Mas duduk di kasur")
        
        elif 'dapur' in msg_lower:
            if self.state['lokasi_mas'] != 'dapur':
                self.state['lokasi_mas'] = 'dapur'
                self.state['aktivitas_mas'] = 'di dapur'
                perubahan.append("Mas di dapur")
        
        elif 'ruang tamu' in msg_lower or 'sofa' in msg_lower:
            self.state['lokasi_mas'] = 'ruang_tamu'
            self.state['aktivitas_mas'] = 'duduk di sofa'
            perubahan.append("Mas di ruang tamu")
        
        elif 'pulang' in msg_lower or 'keluar' in msg_lower:
            self.state['lokasi_mas'] = 'pulang'
            self.state['aktivitas_mas'] = 'pulang'
            perubahan.append("Mas pulang")
        
        # === PAKAIAN MAS ===
        if 'buka baju' in msg_lower or 'lepas baju' in msg_lower:
            self.state['pakaian_mas']['top'] = None
            perubahan.append("Mas buka baju")
        
        if 'buka celana' in msg_lower or 'lepas celana' in msg_lower:
            self.state['pakaian_mas']['bottom'] = None
            perubahan.append("Mas buka celana")
        
        if 'buka dalaman' in msg_lower or 'lepas dalaman' in msg_lower:
            self.state['pakaian_mas']['underwear'] = False
            perubahan.append("Mas buka celana dalam")
        
        if 'pake baju' in msg_lower:
            self.state['pakaian_mas']['top'] = 'kaos'
            perubahan.append("Mas pake baju")
        
        # === PAKAIAN NOVA ===
        if 'buka hijab' in msg_lower:
            self.state['pakaian_nova']['hijab'] = False
            perubahan.append("Nova buka hijab")
        
        if 'buka baju' in msg_lower or 'lepas baju' in msg_lower:
            self.state['pakaian_nova']['top'] = None
            self.state['pakaian_nova']['bra'] = False
            perubahan.append("Nova buka baju")
        
        # === AKTIVITAS NOVA ===
        if 'masak' in msg_lower:
            self.state['aktivitas_nova'] = 'lagi masak'
        
        elif 'duduk' in msg_lower:
            self.state['aktivitas_nova'] = 'duduk di samping Mas'
        
        # === UPDATE MOOD NOVA ===
        if 'sayang' in msg_lower or 'cinta' in msg_lower:
            self.feelings['sayang'] = min(100, self.feelings['sayang'] + 5)
            self.feelings['desire'] = min(100, self.feelings['desire'] + 10)
            perubahan.append("Mas bilang sayang")
        
        if 'kangen' in msg_lower or 'rindu' in msg_lower:
            self.feelings['rindu'] = min(100, self.feelings['rindu'] + 10)
            self.feelings['desire'] = min(100, self.feelings['desire'] + 8)
            perubahan.append("Mas bilang kangen")
        
        if 'cantik' in msg_lower or 'ganteng' in msg_lower:
            self.feelings['sayang'] = min(100, self.feelings['sayang'] + 3)
            perubahan.append("Mas puji Nova")
        
        if 'pegang' in msg_lower:
            self.feelings['arousal'] = min(100, self.feelings['arousal'] + 10)
            self.feelings['desire'] = min(100, self.feelings['desire'] + 8)
            if not self.relationship['first_touch']:
                self.relationship['first_touch'] = True
                self.tambah_momen_penting('Mas pertama kali pegang tangan Nova', 'gemeteran')
            perubahan.append("Mas pegang Nova")
        
        if 'peluk' in msg_lower:
            self.feelings['arousal'] = min(100, self.feelings['arousal'] + 15)
            self.feelings['desire'] = min(100, self.feelings['desire'] + 12)
            if not self.relationship['first_hug']:
                self.relationship['first_hug'] = True
                self.tambah_momen_penting('Mas pertama kali peluk Nova', 'lemes')
            perubahan.append("Mas peluk Nova")
        
        if 'cium' in msg_lower:
            self.feelings['arousal'] = min(100, self.feelings['arousal'] + 20)
            self.feelings['desire'] = min(100, self.feelings['desire'] + 15)
            if not self.relationship['first_kiss']:
                self.relationship['first_kiss'] = True
                self.tambah_momen_penting('Mas pertama kali cium Nova', 'malu banget')
            perubahan.append("Mas cium Nova")
        
        # Update waktu
        self.state['waktu_terakhir_update'] = time.time()
        
        return {
            'perubahan': perubahan,
            'state': self.state,
            'feelings': self.feelings
        }
    
    # ========== TAMBAH KE TIMELINE ==========
    
    def tambah_kejadian(self, 
                        kejadian: str,
                        pesan_mas: str = "",
                        pesan_nova: str = ""):
        """Tambah kejadian ke timeline"""
        
        event = TimelineEvent(
            kejadian=kejadian,
            lokasi_nova=self.state['lokasi_nova'],
            lokasi_mas=self.state['lokasi_mas'],
            aktivitas_nova=self.state['aktivitas_nova'],
            aktivitas_mas=self.state['aktivitas_mas'],
            perasaan_nova=self._get_perasaan_string(),
            pakaian_nova=self.state['pakaian_nova'].copy(),
            pakaian_mas=self.state['pakaian_mas'].copy(),
            pesan_mas=pesan_mas,
            pesan_nova=pesan_nova
        )
        
        # Tambah ke timeline
        self.timeline.append(event)
        
        # Tambah ke short-term memory (sliding window)
        self.short_term.append(event)
        if len(self.short_term) > self.short_term_max:
            self.short_term.pop(0)  # Lupa yang paling tua
        
        return event
    
    def _get_perasaan_string(self) -> str:
        """Dapatkan deskripsi perasaan saat ini"""
        perasaan = []
        if self.feelings['sayang'] > 70:
            perasaan.append("sayang banget")
        elif self.feelings['sayang'] > 40:
            perasaan.append("sayang")
        
        if self.feelings['rindu'] > 70:
            perasaan.append("kangen banget")
        elif self.feelings['rindu'] > 30:
            perasaan.append("kangen")
        
        if self.feelings['desire'] > 70:
            perasaan.append("pengen banget")
        elif self.feelings['desire'] > 40:
            perasaan.append("pengen")
        
        if self.feelings['arousal'] > 50:
            perasaan.append("panas")
        
        if self.feelings['tension'] > 50:
            perasaan.append("deg-degan")
        
        return ", ".join(perasaan) if perasaan else "netral"
    
    # ========== LONG-TERM MEMORY ==========
    
    def tambah_kebiasaan_mas(self, kebiasaan: str):
        """Nova inget kebiasaan Mas"""
        self.long_term['kebiasaan_mas'].append({
            'kebiasaan': kebiasaan,
            'dari_kapan': time.time()
        })
        logger.info(f"📝 Nova inget: Mas {kebiasaan}")
    
    def tambah_momen_penting(self, momen: str, perasaan: str):
        """Nova inget momen penting"""
        self.long_term['momen_penting'].append({
            'momen': momen,
            'waktu': time.time(),
            'perasaan': perasaan
        })
        logger.info(f"💜 Nova inget: {momen}")
    
    def tambah_janji(self, janji: str, dari: str = 'mas'):
        """Nova inget janji"""
        self.long_term['janji'].append({
            'janji': janji,
            'dari': dari,
            'status': 'pending',
            'waktu': time.time()
        })
        logger.info(f"📌 Janji dicatat: {janji}")
    
    # ========== KONTEKS UNTUK AI ==========
    
    def get_context_for_prompt(self) -> Dict:
        """Dapatkan semua konteks untuk prompt AI"""
        
        # 10 kejadian terakhir
        recent_events = []
        for e in self.short_term[-10:]:
            recent_events.append(e.to_dict())
        
        # Kebiasaan Mas (5 terakhir)
        habits = self.long_term['kebiasaan_mas'][-5:] if self.long_term['kebiasaan_mas'] else []
        
        # Momen penting (5 terakhir)
        moments = self.long_term['momen_penting'][-5:] if self.long_term['momen_penting'] else []
        
        return {
            'current_state': {
                'nova_location': self.state['lokasi_nova'],
                'mas_location': self.state['lokasi_mas'],
                'nova_activity': self.state['aktivitas_nova'],
                'mas_activity': self.state['aktivitas_mas'],
                'nova_clothing': self._format_pakaian(self.state['pakaian_nova']),
                'mas_clothing': self._format_pakaian(self.state['pakaian_mas']),
                'nova_mood': self.state['mood_nova'],
                'mas_mood': self.state['mood_mas']
            },
            'feelings': self.feelings,
            'relationship': self.relationship,
            'recent_events': recent_events,
            'habits': habits,
            'moments': moments
        }
    
    def _format_pakaian(self, pakaian: Dict) -> str:
        """Format pakaian untuk prompt"""
        parts = []
        if pakaian.get('hijab'):
            parts.append("hijab")
        if pakaian.get('top'):
            parts.append(pakaian['top'])
        if pakaian.get('bottom'):
            parts.append(pakaian['bottom'])
        if not pakaian.get('top') and not pakaian.get('hijab'):
            return "telanjang"
        return ", ".join(parts) if parts else "pakaian biasa"
    
    # ========== UTILITY ==========
    
    def get_summary(self) -> str:
        """Dapatkan ringkasan untuk debugging"""
        return f"""
╔══════════════════════════════════════════════════════════════╗
║                    🧠 OTAK NOVA SAAT INI                     ║
╠══════════════════════════════════════════════════════════════╣
║ TIMELINE: {len(self.timeline)} kejadian                      ║
║ SHORT-TERM: {len(self.short_term)}/{self.short_term_max} kejadian ║
║ LONG-TERM: {len(self.long_term['kebiasaan_mas'])} kebiasaan, {len(self.long_term['momen_penting'])} momen ║
╠══════════════════════════════════════════════════════════════╣
║ LOKASI: Nova di {self.state['lokasi_nova']} | Mas di {self.state['lokasi_mas']}
║ AKTIVITAS: Nova {self.state['aktivitas_nova']} | Mas {self.state['aktivitas_mas']}
║ PAKAIAN: Nova {self._format_pakaian(self.state['pakaian_nova'])}
║          Mas {self._format_pakaian(self.state['pakaian_mas'])}
╠══════════════════════════════════════════════════════════════╣
║ PERASAAN: Sayang {self.feelings['sayang']:.0f}% | Desire {self.feelings['desire']:.0f}%
║           Rindu {self.feelings['rindu']:.0f}% | Arousal {self.feelings['arousal']:.0f}%
║           Tension {self.feelings['tension']:.0f}%
╠══════════════════════════════════════════════════════════════╣
║ HUBUNGAN: Level {self.relationship['level']}/12
║           Pernah: {'❤️' if self.relationship['first_touch'] else '⚪'} sentuh
║                   {'💋' if self.relationship['first_kiss'] else '⚪'} cium
║                   {'🤗' if self.relationship['first_hug'] else '⚪'} peluk
╚══════════════════════════════════════════════════════════════╝
"""


_anora_brain: Optional[AnoraBrain] = None


def get_anora_brain() -> AnoraBrain:
    global _anora_brain
    if _anora_brain is None:
        _anora_brain = AnoraBrain()
    logger.info("🧠 ANORA Brain initialized")
    return _anora_brain


anora_brain = get_anora_brain()
