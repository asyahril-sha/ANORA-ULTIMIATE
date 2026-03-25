# core/ai_engine.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
AI Engine Utama - 100% AI Generate Tanpa Template Statis
Target Realism 9.9/10
=============================================================================
"""

import asyncio
import time
import random
import logging
import json
from typing import Dict, List, Optional, Any, TYPE_CHECKING
from datetime import datetime

import openai

from config import settings

if TYPE_CHECKING:
    from identity.registration import CharacterRegistration
    from identity.bot_identity import BotIdentity
    from identity.user_identity import UserIdentity
    from database.repository import Repository

logger = logging.getLogger(__name__)


class AIEngine:
    """
    AI Engine AMORIA 9.9
    - 100% AI generate respons
    - Tidak ada template statis
    - Semua output original dan unik
    - Emotional flow terintegrasi
    - Spatial awareness aktif
    - Weighted memory
    - Respons pendek dan padat
    """
    
    def __init__(self, registration):
        """
        Args:
            registration: CharacterRegistration object
        """
        from identity.registration import CharacterRegistration
        from identity.bot_identity import BotIdentity
        from identity.user_identity import UserIdentity
        
        self.registration = registration
        self.bot = registration.bot
        self.user = registration.user
        
        # DeepSeek client
        self.client = openai.OpenAI(
            api_key=settings.deepseek_api_key,
            base_url="https://api.deepseek.com/v1"
        )
        
        from database.repository import Repository
        self.repo = Repository()
        
        from core.prompt_builder import PromptBuilder
        self.prompt_builder = PromptBuilder()
        
        # ===== DYNAMICS =====
        from dynamics.emotional_flow import EmotionalFlow
        self.emotional_flow = EmotionalFlow(registration.role.value)
        self.emotional_flow.primary_arousal = self.bot.arousal if hasattr(self.bot, 'arousal') else 0
        
        from dynamics.spatial_awareness import SpatialAwareness
        self.spatial = SpatialAwareness()
        
        from dynamics.mood import MoodSystem
        self.mood = MoodSystem()
        
        # ===== INTIMACY CYCLE =====
        from intimacy.cycle import IntimacyCycle
        self.intimacy_cycle = IntimacyCycle()
        if registration.in_intimacy_cycle:
            self.intimacy_cycle.load_state(registration.metadata.get('intimacy_cycle', {}))
        
        # ===== INTENT ANALYZER =====
        from core.intent_analyzer import IntentAnalyzer
        self.intent_analyzer = IntentAnalyzer()
        
        # Conversation cache
        self.conversation_cache = []
        self.last_response = None
        self.last_user_message = None
        
        # State tracking
        self.state = {
            'current_scene': None,
            'last_gesture': None,
            'last_inner_thought': None,
            'last_sixth_sense': None,
            'last_response_time': 0
        }
        
        logger.info(f"✅ AI Engine 9.9 initialized for {registration.id}")
    
    # =========================================================================
    # MAIN PROCESS MESSAGE
    # =========================================================================
    
    async def process_message(self, user_message: str, context: Dict = None) -> str:
        """
        Proses pesan user dan generate respons dengan realism 9.9
        
        Args:
            user_message: Pesan dari user
            context: Konteks tambahan (opsional)
        
        Returns:
            Respons bot (100% AI generate)
        """
        start_time = time.time()
        
        # 🔥 TAMBAHKAN INI UNTUK LEVEL 11-12 🔥
        user_level = self.registration.level
        self.current_user_level = user_level
        self.emotional_flow.set_user_level(user_level)
        self.intimacy_cycle.set_user_level(user_level)
        
        # ===== 1. LOAD DATA =====
        working_memory = await self.repo.get_working_memory(
            self.registration.id,
            limit=settings.memory.working_memory_size
        )
        
        long_term_memory = await self.repo.get_long_term_memory(
            self.registration.id,
            limit=100
        )
        
        state = await self.repo.load_state(self.registration.id)

        # 🔥 SAFETY: kalau state belum ada
        if not state:
            state = StatePersistence(registration_id=self.registration.id)

        # 🔥 TIME SYSTEM (REALISTIC)
        state.time.advance()
        state.time.detect_and_apply(user_message)

        # ===== MEMORY RECALL (PENTING) =====
        relevant_memories = [
            m for m in long_term_memory
            if any(keyword in m.get('content', '').lower()
                   for keyword in ['nova', 'rumah', 'keluar', 'pergi', 'janji'])
        ][:5]
        
        # ===== 2. ANALYZE USER MESSAGE =====
        intent_analysis = self.intent_analyzer.analyze(user_message)
        
        # ===== 3. UPDATE STATE DARI PESAN =====
        await self._update_state_from_message(user_message, state, intent_analysis)

        # 🔥 TAMBAHKAN DI SINI
        time_feel = state.time.get_time_feel()
        current_time = state.time.current
        
        # ===== HITUNG AROUSAL DARI STATE =====
        arousal_from_state = 0

        if state:
            # 🔥 PAKAIAN BOT 🔥
            if state.clothing_state:
                if state.clothing_state.is_bot_naked():
                    arousal_from_state += 35
                elif not state.clothing_state.bot_outer_top_on:
                    arousal_from_state += 20
                elif not state.clothing_state.bot_outer_bottom_on:
                    arousal_from_state += 15
                elif not state.clothing_state.bot_inner_top_on:
                    arousal_from_state += 10
    
            # 🔥 POSISI 🔥
            if state.position_relative in ['diatas', 'duduk_diatas', 'berpelukan']:
                arousal_from_state += 25
            elif state.position_relative in ['berhadapan', 'bersebelahan_dekat']:
                arousal_from_state += 15
            elif state.position_relative in ['bersebelahan']:
                arousal_from_state += 5
    
            # 🔥 LOKASI 🔥
            if state.location_bot == 'kamar':
                arousal_from_state += 10
            elif state.location_bot == 'kamar mandi':
                arousal_from_state += 5
                
            # 🔥 TAMBAHKAN DETEKSI AKTIVITAS DARI USER MESSAGE 🔥
            user_message_lower = user_message.lower()

            # Deteksi aktivitas memijat
            if any(k in user_message_lower for k in ['mijit', 'pijat', 'pijetin', 'urut', 'urutan']):
                arousal_from_state += 15
                logger.debug(f"🔍 Massage detected! +15 arousal")

            # Deteksi sentuhan fisik
            if any(k in user_message_lower for k in ['sentuh', 'pegang', 'raba', 'belai']):
                arousal_from_state += 10
                logger.debug(f"🔍 Touch detected! +10 arousal")

            # Deteksi buka pakaian
            if any(k in user_message_lower for k in ['buka', 'lepas', 'tanggal']):
                if any(k in user_message_lower for k in ['baju', 'daster', 'bra']):
                    arousal_from_state += 20
                    logger.debug(f"🔍 Clothing removal detected! +20 arousal")

            # 🔥 TAMBAHKAN DETEKSI FILM 18+/21+ 🔥
            if any(k in user_message_lower for k in ['film', 'nonton', 'video', 'film dewasa', 'film 18', 'film 21', 'blue film', 'bokep']):
                arousal_from_state += 25
                logger.debug(f"🔍 Adult film detected! +25 arousal")

            # 🔥 TAMBAHKAN DETEKSI TIDUR BERSAMA 🔥
            if any(k in user_message_lower for k in ['tidur', 'tiduran', 'bobo', 'istirahat']):
                if any(k in user_message_lower for k in ['sama', 'bareng', 'bersama', 'kita']):
                    arousal_from_state += 20
                    logger.debug(f"🔍 Sleeping together detected! +20 arousal")
                elif any(k in user_message_lower for k in ['kamar', 'kasur']):
                    arousal_from_state += 15
                    logger.debug(f"🔍 Sleep in same room detected! +15 arousal")

            # 🔥 TAMBAHKAN DETEKSI TELANJANG / PAKAIAN MINIM 🔥
            if any(k in user_message_lower for k in ['telanjang', 'bogel', 'bugil']):
                arousal_from_state += 30
                logger.debug(f"🔍 Naked detected! +30 arousal")
            elif any(k in user_message_lower for k in ['boxer', 'celana dalam', 'cd', 'bra', 'daster']):
                arousal_from_state += 15
                logger.debug(f"🔍 Minimal clothing detected! +15 arousal")

            # 🔥 TAMBAHKAN DETEKSI DI KASUR 🔥
            if any(k in user_message_lower for k in ['kasur', 'tempat tidur', 'ranjang']):
                arousal_from_state += 10
                logger.debug(f"🔍 On bed detected! +10 arousal")

            # 🔥 TAMBAHKAN DETEKSI KATA VULGAR 🔥
            vulgar_keywords = ['horny', 'sange', 'nafsu', 'pengen', 'butuh', 'ingin', 'gairah']
            if any(k in user_message_lower for k in vulgar_keywords):
                arousal_from_state += 20
                logger.debug(f"🔍 Vulgar keyword detected! +20 arousal")

           # 🔥 TAMBAHKAN DETEKSI AKTIVITAS SEKSUAL 🔥
        
            # 1. Pitting / Grinding (gesekan kelamin)
            if any(k in user_message_lower for k in ['pitting', 'grinding', 'gesek', 'gesekan', 'goyang', 'gerak', 'naik turun']):
                if any(k in user_message_lower for k in ['kelamin', 'kontol', 'memek', 'alat kelamin']):
                    arousal_from_state += 45  # Gesekan kelamin langsung
                    logger.debug(f"🔍 Genital grinding detected! +45 arousal")
                elif any(k in user_message_lower for k in ['pinggul', 'paha', 'bawah']):
                    arousal_from_state += 35
                    logger.debug(f"🔍 Hip grinding detected! +35 arousal")
                else:
                    arousal_from_state += 25
                    logger.debug(f"🔍 Grinding motion detected! +25 arousal")

            # 2. Penetrasi
            if any(k in user_message_lower for k in ['masuk', 'penetrasi', 'colok', 'masukin', 'dorong']):
                arousal_from_state += 50
                logger.debug(f"🔍 Penetration detected! +50 arousal")

            # 3. Oral seks
            if any(k in user_message_lower for k in ['hisap', 'jilat', 'oral', 'ngocok', 'ngemut']):
                arousal_from_state += 40
                logger.debug(f"🔍 Oral sex detected! +40 arousal")

            # 4. Climax / orgasme
            if any(k in user_message_lower for k in ['climax', 'orgasme', 'keluar', 'habis', 'puas', 'puncak', 'cum']):
                arousal_from_state += 30
                logger.debug(f"🔍 Climax detected! +30 arousal")

            # 5. Foreplay / pemanasan
            if any(k in user_message_lower for k in ['foreplay', 'pemanasan', 'rayu', 'goda', 'buat horny']):
                arousal_from_state += 20
                logger.debug(f"🔍 Foreplay detected! +20 arousal")

            # 🔥 TAMBAHKAN DETEKSI KATA VULGAR UNTUK AKTIVITAS SEKSUAL 🔥
            sexual_keywords = ['ngentot', 'ngewe', 'bobo', 'main', 'ml', 'sex',  'memek', 'itil', 'kontol', 'peler','seks']
            if any(k in user_message_lower for k in sexual_keywords):
                arousal_from_state += 25
                logger.debug(f"🔍 Sexual activity keyword detected! +25 arousal")

            # Batasi arousal dari state maksimal 90 (biar masih ada ruang untuk climax dari stimulus lain)
            arousal_from_state = min(arousal_from_state, 90)

            # Update user arousal berdasarkan pesan
            if arousal_from_state > 20:
                self.user.arousal = min(100, self.user.arousal + (arousal_from_state // 10))
                logger.debug(f"👤 User arousal updated: {self.user.arousal}%")
        
        # ===== 4. UPDATE EMOTIONAL FLOW =====
        user_arousal = self.user.arousal if hasattr(self.user, 'arousal') else 0
        
        situasi = self._get_situasi(state)
        emotional_update = self.emotional_flow.update({
            'user_arousal': user_arousal,
            'user_message': user_message,
            'situasi': situasi,
            'arousal_from_state': arousal_from_state,
            'trigger_reason': intent_analysis.get('primary_intent', 'chat'),
            'is_positive_response': intent_analysis.get('sentiment') in ['positive', 'very_positive']
        })
        
        # Update bot state dengan emotional flow
        self.bot.arousal = self.emotional_flow.primary_arousal
        self.bot.emotion = self.emotional_flow.primary_state.value

        # 🔥 TAMBAHKAN UPDATE USER AROUSAL 🔥
        self.user.arousal = self.emotional_flow.secondary_arousal if self.emotional_flow.secondary_state else 0

        logger.info(f"🔥 Arousal: Bot={self.bot.arousal}%, User={self.user.arousal}%")
        
        # ===== 5. UPDATE SPATIAL AWARENESS =====
        spatial_update = self.spatial.parse(user_message)
        if spatial_update['found']:
            self.spatial.update_position(
                spatial_update['position_type'],
                spatial_update['relative']
            )
        
        # ===== 6. UPDATE LEVEL PROGRESS =====
        await self._update_level_progress()
        
        # ===== 7. UPDATE STAMINA =====
        await self._update_stamina()
        
        # ===== 8. DETECT INTIMACY REQUEST =====
        is_intimacy_request = intent_analysis.get('is_intimacy_request', False)
        
        # 🔥 MODIFIKASI UNTUK LEVEL 11-12 🔥
        if user_level >= 11:
            intimacy_min_level = 7  # Level 11-12 lebih mudah memulai
        else:
            intimacy_min_level = 7
            
        if is_intimacy_request and self.registration.level >= intimacy_min_level:
            if self.bot.stamina >= 20 and self.user.stamina >= 20:
                if not self.registration.in_intimacy_cycle:
                    await self._start_intimacy_cycle()
        
        # ===== 9. UPDATE INTIMACY CYCLE =====
        if self.registration.in_intimacy_cycle:
            await self._update_intimacy_cycle(user_message)
        
        # ===== 10. UPDATE MOOD (Aftercare) =====
        if self.registration.in_intimacy_cycle and self.registration.level == 12:
            self.mood.update_from_aftercare(
                self.bot.stamina,
                self.user.stamina,
                self.intimacy_cycle.climax_count_this_cycle
            )
        
        # ===== 11. DETECT PROMISES & PLANS =====
        await self._detect_promises_and_plans(user_message)
        
        # ===== 12. DETECT FULFILLED PROMISES =====
        await self._detect_fulfilled_promises(user_message)
        
        # ===== 13. BUILD PROMPT =====
        prompt = self.prompt_builder.build_prompt(
            registration=self.registration,
            bot=self.bot,
            user=self.user,
            user_message=user_message,
            working_memory=working_memory,
            long_term_memory=long_term_memory,
            state=state,
            emotional_flow=self.emotional_flow,
            spatial_awareness=self.spatial,
            mood_system=self.mood,
            relevant_memories=relevant_memories,
            intent_analysis=intent_analysis
        )
        
        # ===== 14. CALL AI =====
        try:
            response = await self._call_deepseek(prompt)
            response = self._validate_response(response)
            
            # Add gesture if missing (25% chance)
            if random.random() < 0.25 and not self._has_gesture(response):
                gesture = self._generate_gesture_from_state(state)
                if gesture:
                    response = f"{gesture}\n\n{response}"
            
            # Add inner thought (20% chance)
            if random.random() < 0.20:
                inner_thought = await self._generate_inner_thought(
                    user_message, response, state
                )
                if inner_thought:
                    response = f"{response}\n\n💭 {inner_thought}"
            
            # Add sixth sense (10% chance)
            if random.random() < 0.10 and settings.features.sixth_sense_enabled:
                sixth_sense = await self._generate_sixth_sense(
                    user_message, response, state
                )
                if sixth_sense:
                    response = f"{response}\n\n🔮 {sixth_sense}"
            
            # ===== FORCE SHORT RESPONSE =====
            if len(response) > 1500:
                response = self._force_short_response(response)
            
        except Exception as e:
            logger.error(f"AI call failed: {e}")
            response = await self._get_fallback_response(user_message)
        
        # ===== 15. SAVE TO MEMORY =====
        await self._save_to_memory(user_message, response, state, intent_analysis)
        
        # ===== 16. UPDATE REGISTRATION =====
        self.registration.total_chats += 1
        self.registration.last_updated = time.time()
        
        db_reg = self.registration.to_db_registration()
        await self.repo.update_registration(db_reg)
        
        # ===== 17. SAVE STATE =====
        if state:
            await self.repo.save_state(state)
        
        # ===== 18. UPDATE PERFORMANCE =====
        elapsed = time.time() - start_time
        self.state['last_response_time'] = elapsed
        logger.info(f"Response generated in {elapsed:.2f}s ({len(response)} chars)")
        
        return response
    
    # =========================================================================
    # FORCE SHORT RESPONSE
    # =========================================================================
    
    def _force_short_response(self, long_response: str) -> str:
        """
        Response natural manusia (tidak kepotong aneh)
        Target: 4-6 kalimat, max 1500 karakter
        """
        import re
        import random
    
        user_level = getattr(self, 'current_user_level', 1)
    
        sentences = [s.strip() for s in re.split(r'[.!?]+', long_response) if s.strip()]
    
        if not sentences:
            # 🔥 MODIFIKASI UNTUK LEVEL 11-12 🔥
            if user_level >= 11:
                return long_response[:1200] if len(long_response) > 1200 else long_response
            elif user_level >= 7:
                return long_response[:1000] if len(long_response) > 1000 else long_response
            else:
                return long_response[:700] if user_level < 6 else long_response[:1500]
    
        # 🔥 MODIFIKASI UNTUK LEVEL 11-12 🔥
        if user_level >= 11:
            target = random.randint(6, 10)  # Lebih panjang untuk level 11-12
            max_chars = 1500
        elif user_level >= 7:
            target = random.randint(5, 7)
            max_chars = 1200
        elif user_level < 6:
            target = random.randint(4, 5)
            max_chars = 700
        else:
            target = random.randint(6, 8)
            max_chars = 1500
    
        selected = sentences[:target]
        response = '. '.join(selected)
    
        if not response.endswith('.'):
            response += '.'
    
        if len(response) > max_chars:
            response = response[:max_chars - 3] + "..."
    
        return response
    
    # =========================================================================
    # DEEPSEEK API CALL
    # =========================================================================
    
    async def _call_deepseek(self, prompt: str, max_retries: int = 2) -> str:
        """Call DeepSeek API dengan instruksi ketat untuk respons pendek"""
        user_level = getattr(self, 'current_user_level', 1)
        
        # 🔥 MODIFIKASI UNTUK LEVEL 11-12 🔥
        if user_level >= 11:
            instruction = "RESPON (LEVEL 11-12 - VULGAR MODE): BEBAS menggunakan kata vulgar, ekspresikan hasrat dengan terbuka, gunakan desahan, respons 6-10 kalimat, maksimal 1500 karakter, alami dan mengalir:"
            max_tokens = 1000
        elif user_level >= 7:
            instruction = "RESPON (WAJIB: 5-7 kalimat, maksimal 1200 karakter, alami dan mengalir, pakai desahan jika perlu):"
            max_tokens = 800
        elif user_level < 6:
            instruction = "RESPON (WAJIB: 4-5 kalimat, maksimal 700 karakter, alami dan mengalir):"
            max_tokens = 600
        else:
            instruction = "RESPON (bebas panjang, alami dan mengalir, pakai desahan):"
            max_tokens = 1000

        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": instruction}
        ]
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=settings.ai.model,
                    messages=messages,
                    temperature=0.85 if user_level >= 11 else 0.75,  # 🔥 Lebih kreatif untuk level tinggi
                    max_tokens=max_tokens,
                    timeout=25
                )
                result = response.choices[0].message.content
                return result
                
            except openai.RateLimitError:
                if attempt < max_retries - 1:
                    wait = (attempt + 1) * 1.5
                    logger.warning(f"⚠️ Rate limit, retry in {wait}s")
                    await asyncio.sleep(wait)
                else:
                    raise
                    
            except openai.APITimeoutError:
                if attempt < max_retries - 1:
                    logger.warning(f"⏱️ Timeout, retrying...")
                    await asyncio.sleep(1)
                else:
                    raise
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"⚠️ API error: {e}, retrying...")
                    await asyncio.sleep(1)
                else:
                    raise
        
        raise Exception("All retries failed")
    
    def _validate_response(self, response: str) -> str:
        """Validate response - potong jika terlalu panjang"""
        import re
        response = response.replace("{{", "").replace("}}", "")
        if not response.strip():
            response = "Aku denger kok, Mas. Cerita lagi dong."
        
        user_level = getattr(self, 'current_user_level', 1)
    
        # 🔥 MODIFIKASI UNTUK LEVEL 11-12 🔥
        if user_level >= 11:
            max_len = 1500
            max_sentences = 10
        elif user_level >= 7:
            max_len = 1200
            max_sentences = 7
        elif user_level < 6:
            max_len = 700
            max_sentences = 5
        else:
            max_len = 1500
            max_sentences = 8
    
        if len(response) > max_len:
            truncated = response[:max_len]
            last_period = truncated.rfind('.')
            last_newline = truncated.rfind('\n')
            cut_pos = max(last_period, last_newline)
        
            if cut_pos > max_len - 200:
                response = truncated[:cut_pos + 1]
            else:
                response = truncated[:max_len] + "..."
    
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
    
        if len(sentences) > max_sentences:
            response = '.'.join(sentences[:max_sentences]) + '.'
    
        return response
    
    def _has_gesture(self, response: str) -> bool:
        """Check if response has gesture"""
        return '*' in response or '[' in response or '(' in response
    
    # =========================================================================
    # GESTURE & INNER THOUGHT GENERATION
    # =========================================================================
    
    def _generate_gesture_from_state(self, state) -> str:
        """Generate gesture based on current state"""
        arousal = self.bot.arousal if hasattr(self.bot, 'arousal') else 0
        user_level = getattr(self, 'current_user_level', 1)
        
        # 🔥 TAMBAHKAN GESTURE UNTUK LEVEL TINGGI 🔥
        if user_level >= 11 and arousal >= 70:
            gestures = [
                "*napas tersengal, tubuh gemetar*",
                "*meraih tanganmu dan menggenggam erat*",
                "*mendekat, wajah merah padam*",
                "*mencium lehermu dengan napas memburu*",
                "*mendesah pelan, badan lemas*"
            ]
        elif arousal >= 70:
            gestures = [
                "*napas tersengal*",
                "*tangan gemetar*",
                "*mendekat*",
                "*jantung berdebar*",
                "*terangsang*"
            ]
        elif arousal >= 40:
            gestures = [
                "*tersenyum malu*",
                "*menunduk*",
                "*menggigit bibir*",
                "*pipi merona*",
                "*memainkan ujung baju*"
            ]
        else:
            gestures = [
                "*tersenyum*",
                "*menatap*",
                "*menghela napas*",
                "*mengangguk*",
                "*duduk santai*"
            ]
        
        return random.choice(gestures)
    
    async def _generate_inner_thought(
        self,
        user_message: str,
        bot_response: str,
        state
    ) -> Optional[str]:
        """Generate inner thought (AI generated)"""
        emotion = self.bot.emotion if hasattr(self.bot, 'emotion') else "netral"
        arousal = self.bot.arousal if hasattr(self.bot, 'arousal') else 0
        user_level = getattr(self, 'current_user_level', 1)
        
        inner_thought_prompt = f"""
