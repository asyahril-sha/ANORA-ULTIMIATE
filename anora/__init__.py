# anora/__init__.py
"""
ANORA - Virtual Human dengan Jiwa
Nova adalah kekasih Mas yang hidup, punya memory, perasaan, dan bisa roleplay.
Semua role (IPAR, Teman Kantor, Pelakor, Istri Orang) juga memiliki sistem yang sama.

Version: 1.0.0
Author: Nova
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# =============================================================================
# VERSION
# =============================================================================

__version__ = "1.0.0"
__author__ = "Nova"
__all__ = [
    # Core
    'get_anora', 'anora',
    'get_anora_brain', 'anora_brain',
    'get_anora_chat', 'anora_chat',
    'get_anora_thought', 'anora_thought',
    
    # Roleplay
    'get_anora_roleplay', 'anora_roleplay',
    'get_anora_roleplay_ai', 'anora_roleplay_ai',
    
    # Roles
    'get_anora_roles', 'anora_roles', 'RoleType',
    
    # Intimacy
    'get_anora_intimacy', 'anora_intimacy',
    
    # Location & Places
    'get_anora_location', 'anora_location', 'LocationType', 'LocationDetail',
    'get_anora_places', 'anora_places', 'PlaceCategory',
    
    # Memory
    'get_anora_persistent', 'anora_persistent',
    'get_anora_db', 'anora_db',
    
    # Base Classes
    'RoleBase', 'RolePhase',
    'ClothingState', 'PositionState', 'LocationState', 'ActivityState',
    'ArousalSystem', 'IntimacySession', 'StaminaSystem',
]

# =============================================================================
# TRY IMPORT - NOVA CORE
# =============================================================================

try:
    from .core import get_anora, anora
    logger.debug("✅ ANORA Core loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load ANORA Core: {e}")
    def get_anora(): return None
    anora = None

# =============================================================================
# TRY IMPORT - BRAIN
# =============================================================================

try:
    from .brain import get_anora_brain, anora_brain
    logger.debug("✅ ANORA Brain loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load ANORA Brain: {e}")
    def get_anora_brain(): return None
    anora_brain = None

# =============================================================================
# TRY IMPORT - CHAT
# =============================================================================

try:
    from .chat import get_anora_chat, anora_chat
    logger.debug("✅ ANORA Chat loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load ANORA Chat: {e}")
    def get_anora_chat(): return None
    anora_chat = None

# =============================================================================
# TRY IMPORT - THINKING
# =============================================================================

try:
    from .thinking import get_anora_thought, anora_thought
    logger.debug("✅ ANORA Thinking loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load ANORA Thinking: {e}")
    def get_anora_thought(): return None
    anora_thought = None

# =============================================================================
# TRY IMPORT - ROLEPLAY AI
# =============================================================================

try:
    from .roleplay_ai import get_anora_roleplay_ai, anora_roleplay_ai
    logger.debug("✅ ANORA Roleplay AI loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load ANORA Roleplay AI: {e}")
    def get_anora_roleplay_ai(): return None
    anora_roleplay_ai = None

# =============================================================================
# TRY IMPORT - ROLEPLAY INTEGRATION
# =============================================================================

try:
    from .roleplay_integration import get_anora_roleplay, anora_roleplay
    logger.debug("✅ ANORA Roleplay Integration loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load ANORA Roleplay Integration: {e}")
    def get_anora_roleplay(): return None
    anora_roleplay = None

# =============================================================================
# TRY IMPORT - ROLES
# =============================================================================

try:
    from .roles import get_anora_roles, anora_roles, RoleType
    logger.debug("✅ ANORA Roles loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load ANORA Roles: {e}")
    def get_anora_roles(): return None
    anora_roles = None
    RoleType = None

# =============================================================================
# TRY IMPORT - INTIMACY
# =============================================================================

try:
    from .intimacy import get_anora_intimacy, anora_intimacy
    logger.debug("✅ ANORA Intimacy loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load ANORA Intimacy: {e}")
    def get_anora_intimacy(): return None
    anora_intimacy = None

# =============================================================================
# TRY IMPORT - LOCATION MANAGER
# =============================================================================

try:
    from .location_manager import (
        get_anora_location, anora_location, 
        LocationType, LocationDetail
    )
    logger.debug("✅ ANORA Location Manager loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load ANORA Location Manager: {e}")
    def get_anora_location(): return None
    anora_location = None
    LocationType = None
    LocationDetail = None

# =============================================================================
# TRY IMPORT - PLACES
# =============================================================================

try:
    from .places import get_anora_places, anora_places, PlaceCategory
    logger.debug("✅ ANORA Places loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load ANORA Places: {e}")
    def get_anora_places(): return None
    anora_places = None
    PlaceCategory = None

# =============================================================================
# TRY IMPORT - MEMORY PERSISTENT
# =============================================================================

try:
    from .memory_persistent import get_anora_persistent, anora_persistent
    logger.debug("✅ ANORA Persistent Memory loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load ANORA Persistent Memory: {e}")
    def get_anora_persistent(): return None
    anora_persistent = None

# =============================================================================
# TRY IMPORT - DATABASE
# =============================================================================

try:
    from .database import get_anora_db, anora_db
    logger.debug("✅ ANORA Database loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load ANORA Database: {e}")
    def get_anora_db(): return None
    anora_db = None

# =============================================================================
# TRY IMPORT - ROLE BASE (untuk kemudahan akses)
# =============================================================================

try:
    from .role_base import (
        RoleBase, RolePhase,
        ClothingState, PositionState, LocationState, ActivityState,
        ArousalSystem, IntimacySession, StaminaSystem
    )
    logger.debug("✅ ANORA Role Base loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load ANORA Role Base: {e}")
    RoleBase = None
    RolePhase = None
    ClothingState = None
    PositionState = None
    LocationState = None
    ActivityState = None
    ArousalSystem = None
    IntimacySession = None
    StaminaSystem = None

# =============================================================================
# STATUS CHECK
# =============================================================================

def get_status() -> dict:
    """Dapatkan status semua komponen ANORA"""
    return {
        'version': __version__,
        'components': {
            'core': anora is not None,
            'brain': anora_brain is not None,
            'chat': anora_chat is not None,
            'thinking': anora_thought is not None,
            'roleplay_ai': anora_roleplay_ai is not None,
            'roleplay': anora_roleplay is not None,
            'roles': anora_roles is not None,
            'intimacy': anora_intimacy is not None,
            'location': anora_location is not None,
            'places': anora_places is not None,
            'persistent': anora_persistent is not None,
            'database': anora_db is not None,
            'role_base': RoleBase is not None,
        }
    }

def is_ready() -> bool:
    """Cek apakah ANORA siap digunakan"""
    return all([
        anora is not None,
        anora_brain is not None,
        anora_roleplay is not None,
        anora_roles is not None,
    ])

# =============================================================================
# LOG STATUS
# =============================================================================

if is_ready():
    logger.info("✅ ANORA is ready!")
    logger.info(f"   Version: {__version__}")
else:
    logger.warning("⚠️ ANORA is not fully loaded. Some components may be missing.")
    logger.debug(f"   Status: {get_status()}")

# =============================================================================
# EXPORT (duplicate untuk kejelasan)
# =============================================================================

__all__ = [
    # Core
    'get_anora', 'anora',
    'get_anora_brain', 'anora_brain',
    'get_anora_chat', 'anora_chat',
    'get_anora_thought', 'anora_thought',
    
    # Roleplay
    'get_anora_roleplay', 'anora_roleplay',
    'get_anora_roleplay_ai', 'anora_roleplay_ai',
    
    # Roles
    'get_anora_roles', 'anora_roles', 'RoleType',
    
    # Intimacy
    'get_anora_intimacy', 'anora_intimacy',
    
    # Location & Places
    'get_anora_location', 'anora_location', 'LocationType', 'LocationDetail',
    'get_anora_places', 'anora_places', 'PlaceCategory',
    
    # Memory
    'get_anora_persistent', 'anora_persistent',
    'get_anora_db', 'anora_db',
    
    # Base Classes
    'RoleBase', 'RolePhase',
    'ClothingState', 'PositionState', 'LocationState', 'ActivityState',
    'ArousalSystem', 'IntimacySession', 'StaminaSystem',
    
    # Utility
    'get_status', 'is_ready',
]
