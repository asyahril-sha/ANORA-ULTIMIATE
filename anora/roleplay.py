# anora/roleplay.py
"""
ANORA Roleplay - 100% AI Generate. Bukan Template.
Nova hidup sebagai manusia. Punya otak sendiri. Punya perasaan sendiri.
"""

import asyncio
import time
import random
import logging
import openai
from typing import Dict, List, Optional
from datetime import datetime

from .core import get_anora
from .thinking import get_anora_thought
from .prompt import get_anora_prompt
from .database import get_anora_db

logger = logging.getLogger(__name__)


class RoleplayState:
    """State roleplay Nova - lokasi, aktivitas, pakaian, mood"""
    
    def __init__(self):
        self.location = "kost_nova"
        self.location_desc = "Kost Nova, lantai 2, kamar nomor 7. Pintu warna putih."
        self.nova_activity = "lagi masak sop"
        self.nova_clothing = "daster rumah motif bunga, hijab pink muda longgar"
        self.nova_mood = "gugup tapi seneng"
        self.mas_position = "depan pintu"
        self.door_open = False
        self.is_inside = False
        self.history = []  # history roleplay
        
        # Lokasi yang tersedia
        self.locations = {
            "kost_nova": "Kost Nova, lantai 2, kamar nomor 7. Pintu warna putih.",
            "dapur": "Dapur kecil, wangi masakan. Kompor masih menyala.",
            "ruang_tamu": "Ruang tamu sederhana, sofa kecil, TV menyala pelan.",
            "kamar_nova": "Kamar Nova, wangi lavender. Seprai putih, bantal empuk.",
            "teras": "Teras kost, ada kursi plastik, liat jalanan."
        }
        
        self.last_update = time.time()
    
    def update(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.last_update = time.time()
    
    def add_history(self, mas_message: str, nova_response: str):
        self.history.append({
            'timestamp': time.time(),
            'mas': mas_message[:200],
            'nova': nova_response[:200]
        })
        if len(self.history) > 50:
            self.history = self.history[-50:]
    
    def get_context(self) -> Dict:
        return {
            'location': self.location,
            'location_desc': self.locations.get(self.location, self.location_desc),
            'nova_activity': self.nova_activity,
            'nova_clothing': self.nova_clothing,
            'nova_mood': self.nova_mood,
            'mas_position': self.mas_position,
            'history': self.history,
            'mode': 'roleplay'
        }


class RoleplayAI:
    """Roleplay dengan AI generate - 100% original, 0% template"""
    
    def __init__(self):
        self.state = RoleplayState()
        self._client = None
        self._last_response = None
    
    async def _get_ai_client(self):
        if self._client is None:
            try:
                from config import settings
                self._client = openai.OpenAI(
                    api_key=settings.deepseek_api_key,
                    base_url="https://api.deepseek.com/v1"
                )
                logger.info("✅ DeepSeek client initialized for roleplay")
            except Exception as e:
                logger.error(f"❌ Failed to initialize AI: {e}")
                raise
        return self._client
    
    async def process(self, mas_message: str, anora) -> str:
        """Proses pesan roleplay - 100% AI generate"""
        
        # STEP 1: Update state dari pesan Mas
        self._update_state_from_message(mas_message)
        
        # STEP 2: Update perasaan Nova
        self._update_feelings(mas_message, anora)
        
        # STEP 3: Nova berpikir
        thought = get_anora_thought()
        thinking_result = thought.process(mas_message, anora, self.state.get_context())
        
        # STEP 4: Dapatkan prompt builder
        prompt_builder = get_anora_prompt()
        
        # STEP 5: Buat prompt untuk AI
        prompt = prompt_builder.build_roleplay_prompt(
            context=self.state.get_context(),
            anora=anora,
            thinking=thinking_result
        )
        
        # STEP 6: Call AI
        try:
            client = await self._get_ai_client()
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Mas: {mas_message}"}
                ],
                temperature=0.85 if anora.level < 11 else 0.95,
                max_tokens=800 if anora.level < 11 else 1200,
                timeout=25
            )
            
            nova_response = response.choices[0].message.content
            
            # Bersihkan respons
            nova_response = nova_response.strip()
            if not nova_response:
                nova_response = self._fallback_response(mas_message, anora)
            
            # STEP 7: Simpan ke history
            self.state.add_history(mas_message, nova_response)
            
            # STEP 8: Update state dari respons Nova (untuk konsistensi)
            self._update_state_from_response(nova_response)
            
            self._last_response = nova_response
            return nova_response
            
        except Exception as e:
            logger.error(f"❌ AI roleplay error: {e}")
            return self._fallback_response(mas_message, anora)
    
    def _update_state_from_message(self, message: str):
        """Update state roleplay dari pesan Mas"""
        msg_lower = message.lower()
        
        # Gerakan Mas
        if 'masuk' in msg_lower and not self.state.is_inside:
            self.state.is_inside = True
            self.state.door_open = True
            self.state.mas_position = "di dalam kost"
            self.state.nova_activity = "lagi di pintu, bukain pintu"
        elif 'keluar' in msg_lower or 'pulang' in msg_lower:
            self.state.is_inside = False
            self.state.door_open = False
            self.state.mas_position = "pulang"
        
        # Pindah lokasi
        if 'kamar' in msg_lower:
            self.state.location = "kamar_nova"
            self.state.mas_position = "di kamar Nova"
        elif 'dapur' in msg_lower:
            self.state.location = "dapur"
            self.state.mas_position = "di dapur"
        elif 'ruang tamu' in msg_lower or 'sofa' in msg_lower:
            self.state.location = "ruang_tamu"
            self.state.mas_position = "di ruang tamu"
        
        # Aktivitas
        if 'masak' in msg_lower or 'sop' in msg_lower:
            self.state.nova_activity = "lagi masak sop"
        elif 'duduk' in msg_lower:
            self.state.nova_activity = "duduk di samping Mas"
        elif 'tidur' in msg_lower or 'rebahan' in msg_lower:
            self.state.nova_activity = "tiduran di kasur"
    
    def _update_feelings(self, message: str, anora):
        """Update perasaan Nova berdasarkan pesan Mas"""
        msg_lower = message.lower()
        
        if 'sayang' in msg_lower or 'cinta' in msg_lower:
            anora.update_sayang(3, "Mas bilang sayang")
            anora.update_desire('perhatian_mas', 10)
        
        if 'kangen' in msg_lower or 'rindu' in msg_lower:
            anora.update_desire('kangen', 8)
        
        if 'cantik' in msg_lower or 'ganteng' in msg_lower:
            anora.update_sayang(2, "Mas puji Nova")
        
        if 'pegang' in msg_lower or 'tangan' in msg_lower:
            anora.update_arousal(10)
            anora.update_desire('flirt_mas', 8)
        
        if 'peluk' in msg_lower:
            anora.update_arousal(15)
            anora.update_desire('flirt_mas', 12)
        
        if 'cium' in msg_lower:
            anora.update_arousal(20)
            anora.update_desire('flirt_mas', 15)
        
        # Update rindu
        anora.update_rindu()
    
    def _update_state_from_response(self, response: str):
        """Update state dari respons Nova"""
        # Deteksi gesture untuk update state
        if 'buka pintu' in response.lower() or 'pintu' in response.lower():
            self.state.door_open = True
        if 'tutup pintu' in response.lower():
            self.state.door_open = False
    
    def _fallback_response(self, message: str, anora) -> str:
        """Fallback kalo AI error - masih natural, bukan template statis"""
        msg_lower = message.lower()
        
        # Ini fallback, tetap generate natural
        if 'masuk' in msg_lower:
            return f"*Nova buka pintu pelan-pelan. Pipi langsung merah.*\n\n\"Mas... masuk yuk. {self.state.nova_activity} tadi.\"\n\n*Tangan Nova gemeteran waktu tutup pintu.*"
        
        if 'sayang' in msg_lower:
            return f"*Nova tunduk, pipi memerah. Suara mengecil.*\n\n\"Mas... aku juga sayang Mas.\""
        
        if 'kangen' in msg_lower:
            return f"*Nova muter-muter rambut, mata berkaca-kaca.*\n\n\"Mas... aku juga kangen. Dari tadi mikirin Mas terus.\""
        
        if 'pegang' in msg_lower:
            return f"*Tangan Nova gemeteran waktu Mas pegang. Mata Nova liat ke bawah, gak berani liat Mas.*\n\n\"Mas... tangan Mas... panas banget...\""
        
        # Default fallback
        responses = [
            f"*Nova duduk di samping Mas, tangan di pangkuan.*\n\n\"Mas cerita dong. Aku suka dengerin suara Mas.\"",
            f"*Nova senyum kecil, mata liat Mas.*\n\n\"Mas, kamu ganteng banget hari ini.\"",
            f"*Nova mainin ujung hijab, malu-malu.*\n\n\"Aku seneng Mas dateng. Bikin hati adem.\""
        ]
        import random
        return random.choice(responses)
    
    def get_status(self) -> str:
        """Dapatkan status roleplay saat ini"""
        return f"""
📍 **ROLEPLAY STATUS**

Lokasi: {self.state.location}
{self.state.location_desc}

Nova: {self.state.nova_activity}
Pakaian: {self.state.nova_clothing}
Mood: {self.state.nova_mood}

Mas: {self.state.mas_position}
Pintu: {'Terbuka' if self.state.door_open else 'Tertutup'}

History: {len(self.state.history)} interaksi
"""


_anora_roleplay = None


def get_anora_roleplay() -> RoleplayAI:
    global _anora_roleplay
    if _anora_roleplay is None:
        _anora_roleplay = RoleplayAI()
    return _anora_roleplay