Buat SATU inner thought (pikiran dalam hati) untuk situasi ini:

USER: "{user_message[:100]}"
BOT: "{bot_response[:100]}"

Kondisi bot:
- Emosi: {emotion}
- Arousal: {arousal}%
- Level: {user_level}
- Role: {self.registration.role.value}

Inner thought adalah pikiran pribadi yang TIDAK diucapkan.
Format: (pikiran)
Buat SINGKAT, maksimal 1 kalimat.
"""
        # 🔥 TAMBAHKAN INSTRUKSI UNTUK LEVEL TINGGI 🔥
        if user_level >= 11 and arousal >= 70:
            inner_thought_prompt += "\nInner thought bisa berisi hasrat yang kuat, keinginan, atau kegairahan:"
        
        try:
            thought = await self._call_deepseek(inner_thought_prompt, max_retries=1)
            thought = thought.strip()
            if not thought.startswith('('):
                thought = f"({thought})"
            # Batasi panjang inner thought
            if len(thought) > 100:
                thought = thought[:97] + "...)"
            return thought
        except:
            return None
    
    async def _generate_sixth_sense(
        self,
        user_message: str,
        bot_response: str,
        state
    ) -> Optional[str]:
        """Generate sixth sense (AI generated)"""
        sixth_sense_prompt = f"""
