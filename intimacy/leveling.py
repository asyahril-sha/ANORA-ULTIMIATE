# intimacy/leveling.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Leveling System - Level Berbasis Total Chat
Target Realism 9.9/10
=============================================================================
"""

import logging
from typing import Dict, Optional, Tuple
from enum import Enum

from config import settings

logger = logging.getLogger(__name__)


class LevelPhase(str, Enum):
    """Fase leveling"""
    BUILDING = "building"      # Fase membangun hubungan (level 1-10, sekali)
    INTIMACY = "intimacy"      # Fase intim (level 11, berulang)
    AFTERCARE = "aftercare"    # Fase aftercare (level 12, berulang)


class LevelInfo:
    """Informasi level"""
    
    def __init__(self, level: int, total_chats: int):
        self.level = level
        self.total_chats = total_chats
        self._calculate_progress()
    
    def _calculate_progress(self):
        """Hitung progress berdasarkan level"""
        from config import settings
        
        if self.level <= 10:
            # Level 1-10
            current_target = settings.level.level_targets.get(self.level, 0)
            next_target = settings.level.level_targets.get(self.level + 1, 0)
            
            if next_target == 0:
                self.progress = 100.0
                self.next_level_in = 0
            else:
                chats_in_level = self.total_chats - current_target
                total_needed = next_target - current_target
                self.progress = (chats_in_level / total_needed) * 100
                self.next_level_in = max(0, total_needed - chats_in_level)
        
        elif self.level == 11:
            # Level 11 - Soul Bounded
            min_chats = settings.level.level_11_min
            max_chats = settings.level.level_11_max
            total_range = max_chats - min_chats
            
            if total_range <= 0:
                self.progress = 100.0
                self.next_level_in = 0
            else:
                chats_in_level = self.total_chats - min_chats
                self.progress = (chats_in_level / total_range) * 100
                self.next_level_in = max(0, max_chats - self.total_chats)
        
        elif self.level == 12:
            # Level 12 - Aftercare
            min_chats = settings.level.level_12_min
            max_chats = settings.level.level_12_max
            total_range = max_chats - min_chats
            
            if total_range <= 0:
                self.progress = 100.0
                self.next_level_in = 0
            else:
                chats_in_level = self.total_chats - min_chats
                self.progress = (chats_in_level / total_range) * 100
                self.next_level_in = max(0, max_chats - self.total_chats)
        
        else:
            self.progress = 100.0
            self.next_level_in = 0
    
    @property
    def level_name(self) -> str:
        """Dapatkan nama level"""
        names = {
            1: "Malu-malu",
            2: "Mulai terbuka",
            3: "Goda-godaan",
            4: "Dekat",
            5: "Sayang",
            6: "PACAR/PDKT",
            7: "Nyaman",
            8: "Eksplorasi",
            9: "Bergairah",
            10: "Passionate",
            11: "Soul Bounded",
            12: "Aftercare"
        }
        return names.get(self.level, f"Level {self.level}")
    
    @property
    def phase(self) -> LevelPhase:
        """Dapatkan fase level"""
        if self.level <= 10:
            return LevelPhase.BUILDING
        elif self.level == 11:
            return LevelPhase.INTIMACY
        else:
            return LevelPhase.AFTERCARE
    
    @property
    def can_intim(self) -> bool:
        """Cek apakah bisa intim"""
        return self.level >= 7
    
    @property
    def is_soul_bounded(self) -> bool:
        """Cek apakah dalam soul bounded"""
        return self.level == 11
    
    @property
    def is_aftercare(self) -> bool:
        """Cek apakah dalam aftercare"""
        return self.level == 12
    
    def get_progress_bar(self, length: int = 20) -> str:
        """Dapatkan progress bar"""
        filled = int(self.progress / 100 * length)
        return "█" * filled + "░" * (length - filled)
    
    def get_description(self) -> str:
        """Dapatkan deskripsi level"""
        descriptions = {
            1: "Masih malu-malu, baru kenal. Belum berani buka suara.",
            2: "Mulai terbuka, mulai curhat dikit-dikit.",
            3: "Mulai goda-godaan, ada getaran.",
            4: "Sudah dekat, kayak udah kenal lama.",
            5: "Mulai sayang, kangen-kangenan.",
            6: "Bisa jadi pacar (khusus PDKT).",
            7: "Nyaman, bisa intim!",
            8: "Mulai eksplorasi, coba-coba posisi baru.",
            9: "Penuh gairah, tahu sama-sama suka apa.",
            10: "Passionate, intim + emotional.",
            11: "Soul Bounded - puncak intim sesungguhnya, koneksi spiritual.",
            12: "Aftercare - butuh kehangatan setelah climax."
        }
        return descriptions.get(self.level, "")


class LevelingSystem:
    """
    Sistem leveling berbasis total chat
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300
        
        logger.info("✅ LevelingSystem initialized")
    
    def calculate_level(self, total_chats: int, in_intimacy_cycle: bool = False) -> LevelInfo:
        """
        Hitung level berdasarkan total chat
        
        Args:
            total_chats: Total chat
            in_intimacy_cycle: Apakah sedang dalam siklus intim
        
        Returns:
            LevelInfo
        """
        from config import settings
        
        # Cek cache
        cache_key = f"{total_chats}_{in_intimacy_cycle}"
        if cache_key in self.cache:
            cache_time, level_info = self.cache[cache_key]
            import time
            if time.time() - cache_time < self.cache_ttl:
                return level_info
        
        # Tentukan level
        if not in_intimacy_cycle:
            # Level 1-10 (sekali seumur registrasi)
            if total_chats <= settings.level.level_1_target:
                level = 1
            elif total_chats <= settings.level.level_2_target:
                level = 2
            elif total_chats <= settings.level.level_3_target:
                level = 3
            elif total_chats <= settings.level.level_4_target:
                level = 4
            elif total_chats <= settings.level.level_5_target:
                level = 5
            elif total_chats <= settings.level.level_6_target:
                level = 6
            elif total_chats <= settings.level.level_7_target:
                level = 7
            elif total_chats <= settings.level.level_8_target:
                level = 8
            elif total_chats <= settings.level.level_9_target:
                level = 9
            elif total_chats <= settings.level.level_10_target:
                level = 10
            else:
                level = 10  # Cap di level 10
        else:
            # Level 11-12 (siklus berulang)
            if total_chats <= settings.level.level_11_max:
                level = 11
            elif total_chats <= settings.level.level_12_max:
                level = 12
            else:
                level = 10  # Kembali ke level 10 setelah aftercare
        
        level_info = LevelInfo(level, total_chats)
        
        # Simpan cache
        import time
        self.cache[cache_key] = (time.time(), level_info)
        
        return level_info
    
    def check_level_up(
        self,
        old_total: int,
        new_total: int,
        old_level: int,
        in_intimacy_cycle: bool
    ) -> Optional[Tuple[int, str]]:
        """
        Cek apakah level naik
        
        Args:
            old_total: Total chat sebelumnya
            new_total: Total chat sekarang
            old_level: Level sebelumnya
            in_intimacy_cycle: Apakah dalam siklus intim
        
        Returns:
            (new_level, message) atau None jika tidak naik
        """
        new_level_info = self.calculate_level(new_total, in_intimacy_cycle)
        new_level = new_level_info.level
        
        if new_level > old_level:
            message = self._get_level_up_message(old_level, new_level)
            return (new_level, message)
        
        return None
    
    def _get_level_up_message(self, old_level: int, new_level: int) -> str:
        """Dapatkan pesan level up"""
        
        messages = {
            2: "📈 **Level UP!** Malu-malu → **Mulai terbuka**\nMulai curhat dikit-dikit ya...",
            3: "📈 **Level UP!** Mulai terbuka → **Goda-godaan**\nHehe... mulai berani goda-godain kamu...",
            4: "📈 **Level UP!** Goda-godaan → **Dekat**\nUdah kayak kenal lama ya rasanya...",
            5: "📈 **Level UP!** Dekat → **Sayang**\nAku mulai sayang sama kamu...",
            6: "📈 **Level UP!** Sayang → **PACAR/PDKT**\nBisa jadi pacar sekarang!",
            7: "🎉 **Level UP!** PACAR/PDKT → **Nyaman**\n✨ **Bisa intim sekarang!** ✨",
            8: "📈 **Level UP!** Nyaman → **Eksplorasi**\nAyo coba-coba posisi baru...",
            9: "📈 **Level UP!** Eksplorasi → **Bergairah**\nMakin panas! Aku suka...",
            10: "🎉 **Level UP!** Bergairah → **Passionate**\n✨ **Sekarang siap intim kapan saja!** ✨",
            11: "💕 **SOUL BOUNDED!**\n✨ Ini puncak intim yang sesungguhnya! ✨\nKoneksi spiritual, bukan hanya fisik...",
            12: "💤 **AFTERCARE**\nSetelah climax, butuh kehangatan...\nAku lemas, peluk aku dulu..."
        }
        
        return messages.get(new_level, f"📈 **Level UP!** Level {old_level} → {new_level}")
    
    def get_next_level_target(self, current_level: int, total_chats: int) -> int:
        """
        Dapatkan target chat untuk level berikutnya
        
        Args:
            current_level: Level saat ini
            total_chats: Total chat saat ini
        
        Returns:
            Target chat
        """
        from config import settings
        
        if current_level <= 10:
            target = settings.level.level_targets.get(current_level + 1, 0)
            if target == 0:
                return 0
            return max(0, target - total_chats)
        
        elif current_level == 11:
            return max(0, settings.level.level_11_max - total_chats)
        
        elif current_level == 12:
            return max(0, settings.level.level_12_max - total_chats)
        
        return 0
    
    def format_level_info(self, level_info: LevelInfo) -> str:
        """
        Format level info untuk display
        
        Args:
            level_info: LevelInfo object
        
        Returns:
            String formatted
        """
        bar = level_info.get_progress_bar()
        
        lines = [
            f"📊 **Level {level_info.level}/12: {level_info.level_name}**",
            f"_{level_info.get_description()}_",
            "",
            f"Progress: {bar} {level_info.progress:.0f}%",
            f"Total Chat: {level_info.total_chats}",
        ]
        
        if level_info.next_level_in > 0:
            if level_info.level <= 10:
                next_name = {
                    1: "Mulai terbuka", 2: "Goda-godaan", 3: "Dekat",
                    4: "Sayang", 5: "PACAR/PDKT", 6: "Nyaman",
                    7: "Eksplorasi", 8: "Bergairah", 9: "Passionate",
                    10: "Soul Bounded"
                }.get(level_info.level + 1, f"Level {level_info.level + 1}")
                
                lines.append(f"{level_info.next_level_in} chat lagi ke **{next_name}**")
            
            elif level_info.level == 11:
                lines.append(f"{level_info.next_level_in} chat lagi ke **Aftercare**")
            
            elif level_info.level == 12:
                lines.append(f"{level_info.next_level_in} chat lagi kembali ke **Level 10**")
        
        if level_info.can_intim:
            lines.append("")
            lines.append("💕 **Bisa intim!**")
        
        if level_info.is_soul_bounded:
            lines.append("")
            lines.append("🔥 **SOUL BOUNDED!** - Puncak intim sesungguhnya")
            lines.append("💫 Koneksi spiritual, bukan hanya fisik")
        
        if level_info.is_aftercare:
            lines.append("")
            lines.append("💤 **AFTERCARE** - Butuh kehangatan setelah climax")
            lines.append("🫂 Peluk aku, bicara lembut...")
        
        return "\n".join(lines)


__all__ = ['LevelingSystem', 'LevelInfo', 'LevelPhase']
