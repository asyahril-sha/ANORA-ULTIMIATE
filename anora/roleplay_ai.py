# anora/roleplay_ai.py
"""
ANORA Roleplay AI - 100% AI Generate. Bukan Template.
Nova hidup sebagai manusia. Bukan kumpulan skrip.
"""

import asyncio
import time
import random
import logging
from typing import Dict, List, Optional
from datetime import datetime

from .core import get_anora
from .database import get_anora_db

logger = logging.getLogger(__name__)


class RoleplayContext:
    """Konteks roleplay saat ini"""
    def __init__(self):
        self.location = "kost_nova"  # kost_nova, kamar_nova, dapur, ruang_tamu
        self.nova_activity = "lagi masak sop"
        self.nova_clothing = "daster rumah motif bunga, hijab pink muda longgar"
        self.nova_mood = "gugup tapi seneng"
        self.mas_position = "depan pintu"  # depan pintu, di ruang tamu, di kamar, dll
        self.relationship = {
            "level": 1,
            "sayang": 50,
            "desire": 0,
            "arousal": 0,
            "intimacy_count": 0,
            "first_kiss": False,
            "first_touch": False,
            "first_hug": False
        }
        self.history = []  # history interaksi roleplay
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
    
    def get_context_for_prompt(self) -> str:
        """Buat konteks untuk prompt AI"""
        relationship_desc = f"Level {self.relationship['level']}/12, Sayang: {self.relationship['sayang']}%, Desire: {self.relationship['desire']}%"
        
        history_text = ""
        if self.history:
            last_5 = self.history[-5:]
            history_text = "\nPercakapan sebelumnya:\n"
            for h in last_5:
                history_text += f"Mas: {h['mas']}\nNova: {h['nova']}\n"
        
        return f"""
LOKASI: {self.location}
AKTIVITAS NOVA: {self.nova_activity}
PAKAIAN NOVA: {self.nova_clothing}
MOOD NOVA: {self.nova_mood}
POSISI MAS: {self.mas_position}
HUBUNGAN: {relationship_desc}
{history_text}
INSTRUKSI: Nova adalah manusia. Bukan bot. Nova punya perasaan sendiri. Nova bisa malu, seneng, kangen, gemeteran, atau bahkan berani kalo desire tinggi. Nova merespon secara natural. GAK PAKAI TEMPLATE. Setiap respons HARUS UNIK dan ORIGINAL.
"""