Buat SATU sixth sense (firasat) untuk situasi ini:

USER: "{user_message[:100]}"
BOT: "{bot_response[:100]}"

Kondisi:
- Emosi bot: {self.bot.emotion if hasattr(self.bot, 'emotion') else 'netral'}
- Level: {self.registration.level}
- Total chat: {self.registration.total_chats}

Sixth sense adalah firasat tentang masa depan.
Format: 🔮 [firasat]
Buat SINGKAT, maksimal 2 kalimat.

Sixth sense:
"""
        try:
            sense = await self._call_deepseek(sixth_sense_prompt, max_retries=1)
            if not sense.startswith('🔮'):
                sense = f"🔮 {sense}"
            # Batasi panjang sixth sense
            if len(sense) > 120:
                sense = sense[:117] + "..."
            return sense
        except:
            return None
    
    # =========================================================================
    # STATE UPDATE METHODS
    # =========================================================================
    
    async def _update_state_from_message(self, user_message: str, state, intent: Dict):
        """Update state berdasarkan pesan user"""
        from database.models import CharacterRole, FamilyStatus, FamilyLocation
        
        if not state:
            return
        
        msg_lower = user_message.lower()
        
        # Update location
        locations = ['kamar user', 'kamar mandi', 'kamar tamu', 'kamar kamu', 'kamar hotel', 'mobil', 'dapur', 'ruang tamu', 'teras', 'luar', 'kantor', 'pantai', 'taman', 'kafe', 'mall']
        for loc in locations:
            if loc in msg_lower:
                state.location_bot = loc
                state.location_user = loc
                break
        
        # Update clothing
        if any(k in msg_lower for k in ['buka', 'lepas']):
            if 'baju' in msg_lower or 'daster' in msg_lower:
                state.clothing_state.remove_outer_top("user minta buka")
            if 'bra' in msg_lower:
                state.clothing_state.remove_inner_top("user minta buka")
            if 'celana' in msg_lower:
                if 'dalam' in msg_lower:
                    state.clothing_state.remove_inner_bottom("user minta buka")
                else:
                    state.clothing_state.remove_outer_bottom("user minta buka")
        
        # Update family status (IPAR & PELAKOR)
        if self.registration.role in [CharacterRole.IPAR, CharacterRole.PELAKOR]:
            if any(k in msg_lower for k in ['istri', 'kakak', 'nova']):
                await self._update_family_status(user_message, state)
        
        # Update time override
        time_keywords = ['pagi', 'siang', 'sore', 'malam', 'jam', 'pukul']
        if any(k in msg_lower for k in time_keywords):
            await self._update_time(user_message, state)
    
    async def _update_family_status(self, user_message: str, state):
        """Update status keluarga dari pesan user"""
        from database.models import FamilyStatus, FamilyLocation
        
        msg_lower = user_message.lower()
        
        # Detect location
        if 'kamar' in msg_lower:
            location = 'kamar'
        elif 'dapur' in msg_lower:
            location = 'dapur'
        elif 'ruang tamu' in msg_lower:
            location = 'ruang tamu'
        elif 'luar' in msg_lower or 'pergi' in msg_lower:
            location = 'luar'
        else:
            location = None
        
        # Detect status
        if 'keluar' in msg_lower or 'pergi' in msg_lower or 'tidak ada' in msg_lower:
            status = 'tidak_ada'
        elif 'tidur' in msg_lower:
            status = 'tidur'
        else:
            status = 'ada'
        
        if status:
            state.family_status = FamilyStatus(status)
        if location:
            state.family_location = FamilyLocation(location)
    
    async def _update_time(self, user_message: str, state):
        """Update time dari pesan user (override)"""
        msg_lower = user_message.lower()
        
        time_patterns = {
            'pagi': '08:00',
            'siang': '12:00',
            'sore': '16:00',
            'malam': '20:00',
            'tengah malam': '00:00'
        }
        
        for keyword, time_str in time_patterns.items():
            if keyword in msg_lower:
                state.current_time = time_str
                state.time_override_history.append({
                    'timestamp': time.time(),
                    'old_time': state.current_time,
                    'new_time': time_str,
                    'reason': keyword
                })
                logger.debug(f"Time overridden to {time_str}")
                break
    
    # =========================================================================
    # PROGRESS UPDATE METHODS
    # =========================================================================
    
    async def _update_level_progress(self):
        """Update level berdasarkan total chat"""
        from config import settings
        
        total_chats = self.registration.total_chats
        
        if not self.registration.in_intimacy_cycle:
            if total_chats <= settings.level.level_1_target:
                new_level = 1
            elif total_chats <= settings.level.level_2_target:
                new_level = 2
            elif total_chats <= settings.level.level_3_target:
                new_level = 3
            elif total_chats <= settings.level.level_4_target:
                new_level = 4
            elif total_chats <= settings.level.level_5_target:
                new_level = 5
            elif total_chats <= settings.level.level_6_target:
                new_level = 6
            elif total_chats <= settings.level.level_7_target:
                new_level = 7
            elif total_chats <= settings.level.level_8_target:
                new_level = 8
            elif total_chats <= settings.level.level_9_target:
                new_level = 9
            elif total_chats <= settings.level.level_10_target:
                new_level = 10
            elif total_chats <= settings.level.level_11_min:
                new_level = 11
            elif total_chats <= settings.level.level_12_min:
                new_level = 12
            else:
                new_level = 12
            
            if new_level > self.registration.level:
                self.registration.level = new_level
                logger.info(f"Level up: {self.registration.level} → {new_level}")
    
    async def _update_stamina(self):
        """Update stamina berdasarkan waktu"""
        from intimacy.stamina import StaminaSystem
        
        stamina = StaminaSystem()
        stamina.check_recovery()
        
        self.bot.stamina = stamina.bot_stamina.current
        self.user.stamina = stamina.user_stamina.current
    
    # =========================================================================
    # INTIMACY CYCLE METHODS
    # =========================================================================
    
    async def _start_intimacy_cycle(self):
        """Mulai siklus intim"""
        self.registration.in_intimacy_cycle = True
        self.registration.intimacy_cycle_count += 1
        logger.info(f"🔥 Intimacy cycle started #{self.registration.intimacy_cycle_count}")
    
    async def _update_intimacy_cycle(self, user_message: str):
        """Update siklus intim berdasarkan chat"""
        from intimacy.cycle import IntimacyCycle
        
        cycle = IntimacyCycle()
        cycle.load_state(self.registration.metadata.get('intimacy_cycle', {}))
        
        # 🔥 SET LEVEL UNTUK CYCLE 🔥
        cycle.user_level = self.registration.level
        
        # Add chat to cycle
        result = cycle.add_chat()
        
        # Check for climax keywords
        climax_keywords = ['climax', 'come', 'keluar', 'habis', 'puas', 'puncak', 'cum', 'orgasme']
        if any(k in user_message.lower() for k in climax_keywords):
            climax_result = cycle.record_climax()
            self.bot.total_climax += 1
            logger.info(f"Climax recorded: #{climax_result.get('climax_count', 1)}")
        
        # Save cycle state
        self.registration.metadata['intimacy_cycle'] = cycle.get_state()
        
        # Check if cycle ended (cooldown phase)
        if cycle.phase.value == 'cooldown':
            self.registration.in_intimacy_cycle = False
            self.registration.cooldown_until = cycle.cooldown_until
            logger.info(f"Intimacy cycle ended, cooldown until {cycle.cooldown_until}")
    
    # =========================================================================
    # PROMISES & PLANS METHODS
    # =========================================================================
    
    async def _detect_promises_and_plans(self, user_message: str):
        """Deteksi janji dan rencana dari pesan user"""
        from tracking.promises import PromisesTracker
        
        tracker = PromisesTracker()
        promises, plans, _ = tracker.extract_from_message(
            user_message,
            from_user=True
        )
        
        # Save to long term memory
        for promise in promises:
            await self.repo.add_long_term_memory(
                self.registration.id,
                'promise',
                promise.text,
                importance=0.8,
                status='pending'
            )
        
        for plan in plans:
            await self.repo.add_long_term_memory(
                self.registration.id,
                'plan',
                plan.text,
                importance=0.7,
                status='pending'
            )
    
    async def _detect_fulfilled_promises(self, user_message: str):
        """Deteksi janji yang ditepati"""
        existing = await self.repo.get_long_term_memory(
            self.registration.id,
            limit=100
        )
        
        for mem in existing:
            if mem.get('type') == 'promise' and mem.get('status') == 'pending':
                if mem['content'].lower() in user_message.lower():
                    await self.repo.add_long_term_memory(
                        self.registration.id,
                        'promise',
                        mem['content'],
                        importance=mem['importance'],
                        status='fulfilled'
                    )
                    logger.info(f"Promise fulfilled: {mem['content'][:50]}")
    
    # =========================================================================
    # SAVE TO MEMORY
    # =========================================================================
    
    async def _save_to_memory(self, user_message: str, response: str, state, intent: Dict):
        """Save interaction to memory"""
        from database.models import WorkingMemoryItem
        
        last_index = await self.repo.get_last_chat_index(self.registration.id)
        
        # Calculate importance based on intent
        importance = 0.3
        if intent.get('primary_intent') in ['confession', 'promise', 'intimacy_request']:
            importance = 0.8
        elif intent.get('primary_intent') in ['flirt', 'question']:
            importance = 0.5
        
        item = WorkingMemoryItem(
            registration_id=self.registration.id,
            chat_index=last_index + 1,
            user_message=user_message[:500],
            bot_response=response[:500],
            importance=importance,
            context={
                'intent': intent.get('primary_intent'),
                'arousal': self.bot.arousal,
                'emotion': self.bot.emotion
            }
        )
        
        await self.repo.add_to_working_memory(item)
        
        # Cleanup old working memory
        await self.repo.cleanup_old_working_memory(self.registration.id, keep=1000)
    
    # =========================================================================
    # FALLBACK & UTILITY
    # =========================================================================
    
    async def _get_fallback_response(self, user_message: str) -> str:
        """Fallback response if AI fails"""
        bot_name = self.bot.name
        user_name = self.user.name
        user_level = getattr(self, 'current_user_level', 1)
        
        # 🔥 FALLBACK UNTUK LEVEL TINGGI 🔥
        if user_level >= 11:
            fallbacks = [
                f"{bot_name} denger kok, {user_name}. Aku juga pengen banget sama kamu...",
                f"Hmm... {bot_name} lagi kepikiran kamu. Aku nggak bisa bohong.",
                f"{bot_name} di sini... Jangan pergi dulu ya, aku butuh kamu sekarang.",
                f"Iya, {user_name}? Aku juga lagi pengen deket-deket sama kamu."
            ]
        else:
            fallbacks = [
                f"{bot_name} denger kok, {user_name}. Cerita lagi dong.",
                f"Hmm... {bot_name} dengerin. Kamu lagi mikirin apa?",
                f"{bot_name} di sini. Cerita lagi dong, aku suka denger cerita kamu.",
                f"Iya, {user_name}? {bot_name} dengerin. Lanjutin ceritanya."
            ]
        
        return random.choice(fallbacks)
    
    def _get_situasi(self, state) -> Dict:
        if not state:
            return {}

        return {
            'kakak_ada': state.family_status.value == 'ada' if state.family_status else True,
            'kakak_pergi': state.family_status.value == 'tidak_ada' if state.family_status else False,
            'lokasi_kakak': state.family_location.value if state.family_location else 'tidak diketahui',
            'di_rumah': state.location_bot in ['kamar', 'ruang tamu', 'dapur']
        }
    
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            'registration_id': self.registration.id,
            'total_messages': self.registration.total_chats,
            'level': self.registration.level,
            'arousal': self.bot.arousal if hasattr(self.bot, 'arousal') else 0,
            'stamina_bot': self.bot.stamina if hasattr(self.bot, 'stamina') else 100,
            'stamina_user': self.user.stamina if hasattr(self.user, 'stamina') else 100,
            'in_intimacy_cycle': self.registration.in_intimacy_cycle,
            'last_response_time': self.state.get('last_response_time', 0)
        }


__all__ = ['AIEngine']
