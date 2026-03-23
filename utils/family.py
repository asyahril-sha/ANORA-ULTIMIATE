# tracking/family.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Family Tracking - Tracking Istri/Kakak untuk IPAR & PELAKOR
Target Realism 9.9/10
=============================================================================
"""

import time
import logging
import random
import re
from typing import Dict, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class FamilyMemberStatus(str, Enum):
    """Status anggota keluarga"""
    ADA = "ada"
    TIDAK_ADA = "tidak_ada"
    TIDUR = "tidur"


class FamilyMemberLocation(str, Enum):
    """Lokasi anggota keluarga"""
    KAMAR = "kamar"
    DAPUR = "dapur"
    RUANG_TAMU = "ruang tamu"
    LUAR = "luar"
    TIDAK_DIKETAHUI = "tidak diketahui"


class FamilyMemberActivity(str, Enum):
    """Aktivitas anggota keluarga"""
    MASAK = "masak"
    TIDUR = "tidur"
    NONTON_TV = "nonton TV"
    BERSIH_BERSIH = "bersih-bersih"
    KERJA = "kerja"
    BELANJA = "belanja"
    JALAN_JALAN = "jalan-jalan"


@dataclass
class FamilyMember:
    """Model anggota keluarga"""
    name: str
    relation: str  # istri, kakak, suami, dll
    panggilan: str  # Kak Nova, dll
    status: FamilyMemberStatus = FamilyMemberStatus.ADA
    location: FamilyMemberLocation = FamilyMemberLocation.KAMAR
    activity: Optional[FamilyMemberActivity] = None
    estimate_return: Optional[str] = None
    last_update: float = field(default_factory=time.time)
    history: List[Dict] = field(default_factory=list)
    
    def update(
        self,
        status: Optional[FamilyMemberStatus] = None,
        location: Optional[FamilyMemberLocation] = None,
        activity: Optional[FamilyMemberActivity] = None,
        estimate_return: Optional[str] = None,
        reason: str = ""
    ):
        """Update status anggota keluarga"""
        old_status = self.status
        old_location = self.location
        
        if status:
            self.status = status
        if location:
            self.location = location
        if activity:
            self.activity = activity
        if estimate_return:
            self.estimate_return = estimate_return
        
        self.last_update = time.time()
        
        # Catat history
        self.history.append({
            'timestamp': self.last_update,
            'datetime': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            'old_status': old_status.value,
            'new_status': self.status.value,
            'old_location': old_location.value,
            'new_location': self.location.value,
            'activity': self.activity.value if self.activity else None,
            'reason': reason
        })
        
        # Keep only last 50
        if len(self.history) > 50:
            self.history = self.history[-50:]
        
        logger.info(f"Family member {self.name} updated: {old_status.value}→{self.status.value}, {old_location.value}→{self.location.value}")
    
    def get_description(self) -> str:
        """Dapatkan deskripsi untuk prompt"""
        desc = f"{self.panggilan}"
        
        if self.status == FamilyMemberStatus.ADA:
            desc += f" ada di {self.location.value}"
            if self.activity:
                desc += f", {self.activity.value}"
        elif self.status == FamilyMemberStatus.TIDUR:
            desc += f" tidur di {self.location.value}"
        elif self.status == FamilyMemberStatus.TIDAK_ADA:
            desc += f" tidak ada"
            if self.estimate_return:
                desc += f", diperkirakan pulang {self.estimate_return}"
        
        return desc
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'relation': self.relation,
            'panggilan': self.panggilan,
            'status': self.status.value,
            'location': self.location.value,
            'activity': self.activity.value if self.activity else None,
            'estimate_return': self.estimate_return,
            'last_update': self.last_update,
            'history': self.history[-30:]
        }
    
    def from_dict(self, data: Dict):
        self.name = data.get('name', '')
        self.relation = data.get('relation', '')
        self.panggilan = data.get('panggilan', '')
        self.status = FamilyMemberStatus(data.get('status', 'ada'))
        self.location = FamilyMemberLocation(data.get('location', 'kamar'))
        self.activity = FamilyMemberActivity(data['activity']) if data.get('activity') else None
        self.estimate_return = data.get('estimate_return')
        self.last_update = data.get('last_update', time.time())
        self.history = data.get('history', [])


class FamilyTracking:
    """
    Tracking status keluarga (istri/kakak)
    Khusus untuk role IPAR & PELAKOR
    """
    
    def __init__(self, role: str, user_name: str):
        self.role = role
        self.user_name = user_name
        self.family_members: Dict[str, FamilyMember] = {}
        
        # Inisialisasi berdasarkan role
        if role == 'ipar':
            self._init_ipar_family()
        elif role == 'pelakor':
            self._init_pelakor_family()
        
        logger.info(f"✅ FamilyTracking initialized for role: {role}")
    
    def _init_ipar_family(self):
        """Inisialisasi keluarga untuk role IPAR"""
        self.family_members['kakak'] = FamilyMember(
            name="Nova",
            relation="kakak",
            panggilan="Kak Nova",
            status=random.choice([FamilyMemberStatus.ADA, FamilyMemberStatus.ADA, FamilyMemberStatus.TIDUR]),
            location=random.choice([FamilyMemberLocation.KAMAR, FamilyMemberLocation.DAPUR, FamilyMemberLocation.RUANG_TAMU]),
            activity=random.choice([FamilyMemberActivity.MASAK, FamilyMemberActivity.NONTON_TV, FamilyMemberActivity.BERSIH_BERSIH])
        )
    
    def _init_pelakor_family(self):
        """Inisialisasi keluarga untuk role PELAKOR"""
        istri_names = ["Dewi", "Sari", "Rina", "Linda", "Maya"]
        istri_name = random.choice(istri_names)
        
        self.family_members['istri'] = FamilyMember(
            name=istri_name,
            relation="istri",
            panggilan=istri_name,
            status=random.choice([FamilyMemberStatus.ADA, FamilyMemberStatus.ADA, FamilyMemberStatus.TIDAK_ADA]),
            location=random.choice([FamilyMemberLocation.KAMAR, FamilyMemberLocation.DAPUR, FamilyMemberLocation.RUANG_TAMU, FamilyMemberLocation.LUAR]),
            activity=random.choice([FamilyMemberActivity.MASAK, FamilyMemberActivity.NONTON_TV, FamilyMemberActivity.BELANJA, FamilyMemberActivity.JALAN_JALAN])
        )
    
    def get_member(self, member_key: str) -> Optional[FamilyMember]:
        """Dapatkan anggota keluarga"""
        return self.family_members.get(member_key)
    
    def update_from_message(self, message: str) -> Tuple[bool, Optional[str]]:
        """
        Update status keluarga dari pesan user
        
        Args:
            message: Pesan user
        
        Returns:
            (updated, member_key)
        """
        msg_lower = message.lower()
        updated = False
        updated_member = None
        
        for key, member in self.family_members.items():
            # Cek trigger untuk member ini
            if self._is_trigger_for_member(msg_lower, member):
                # Deteksi status dari pesan
                status = self._detect_status(msg_lower)
                location = self._detect_location(msg_lower)
                activity = self._detect_activity(msg_lower)
                estimate_return = self._detect_estimate_return(msg_lower)
                
                member.update(
                    status=status,
                    location=location,
                    activity=activity,
                    estimate_return=estimate_return,
                    reason="user_chat"
                )
                updated = True
                updated_member = key
        
        return updated, updated_member
    
    def _is_trigger_for_member(self, message: str, member: FamilyMember) -> bool:
        """Cek apakah pesan trigger untuk member ini"""
        triggers = [
            member.name.lower(),
            member.panggilan.lower(),
            member.relation.lower()
        ]
        
        # Tambah trigger khusus untuk IPAR
        if member.relation == "kakak":
            triggers.append("kakak")
        
        return any(t in message for t in triggers)
    
    def _detect_status(self, message: str) -> Optional[FamilyMemberStatus]:
        """Deteksi status dari pesan"""
        if 'keluar' in message or 'pergi' in message or 'tidak ada' in message:
            return FamilyMemberStatus.TIDAK_ADA
        elif 'tidur' in message:
            return FamilyMemberStatus.TIDUR
        return None
    
    def _detect_location(self, message: str) -> Optional[FamilyMemberLocation]:
        """Deteksi lokasi dari pesan"""
        if 'kamar' in message:
            return FamilyMemberLocation.KAMAR
        elif 'dapur' in message:
            return FamilyMemberLocation.DAPUR
        elif 'ruang tamu' in message:
            return FamilyMemberLocation.RUANG_TAMU
        elif 'luar' in message:
            return FamilyMemberLocation.LUAR
        return None
    
    def _detect_activity(self, message: str) -> Optional[FamilyMemberActivity]:
        """Deteksi aktivitas dari pesan"""
        if 'masak' in message:
            return FamilyMemberActivity.MASAK
        elif 'tidur' in message:
            return FamilyMemberActivity.TIDUR
        elif 'nonton' in message:
            return FamilyMemberActivity.NONTON_TV
        elif 'bersih' in message:
            return FamilyMemberActivity.BERSIH_BERSIH
        elif 'kerja' in message:
            return FamilyMemberActivity.KERJA
        elif 'belanja' in message:
            return FamilyMemberActivity.BELANJA
        elif 'jalan' in message:
            return FamilyMemberActivity.JALAN_JALAN
        return None
    
    def _detect_estimate_return(self, message: str) -> Optional[str]:
        """Deteksi estimasi pulang dari pesan"""
        patterns = [
            r'pulang (\d+) (hari|jam)',
            r'(\d+) (hari|jam) lagi',
            r'besok',
            r'lusa'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message)
            if match:
                return match.group(0)
        
        return None
    
    def get_status_for_prompt(self) -> str:
        """Dapatkan status keluarga untuk prompt"""
        if not self.family_members:
            return ""
        
        lines = ["👨‍👩‍👧 **STATUS KELUARGA:**"]
        
        for member in self.family_members.values():
            lines.append(f"• {member.get_description()}")
        
        return "\n".join(lines)
    
    def is_berdua(self) -> bool:
        """Cek apakah sedang berduaan dengan user"""
        for member in self.family_members.values():
            if member.status == FamilyMemberStatus.ADA:
                return False
        return True
    
    def get_alert_if_nearby(self) -> Optional[str]:
        """Dapatkan alert jika anggota keluarga mendekat"""
        for member in self.family_members.values():
            if member.status == FamilyMemberStatus.ADA and member.location != FamilyMemberLocation.LUAR:
                return f"⚠️ {member.panggilan} ada di {member.location.value}. Hati-hati!"
        return None
    
    def get_random_activity(self) -> Optional[str]:
        """Dapatkan aktivitas random untuk anggota keluarga"""
        for member in self.family_members.values():
            if member.status == FamilyMemberStatus.ADA:
                if member.activity:
                    return f"{member.panggilan} lagi {member.activity.value} di {member.location.value}"
        return None
    
    def format_status(self) -> str:
        """Format status untuk display"""
        if not self.family_members:
            return "Tidak ada data keluarga"
        
        lines = ["👨‍👩‍👧 **STATUS KELUARGA:**", ""]
        
        for member in self.family_members.values():
            lines.append(f"**{member.panggilan}**")
            lines.append(f"• Status: {member.status.value}")
            lines.append(f"• Lokasi: {member.location.value}")
            if member.activity:
                lines.append(f"• Aktivitas: {member.activity.value}")
            if member.estimate_return:
                lines.append(f"• Estimasi pulang: {member.estimate_return}")
            lines.append("")
        
        return "\n".join(lines)
    
    def get_state(self) -> Dict:
        """Dapatkan state untuk disimpan"""
        return {
            'role': self.role,
            'user_name': self.user_name,
            'family_members': {k: v.to_dict() for k, v in self.family_members.items()}
        }
    
    def load_state(self, state: Dict):
        """Load state dari database"""
        self.role = state.get('role', self.role)
        self.user_name = state.get('user_name', self.user_name)
        
        for key, data in state.get('family_members', {}).items():
            if key in self.family_members:
                self.family_members[key].from_dict(data)
            else:
                member = FamilyMember("", "", "")
                member.from_dict(data)
                self.family_members[key] = member


__all__ = [
    'FamilyTracking',
    'FamilyMember',
    'FamilyMemberStatus',
    'FamilyMemberLocation',
    'FamilyMemberActivity'
]