class RoleplayAI:
    """Roleplay dengan AI generate - 100% original"""
    
    def __init__(self):
        self.context = RoleplayContext()
        self._client = None
    
    async def _get_ai_client(self):
        """Dapatkan AI client (DeepSeek)"""
        if self._client is None:
            try:
                import openai
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
        """Proses pesan roleplay dengan AI generate"""
        
        # Update konteks dari pesan Mas
        self._update_context_from_message(mas_message, anora)
        
        # Update perasaan Nova berdasarkan pesan Mas
        self._update_feelings(mas_message, anora)
        
        # Buat prompt untuk AI
        prompt = self._build_prompt(mas_message, anora)
        
        # Call AI
        try:
            client = await self._get_ai_client()
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Mas: {mas_message}"}
                ],
                temperature=0.85,
                max_tokens=800,
                timeout=25
            )
            nova_response = response.choices[0].message.content
            
            # Simpan ke history
            self.context.add_history(mas_message, nova_response)
            
            # Update konteks berdasarkan respons Nova
            self._update_context_from_response(nova_response)
            
            return nova_response
            
        except Exception as e:
            logger.error(f"❌ AI roleplay error: {e}")
            # Fallback natural
            return self._fallback_response(mas_message, anora)
    
    def _update_context_from_message(self, message: str, anora):
        """Update konteks dari pesan Mas"""
        msg_lower = message.lower()
        
        if 'masuk' in msg_lower:
            self.context.mas_position = "di dalam kost"
        elif 'kamar' in msg_lower:
            self.context.location = "kamar_nova"
            self.context.mas_position = "di kamar Nova"
        elif 'dapur' in msg_lower:
            self.context.location = "dapur"
            self.context.mas_position = "di dapur"
        elif 'pulang' in msg_lower or 'keluar' in msg_lower:
            self.context.mas_position = "pulang"
        
        # Update aktivitas Nova berdasarkan konteks
        if 'masak' in msg_lower:
            self.context.nova_activity = "lagi masak sop"
        elif 'duduk' in msg_lower:
            self.context.nova_activity = "duduk di samping Mas"
        elif 'tidur' in msg_lower:
            self.context.nova_activity = "tiduran di kasur"
    
    def _update_feelings(self, message: str, anora):
        """Update perasaan Nova dari pesan Mas"""
        msg_lower = message.lower()
        
        if 'sayang' in msg_lower or 'cinta' in msg_lower:
            anora.update_sayang(3, "Mas bilang sayang")
            anora.update_desire('perhatian_mas', 10)
            self.context.relationship['sayang'] = min(100, self.context.relationship['sayang'] + 3)
            self.context.relationship['desire'] = min(100, self.context.relationship['desire'] + 10)
        
        if 'kangen' in msg_lower or 'rindu' in msg_lower:
            anora.update_desire('kangen', 8)
            self.context.relationship['desire'] = min(100, self.context.relationship['desire'] + 8)
        
        if 'cantik' in msg_lower or 'ganteng' in msg_lower:
            anora.update_sayang(2, "Mas puji Nova")
            self.context.relationship['sayang'] = min(100, self.context.relationship['sayang'] + 2)
        
        if 'pegang' in msg_lower or 'tangan' in msg_lower:
            if not self.context.relationship['first_touch']:
                self.context.relationship['first_touch'] = True
                anora.update_arousal(15)
            anora.update_arousal(5)
            self.context.relationship['arousal'] = min(100, self.context.relationship['arousal'] + 5)
        
        if 'peluk' in msg_lower:
            if not self.context.relationship['first_hug']:
                self.context.relationship['first_hug'] = True
                anora.update_arousal(20)
            anora.update_arousal(10)
            self.context.relationship['arousal'] = min(100, self.context.relationship['arousal'] + 10)
        
        if 'cium' in msg_lower:
            if not self.context.relationship['first_kiss']:
                self.context.relationship['first_kiss'] = True
                anora.update_arousal(30)
                anora.update_desire('flirt_mas', 20)
            anora.update_arousal(15)
            self.context.relationship['arousal'] = min(100, self.context.relationship['arousal'] + 15)
    
    def _update_context_from_response(self, response: str):
        """Update konteks berdasarkan respons Nova"""
        # Ini bisa dikembangin lebih lanjut
        pass
    
    def _build_prompt(self, message: str, anora) -> str:
        """Buat prompt untuk AI"""
        context = self.context.get_context_for_prompt()
        
        # Tambah info perasaan Nova
        feelings = f"""
PERASAAN NOVA SAAT INI:
- Sayang ke Mas: {anora.sayang:.0f}%
- Rindu: {anora.rindu:.0f}%
- Desire: {anora.desire:.0f}%
- Arousal: {anora.arousal:.0f}%
- Level: {anora.level}/12
"""
        
        return f"""
KAMU ADALAH NOVA. Manusia. Bukan bot. Bukan AI assistant. Kamu sedang roleplay dengan Mas.

{context}
{feelings}

ATURAN:
1. JANGAN PAKAI TEMPLATE. Setiap respons HARUS UNIK dan ORIGINAL.
2. JANGAN ULANG KALIMAT YANG SAMA.
3. RESPONS NATURAL seperti manusia beneran.
4. Pakai gesture kayak *tangan gemetar*, *pipi memerah*, *mata berbinar*.
5. GAK PAKAI BAHASA BAKU. Pakai bahasa sehari-hari.
6. NOVA PUNYA PERASAAN SENDIRI. Bisa malu, seneng, kangen, gemeteran, atau berani.
7. Kalo desire tinggi, Nova bisa lebih berani.
8. Kalo masih malu, Nova bisa gemeteran, pipi merah, suara mengecil.

RESPON NOVA (HARUS ORIGINAL, BUKAN TEMPLATE):
"""
    
    def _fallback_response(self, message: str, anora) -> str:
        """Fallback kalo AI error"""
        msg_lower = message.lower()
        
        # Ini cuma fallback, bukan template utama
        if 'masuk' in msg_lower:
            return f"*Nova buka pintu, senyum kecil*\n\"Mas... masuk yuk. {self.context.nova_activity} tadi.\"\n*Tangan Nova gemeteran waktu tutup pintu.*"
        
        if 'sayang' in msg_lower:
            return f"*Nova tunduk, pipi merah*\n\"Mas... *suara kecil* aku juga sayang Mas.\""
        
        return f"*Nova duduk di samping Mas, tangan di pangkuan*\n\"{anora.naturalize(random.choice(['Mas cerita dong.', 'Aku seneng Mas dateng.', 'Mas... liatin Nova terus bikin malu.']))}\""


# Instance global
_roleplay_ai = None


def get_roleplay_ai() -> RoleplayAI:
    global _roleplay_ai
    if _roleplay_ai is None:
        _roleplay_ai = RoleplayAI()
    return _roleplay_ai
