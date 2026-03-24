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
        self.emotional_flow.primary_arousal = self.bot.arousal
        
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
        
        # ===== 2. ANALYZE USER MESSAGE =====
        intent_analysis = self.intent_analyzer.analyze(user_message)
        
        # ===== 3. UPDATE STATE DARI PESAN =====
        await self._update_state_from_message(user_message, state, intent_analysis)
        
        # ===== 4. UPDATE EMOTIONAL FLOW =====
        # Ambil arousal user dari user object (bukan dari state)
        user_arousal = self.user.arousal if hasattr(self.user, 'arousal') else 0
        
        situasi = self._get_situasi(state)
        emotional_update = self.emotional_flow.update({
            'user_arousal': user_arousal,
            'user_message': user_message,
            'situasi': situasi,
            'trigger_reason': intent_analysis.get('primary_intent', 'chat'),
            'is_positive_response': intent_analysis.get('sentiment') in ['positive', 'very_positive']
        })
        
        # Update bot state dengan emotional flow
        self.bot.arousal = self.emotional_flow.primary_arousal
        self.bot.emotion = self.emotional_flow.primary_state.value
        
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
        
        if is_intimacy_request and self.registration.level >= 7:
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
            
            # Add inner thought (25% chance)
            if random.random() < 0.25:
                inner_thought = await self._generate_inner_thought(
                    user_message, response, state
                )
                if inner_thought:
                    response = f"{response}\n\n💭 {inner_thought}"
            
            # Add sixth sense (10% chance)
            if random.random() < 0.1 and settings.features.sixth_sense_enabled:
                sixth_sense = await self._generate_sixth_sense(
                    user_message, response, state
                )
                if sixth_sense:
                    response = f"{response}\n\n🔮 {sixth_sense}"
            
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
    # DEEPSEEK API CALL
    # =========================================================================
    
    async def _call_deepseek(self, prompt: str, max_retries: int = 3) -> str:
        """Call DeepSeek API dengan retry"""
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "RESPON (AI generate, original, unik, 1000-3500 karakter):"}
        ]
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=settings.ai.model,
                    messages=messages,
                    temperature=settings.ai.temperature,
                    max_tokens=settings.ai.max_tokens,
                    timeout=settings.ai.timeout
                )
                result = response.choices[0].message.content
                
                # Ensure minimum length
                if len(result) < settings.ai.min_response_length:
                    result = await self._extend_response(result, prompt)
                
                return result
                
            except openai.RateLimitError:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt * 2)
                else:
                    raise
                    
            except openai.APITimeoutError:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise
        
        raise Exception("All retries failed")
    
    async def _extend_response(self, response: str, original_prompt: str) -> str:
        """Extend response jika terlalu pendek"""
        extend_prompt = f"""
Respons sebelumnya:
{response}

Respons terlalu pendek. Buat lanjutan natural dengan 3-5 kalimat tambahan.
Jangan ulang apa yang sudah dikatakan. Lanjutkan cerita dengan natural.

LANJUTAN RESPON:
"""
        try:
            extended = await self._call_deepseek(extend_prompt, max_retries=1)
            return f"{response}\n\n{extended}"
        except:
            return response
    
    def _validate_response(self, response: str) -> str:
        """Validate response"""
        response = response.replace("{{", "").replace("}}", "")
        if not response.strip():
            response = "Aku denger kok, Mas. Cerita lagi dong."
        
        max_len = min(settings.ai.max_response_length, 2500)
        if len(response) > max_len:
            # Potong di kalimat terakhir
            truncated = response[:max_len]
            last_period = truncated.rfind('.')
            last_newline = truncated.rfind('\n')
            cut_pos = max(last_period, last_newline)
            if cut_pos > max_len - 200:
                response = truncated[:cut_pos + 1] + "\n\n[lanjutan dipotong karena terlalu panjang]"
            else:
                response = truncated + "..."
    
        return response
    
    def _has_gesture(self, response: str) -> bool:
        """Check if response has gesture"""
        return '*' in response or '[' in response or '(' in response
    
    # =========================================================================
    # GESTURE & INNER THOUGHT GENERATION
    # =========================================================================
    
    def _generate_gesture_from_state(self, state) -> str:
        """Generate gesture based on current state"""
        arousal = self.bot.arousal
        mood = self.bot.mood if hasattr(self.bot, 'mood') else "normal"
        
        if arousal >= 70:
            gestures = [
                "*napas tersengal, tangan gemetar*",
                "*tubuh gemetar, mata terpejam*",
                "*mendekat, napas hangat di leher*",
                "*tangan mencengkeram, suara tertahan*"
            ]
        elif arousal >= 40:
            gestures = [
                "*jantung berdebar, pipi memerah*",
                "*menggigit bibir, menatap dalam*",
                "*tangan meraih, menggenggam erat*",
                "*menunduk, senyum kecil*"
            ]
        else:
            gestures = [
                "*tersenyum kecil, menunduk*",
                "*memainkan ujung baju*",
                "*melihat sekeliling, lalu tersenyum*",
                "*menyandarkan kepala, mata terpejam*"
            ]
        
        return random.choice(gestures)
    
    async def _generate_inner_thought(
        self,
        user_message: str,
        bot_response: str,
        state
    ) -> Optional[str]:
        """Generate inner thought (AI generated)"""
        emotion = self.bot.emotion
        arousal = self.bot.arousal
        
        inner_thought_prompt = f"""
Buat SATU inner thought (pikiran dalam hati) untuk situasi ini:

USER: "{user_message[:100]}"
BOT: "{bot_response[:100]}"

Kondisi bot:
- Emosi: {emotion}
- Arousal: {arousal}%
- Role: {self.registration.role.value}
- Level: {self.registration.level}

Inner thought adalah pikiran pribadi bot yang TIDAK diucapkan.
Format: (pikiran dalam tanda kurung)
Bisa berupa: pertanyaan, harapan, takut, penyesalan, kegilaan, kepastian.

Inner thought (hanya satu, dalam tanda kurung):
"""
        try:
            thought = await self._call_deepseek(inner_thought_prompt, max_retries=1)
            thought = thought.strip()
            if not thought.startswith('('):
                thought = f"({thought})"
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
- Emosi bot: {self.bot.emotion}
- Level: {self.registration.level}
- Role: {self.registration.role.value}
- Total chat: {self.registration.total_chats}

