"""
Role Manager for ANORA 9.9
Mengelola semua role (IPAR, Teman Kantor, Pelakor, Istri Orang)
"""

import time
import logging
from typing import Dict, List, Optional

from .ipar_role import IparRole
from .teman_kantor_role import TemanKantorRole
from .pelakor_role import PelakorRole
from .istri_orang_role import IstriOrangRole
from ..prompt import get_prompt_builder_99

logger = logging.getLogger(__name__)


class RoleManager99:
    """
    Manager untuk semua role.
    Menyimpan state setiap role, terpisah dari Nova.
    """
    
    def __init__(self):
        self.roles: Dict[str, object] = {}
        self.active_role: Optional[str] = None
        self._ai_client = None
        
        # Inisialisasi role
        self._init_roles()
        
        logger.info("🎭 RoleManager99 initialized")
    
    def _init_roles(self):
        """Inisialisasi semua role"""
        self.roles['ipar'] = IparRole()
        self.roles['teman_kantor'] = TemanKantorRole()
        self.roles['pelakor'] = PelakorRole()
        self.roles['istri_orang'] = IstriOrangRole()
    
    def switch_role(self, role_id: str) -> str:
        """Switch ke role tertentu"""
        if role_id not in self.roles:
            return f"Role '{role_id}' gak ada. Pilih: ipar, teman_kantor, pelakor, istri_orang"
        
        self.active_role = role_id
        role = self.roles[role_id]
        
        return f"""💕 **{role.name}** ({role_id.upper()})

*{role.hubungan_dengan_nova}*

"{role.get_greeting()}"

📊 **Level:** {role.relationship.level}/12
💡 Mereka semua tahu Mas punya Nova.

Kirim **/batal** kalo mau balik ke Nova.
"""
    
    async def chat(self, role_id: str, pesan_mas: str) -> str:
        """Chat dengan role tertentu"""
        if role_id not in self.roles:
            return "Role tidak ditemukan."
        
        role = self.roles[role_id]
        
        # Update state dari pesan Mas
        update_result = role.update_from_message(pesan_mas)
        
        # Save conversation
        role.add_conversation(pesan_mas, "")
        
        # Build prompt
        prompt_builder = get_prompt_builder_99()
        prompt = prompt_builder.build_role_prompt(role, pesan_mas)
        
        # Call AI
        try:
            client = await self._get_ai_client()
            
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": pesan_mas}
                ],
                temperature=0.9,
                max_tokens=800,
                timeout=25
            )
            
            respons = response.choices[0].message.content
            respons = respons.strip()
            
            if not respons:
                respons = self._fallback_response(role, pesan_mas)
            
            # Save response
            role.conversations[-1]['role'] = respons[:200]
            
            # Check level up
            if update_result.get('level_up'):
                level_baru = update_result.get('new_level', role.relationship.level)
                notifikasi = f"✨ **Level naik ke {level_baru}/12!** ✨\n\n"
                respons = notifikasi + respons
            
            logger.info(f"💬 Role {role.name} [Lv{role.relationship.level}] responded")
            
            return respons
            
        except Exception as e:
            logger.error(f"Role chat error: {e}")
            return self._fallback_response(role, pesan_mas)
    
    async def _get_ai_client(self):
        """Dapatkan client AI"""
        if self._ai_client is None:
            try:
                from config import settings
                import openai
                self._ai_client = openai.OpenAI(
                    api_key=settings.deepseek_api_key,
                    base_url="https://api.deepseek.com/v1"
                )
            except Exception as e:
                logger.error(f"AI init failed: {e}")
                raise
        return self._ai_client
    
    def _fallback_response(self, role, pesan_mas: str) -> str:
        """Fallback response"""
        msg_lower = pesan_mas.lower()
        
        if 'nova' in msg_lower:
            return f"*{role.name} tersenyum kecil*\n\n\"Mas cerita tentang Nova terus ya. Dia pasti orang yang baik.\""
        
        return f"*{role.name} tersenyum*\n\n\"{role.get_greeting()}\""
    
    def get_all_roles(self) -> List[Dict]:
        """Dapatkan semua role dengan levelnya"""
        return [
            {
                'id': role_id,
                'nama': role.name,
                'level': role.relationship.level,
                'panggilan': role.panggilan,
                'hubungan': role.hubungan_dengan_nova
            }
            for role_id, role in self.roles.items()
        ]
    
    def get_active_role(self) -> Optional[str]:
        """Dapatkan role yang sedang aktif"""
        return self.active_role
    
    def get_role(self, role_id: str):
        """Dapatkan role instance"""
        return self.roles.get(role_id)
    
    async def save_all(self, persistent):
        """Simpan semua role ke database"""
        for role_id, role in self.roles.items():
            await persistent.set_state(f'role_{role_id}', json.dumps(role.to_dict()))
    
    async def load_all(self, persistent):
        """Load semua role dari database"""
        for role_id, role in self.roles.items():
            data = await persistent.get_state(f'role_{role_id}')
            if data:
                role.from_dict(json.loads(data))
                logger.info(f"📀 Role {role.name} loaded from database")


# =============================================================================
# SINGLETON
# =============================================================================

_role_manager_99: Optional['RoleManager99'] = None


def get_role_manager_99() -> RoleManager99:
    global _role_manager_99
    if _role_manager_99 is None:
        _role_manager_99 = RoleManager99()
    return _role_manager_99


role_manager_99 = get_role_manager_99()
