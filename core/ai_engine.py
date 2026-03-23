# core/ai_engine.py
import time
import logging
import openai
from config import settings

logger = logging.getLogger(__name__)


class AIEngine:
    def __init__(self, registration):
        self.registration = registration
        self.bot = registration.bot
        self.user = registration.user
        
        # FALLBACK: Jika get_full_prompt tidak ada
        if not hasattr(self.bot, 'get_full_prompt'):
            self.bot.get_full_prompt = lambda: f"Nama: {self.bot.name}\nRole: {self.bot.role.value}"
        
        self.client = openai.OpenAI(
            api_key=settings.deepseek_api_key,
            base_url="https://api.deepseek.com/v1"
        )
        
        from database.repository import Repository
        self.repo = Repository()
        
        from core.prompt_builder import PromptBuilder
        self.prompt_builder = PromptBuilder()
    
    async def process_message(self, user_message: str, context: dict = None) -> str:
        try:
            working_memory = await self.repo.get_working_memory(self.registration.id, limit=1000)
            long_term_memory = await self.repo.get_long_term_memory(self.registration.id, limit=100)
            state = await self.repo.load_state(self.registration.id)
            
            prompt = self.prompt_builder.build_prompt(
                registration=self.registration, bot=self.bot, user=self.user,
                user_message=user_message, working_memory=working_memory,
                long_term_memory=long_term_memory, state=state,
                is_intimacy_cycle=self.registration.in_intimacy_cycle,
                intimacy_cycle_count=self.registration.intimacy_cycle_count,
                level=self.registration.level
            )
            
            response = await self._call_ai(prompt)
            
            # Save to memory
            await self.repo.add_to_working_memory(
                self.registration.id, user_message, response,
                {'level': self.registration.level}
            )
            
            self.registration.total_chats += 1
            await self.repo.update_registration(self.registration.to_db_registration())
            
            return response
            
        except Exception as e:
            logger.error(f"AI error: {e}")
            return f"{self.bot.name} denger kok, Mas. Cerita lagi dong."
    
    async def _call_ai(self, prompt: str) -> str:
        messages = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": "RESPON:"}
        ]
        resp = self.client.chat.completions.create(
            model=settings.ai.model,
            messages=messages,
            temperature=settings.ai.temperature,
            max_tokens=settings.ai.max_tokens
        )
        return resp.choices[0].message.content


__all__ = ['AIEngine']