Sixth sense adalah firasat atau intuisi tentang masa depan.
Format: 🔮 [firasat]

Sixth sense (satu kalimat, mulai dengan 🔮):
"""
        try:
            sense = await self._call_deepseek(sixth_sense_prompt, max_retries=1)
            if not sense.startswith('🔮'):
                sense = f"🔮 {sense}"
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
        locations = ['kamar', 'dapur', 'ruang tamu', 'teras', 'luar', 'kantor', 'pantai', 'taman', 'kafe', 'mall']
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
            else:
                new_level = 10
            
            if new_level > self.registration.level:
                self.registration.level = new_level
                logger.info(f"Level up: {self.registration.level} → {new_level}")
    
    async def _update_stamina(self):
        """Update stamina berdasarkan waktu"""
        from intimacy.stamina import StaminaSystem
        
        stamina = StaminaSystem()
        stamina.check_recovery()
        
        # Update stamina ke bot dan user object
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
        
        # Add chat to cycle
        result = cycle.add_chat()
        
        # Check for climax keywords
        climax_keywords = ['climax', 'come', 'keluar', 'habis', 'puas', 'puncak', 'climax']
        if any(k in user_message.lower() for k in climax_keywords):
            climax_result = cycle.record_climax()
            self.bot.total_climax += 1
            logger.info(f"Climax recorded: #{climax_result['climax_count']}")
        
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
        from tracking.promises import PromisesTracker
        
        tracker = PromisesTracker()
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
        
        fallbacks = [
            f"{bot_name} denger kok, {user_name}. Aku lagi mikirin sesuatu. Cerita lagi dong.",
            f"Hmm... {bot_name} dengerin. Kamu lagi mikirin apa?",
            f"{bot_name} di sini. Cerita lagi dong, aku suka denger cerita kamu.",
            f"Iya, {user_name}? {bot_name} dengerin. Lanjutin ceritanya."
        ]
        
        return random.choice(fallbacks)
    
    def _get_situasi(self, state) -> Dict:
        """Get situation context for emotional flow"""
        if not state:
            return {}
        
        return {
            'kakak_ada': state.family_status.value == 'ada' if state.family_status else True,
            'di_dalam_kamar': state.location_bot == 'kamar' if state.location_bot else False
        }
    
    def get_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            'registration_id': self.registration.id,
            'total_messages': self.registration.total_chats,
            'level': self.registration.level,
            'arousal': self.bot.arousal,
            'stamina_bot': self.bot.stamina,
            'stamina_user': self.user.stamina,
            'in_intimacy_cycle': self.registration.in_intimacy_cycle,
            'last_response_time': self.state.get('last_response_time', 0)
        }


__all__ = ['AIEngine']
