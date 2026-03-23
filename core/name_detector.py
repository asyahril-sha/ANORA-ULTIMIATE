# core/name_detector.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Name Detector - Deteksi Nama Bot dalam Pesan User
=============================================================================
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any

logger = logging.getLogger(__name__)


class NameDetector:
    """
    Detektor nama bot yang pintar
    - Generate alias untuk nama bot (panggilan natural)
    - Deteksi panggilan dalam pesan user
    - Analisa subjek (aku/kamu/kita/panggilan nama)
    """
    
    def __init__(self):
        # Database panggilan umum Indonesia
        self.common_calls = {
            'sari': ['sa', 'ari', 'sasa', 'sari sayang'],
            'dewi': ['wi', 'dew', 'dedew', 'dewi cantik'],
            'maya': ['ya', 'may', 'maya sayang'],
            'putri': ['put', 'tri', 'putput', 'putri manis'],
            'rina': ['ri', 'na', 'rina sayang'],
            'diana': ['di', 'ana', 'dian', 'diana sayang'],
            'linda': ['lin', 'da', 'linda manis'],
            'ayu': ['yu', 'ayu cantik'],
            'sasha': ['sha', 'sas', 'sasha sayang'],
            'bella': ['bel', 'la', 'bella cantik'],
            'aurora': ['rora', 'auri', 'ora', 'rara', 'aurora sayang'],
            'cinta': ['cin', 'ta', 'cinta manis'],
            'kirana': ['kira', 'rana', 'nana', 'kirana sayang'],
            'nadia': ['nad', 'dia', 'nadia cantik'],
            'amara': ['mar', 'ara', 'amara sayang']
        }
        
        logger.info("✅ NameDetector initialized")
    
    def generate_aliases(self, bot_name: str) -> List[str]:
        """
        Generate alias yang manusiawi untuk nama bot
        
        Args:
            bot_name: Nama bot (contoh: "Sari")
        
        Returns:
            List of aliases
        """
        name = bot_name.lower()
        aliases = {name}
        
        # Aturan 1: 2-4 huruf pertama/akhir
        if len(name) >= 3:
            aliases.add(name[:3])
            aliases.add(name[-3:])
        
        if len(name) >= 4:
            aliases.add(name[:4])
            aliases.add(name[-4:])
        
        # Aturan 2: Nama panggilan umum Indonesia
        for key, values in self.common_calls.items():
            if key in name or name in key:
                for val in values:
                    aliases.add(val)
        
        # Aturan 3: Tambahkan "kak" prefix
        aliases.add(f"kak {name}")
        aliases.add(f"kak{name}")
        
        # Aturan 4: Tambahkan "sayang" suffix
        aliases.add(f"{name} sayang")
        
        # Filter yang terlalu pendek
        aliases = [a for a in aliases if 2 <= len(a) <= 20]
        
        # Urutkan berdasarkan panjang
        aliases.sort(key=len)
        
        logger.debug(f"Generated {len(aliases)} aliases for '{bot_name}'")
        
        return aliases
    
    def detect_name_in_message(self, message: str, aliases: List[str]) -> Tuple[bool, Optional[str]]:
        """
        Deteksi apakah user memanggil bot dengan namanya
        
        Args:
            message: Pesan user
            aliases: Daftar alias nama bot
        
        Returns:
            (terdeteksi, alias_yang_dipakai)
        """
        msg_lower = message.lower()
        
        # Pattern umum panggilan nama
        patterns = [
            r'^{}\s',           # Di awal kalimat + spasi
            r'\s{}\s',          # Di tengah kalimat
            r'\s{}$',           # Di akhir kalimat
            r'^{}$',            # Satu kata saja
            r'{}[!.,;?]',       # Diikuti tanda baca
            r'^{},',            # Di awal + koma
            r'^{}\.',           # Di awal + titik
            r'^{}!',            # Di awal + seru
            r'^{}\?',           # Di awal + tanya
        ]
        
        for alias in aliases:
            alias_lower = alias.lower()
            
            if len(alias_lower) < 2:
                continue
            
            for pattern_template in patterns:
                pattern = pattern_template.format(re.escape(alias_lower))
                if re.search(pattern, msg_lower):
                    return True, alias
            
            # Cek panggilan langsung
            if msg_lower.startswith(alias_lower + ' '):
                return True, alias
            if msg_lower.endswith(' ' + alias_lower):
                return True, alias
        
        # Cek panggilan dengan "kak" + nama
        for alias in aliases[:5]:
            alias_clean = alias.replace('kak ', '').replace('kak', '')
            if alias_clean and alias_clean != alias:
                if f"kak{alias_clean}" in msg_lower or f"kak {alias_clean}" in msg_lower:
                    return True, f"kak {alias_clean}"
        
        return False, None
    
    def analyze_subject(self, message: str, bot_aliases: List[str]) -> Dict[str, Any]:
        """
        Analisa subjek dari pesan user secara lengkap
        
        Args:
            message: Pesan user
            bot_aliases: Daftar alias nama bot
        
        Returns:
            Dict dengan info subjek
        """
        msg_lower = message.lower()
        
        # Deteksi nama bot
        bot_mentioned, used_alias = self.detect_name_in_message(message, bot_aliases)
        
        # Deteksi subjek dasar
        has_self = any(word in msg_lower for word in ['aku ', 'aku$', 'saya ', 'gue ', 'gw '])
        has_bot = any(word in msg_lower for word in ['kamu ', 'lu ', 'elo '])
        has_together = any(word in msg_lower for word in ['kita ', 'bareng ', 'bersama '])
        
        # Deteksi jenis kalimat
        is_question = '?' in msg_lower or any(q in msg_lower for q in ['apa', 'siapa', 'kenapa', 'bagaimana'])
        is_command = any(cmd in msg_lower for cmd in ['ke ', 'pindah', 'kesini', 'sini', 'ayo', 'pergi'])
        is_invitation = any(inv in msg_lower for inv in ['yuk', 'ayo', 'mari'])
        
        # Tentukan arah
        direction = 'unknown'
        if bot_mentioned:
            direction = 'bot_directed'
        elif has_bot:
            direction = 'bot_mentioned'
        elif has_self:
            direction = 'self_mentioned'
        elif has_together:
            direction = 'together_mentioned'
        
        # Logika keputusan
        if bot_mentioned:
            subject = 'bot'
            confidence = 0.95
            reason = f"dipanggil dengan '{used_alias}'"
        elif has_together:
            subject = 'together'
            confidence = 0.9
            reason = "ada kata 'kita'"
        elif has_bot:
            subject = 'bot'
            confidence = 0.85
            reason = "ada kata 'kamu'"
        elif has_self:
            subject = 'self'
            confidence = 0.9
            reason = "ada kata 'aku'"
        elif is_question:
            subject = 'question'
            confidence = 0.7
            reason = "pertanyaan"
        elif is_command or is_invitation:
            subject = 'bot'
            confidence = 0.6
            reason = "perintah/ajakan tanpa subjek"
        else:
            subject = 'unknown'
            confidence = 0.5
            reason = "tidak jelas"
        
        return {
            'subject': subject,
            'confidence': round(confidence, 2),
            'reason': reason,
            'mentioned_bot': bot_mentioned,
            'bot_alias': used_alias,
            'has_self': has_self,
            'has_bot': has_bot,
            'has_together': has_together,
            'is_question': is_question,
            'is_command': is_command,
            'is_invitation': is_invitation,
            'direction': direction,
            'raw_message': message[:100]
        }
    
    def get_suggested_response(self, analysis: Dict, bot_name: str, bot_location: str) -> str:
        """
        Dapatkan saran respons berdasarkan analisa subjek
        
        Args:
            analysis: Hasil dari analyze_subject()
            bot_name: Nama bot
            bot_location: Lokasi bot saat ini
        
        Returns:
            Saran respons
        """
        subject = analysis['subject']
        
        if subject == 'self':
            return f"Oh, kamu cerita tentang dirimu? Aku dengerin kok."
        
        elif subject == 'bot':
            if analysis['mentioned_bot']:
                alias = analysis['bot_alias'] or bot_name
                return f"Iya {alias}, ada apa?"
            else:
                return f"Aku di {bot_location}. Ada yang bisa dibantu?"
        
        elif subject == 'together':
            if analysis['is_invitation']:
                return "Ayo!"
            else:
                return f"Kita di {bot_location} ya"
        
        elif subject == 'question':
            return f"Aku di {bot_location}. Kamu?"
        
        else:
            return f"Aku di {bot_location}. Kamu lagi ngapain?"
    
    def detect_intent_from_call(self, message: str, bot_name: str) -> Dict[str, Any]:
        """
        Deteksi intent dari cara user memanggil bot
        
        Args:
            message: Pesan user
            bot_name: Nama bot
        
        Returns:
            Dict dengan intent info
        """
        msg_lower = message.lower()
        name_lower = bot_name.lower()
        
        patterns = {
            'panggilan_manja': [
                f"{name_lower} sayang",
                f"{name_lower} cinta",
                f"{name_lower} manis",
                f"sayang {name_lower}",
            ],
            'panggilan_marah': [
                f"{name_lower}!!!",
                f"{name_lower}!!",
                f"{name_lower}!",
                f"{name_lower} kenapa sih",
            ],
            'panggilan_serius': [
                f"{name_lower}, tolong",
                f"{name_lower}, bantu",
                f"{name_lower}, perlu",
            ],
            'panggilan_cemas': [
                f"{name_lower}...",
                f"{name_lower}?",
                f"{name_lower} kamu di mana",
            ]
        }
        
        intent = 'normal'
        for intent_type, pattern_list in patterns.items():
            for pattern in pattern_list:
                if pattern in msg_lower:
                    intent = intent_type
                    break
        
        return {
            'intent': intent,
            'bot_name': bot_name,
            'message': message[:50]
        }


_name_detector = None


def get_name_detector() -> NameDetector:
    """Dapatkan instance NameDetector (singleton)"""
    global _name_detector
    if _name_detector is None:
        _name_detector = NameDetector()
    return _name_detector


__all__ = ['NameDetector', 'get_name_detector']
