# threesome/manager.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Threesome Manager
=============================================================================
"""

import time
import uuid
import logging
from typing import Dict, List, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ThreesomeType(str, Enum):
    HTS_HTS = "hts_hts"
    FWB_FWB = "fwb_fwb"
    HTS_FWB = "hts_fwb"


class ThreesomeStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ThreesomeManager:
    """Manager untuk sesi threesome"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict] = {}
        self.user_sessions: Dict[int, str] = {}
        self.combinations: Dict[str, Dict] = {}
        logger.info("✅ ThreesomeManager initialized")
    
    async def get_possible_combinations(self, user_id: int) -> List[Dict]:
        """Dapatkan kombinasi threesome yang mungkin"""
        return list(self.combinations.values())
    
    async def get_combination(self, combo_id: str) -> Optional[Dict]:
        """Dapatkan kombinasi berdasarkan ID"""
        return self.combinations.get(combo_id)
    
    async def create_threesome(self, user_id: int, participant1: Dict, participant2: Dict) -> Dict:
        """Buat session threesome baru"""
        session_id = f"3some_{user_id}_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        
        session = {
            'session_id': session_id,
            'user_id': user_id,
            'type': self._determine_type(participant1, participant2),
            'status': ThreesomeStatus.PENDING,
            'created_at': time.time(),
            'participants': [
                {
                    'id': participant1.get('hts_id') or participant1.get('fwb_id'),
                    'role': participant1['role'],
                    'type': participant1.get('type', 'hts'),
                    'name': participant1.get('bot_name', participant1['role'].title()),
                },
                {
                    'id': participant2.get('hts_id') or participant2.get('fwb_id'),
                    'role': participant2['role'],
                    'type': participant2.get('type', 'hts'),
                    'name': participant2.get('bot_name', participant2['role'].title()),
                }
            ],
            'total_messages': 0,
            'climax_count': 0,
            'aftercare_needed': False
        }
        
        self.active_sessions[session_id] = session
        logger.info(f"🎭 Created threesome session: {session_id}")
        return session
    
    def _determine_type(self, p1: Dict, p2: Dict) -> ThreesomeType:
        type1 = p1.get('type', 'hts')
        type2 = p2.get('type', 'hts')
        
        if type1 == 'hts' and type2 == 'hts':
            return ThreesomeType.HTS_HTS
        elif type1 == 'fwb' and type2 == 'fwb':
            return ThreesomeType.FWB_FWB
        return ThreesomeType.HTS_FWB
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        return self.active_sessions.get(session_id)
    
    async def get_user_active_session(self, user_id: int) -> Optional[Dict]:
        session_id = self.user_sessions.get(user_id)
        if session_id:
            return self.active_sessions.get(session_id)
        return None
    
    async def start_session(self, session_id: str) -> Dict:
        session = self.active_sessions.get(session_id)
        if not session:
            return {'success': False, 'error': 'Session not found'}
        
        if session['status'] != ThreesomeStatus.PENDING:
            return {'success': False, 'error': f'Session already {session["status"]}'}
        
        session['status'] = ThreesomeStatus.ACTIVE
        session['started_at'] = time.time()
        self.user_sessions[session['user_id']] = session_id
        
        return {'success': True, 'pattern': 'both_respond'}
    
    async def cancel_session(self, session_id: str) -> Dict:
        session = self.active_sessions.get(session_id)
        if not session:
            return {'success': False, 'error': 'Session not found'}
        
        session['status'] = ThreesomeStatus.CANCELLED
        session['cancelled_at'] = time.time()
        
        if session['user_id'] in self.user_sessions:
            del self.user_sessions[session['user_id']]
        
        return {'success': True}
    
    async def record_climax(self, session_id: str) -> Dict:
        session = self.active_sessions.get(session_id)
        if not session:
            return {'success': False, 'error': 'Session not found'}
        
        session['climax_count'] += len(session['participants'])
        session['aftercare_needed'] = session['climax_count'] >= 3
        
        return {'success': True, 'session': session}


__all__ = ['ThreesomeManager', 'ThreesomeType', 'ThreesomeStatus']
