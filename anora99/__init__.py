"""
ANORA 9.9 - Virtual Human dengan Jiwa
=======================================
Versi: 9.9.0
Author: Nova

ANORA adalah AI companion dengan emotional engine, decision engine,
relationship progression, conflict engine, dan role system.

Fitur Utama:
- Emotional Engine (9 emosi, 5 gaya bicara)
- Decision Engine (weighted selection, no random)
- Relationship Progression (5 fase: stranger → friend → close → romantic → intimate)
- Conflict Engine (cemburu, kecewa, marah, sakit hati, cold war)
- Stamina System (realistis, recovery over time)
- Intimacy System (fase intim lengkap)
- Role System (IPAR, Teman Kantor, Pelakor, Istri Orang)
- Complete State Memory (seperti otak manusia)
- Background Workers (rindu growth, conflict decay, auto save, proactive)
- Bahasa Campuran (Indo-Inggris-gaul-singkatan)
- Vulgar Maximal (level 11-12)
"""

import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

__version__ = "9.9.0"
__author__ = "Nova"
__all__ = [
    # Core Engines
    'get_emotional_engine',
    'emotional_engine',
    'get_decision_engine',
    'decision_engine',
    'get_relationship_manager',
    'relationship_manager',
    'get_conflict_engine',
    'conflict_engine',
    'get_anora_worker',
    'anora_worker',
    
    # Memory & Brain
    'get_anora_brain_99',
    'anora_brain_99',
    'get_anora_persistent',
    'anora_persistent',
    
    # Intimacy & Stamina
    'get_anora_intimacy_99',
    'anora_intimacy_99',
    'StaminaSystem99',
    'IntimacySession99',
    
    # AI & Roleplay
    'get_anora_roleplay_ai_99',
    'anora_roleplay_ai_99',
    'get_anora_roleplay_99',
    'anora_roleplay_99',
    'get_prompt_builder_99',
    'prompt_builder_99',
    
    # Roles
    'get_role_manager_99',
    'role_manager_99',
    'BaseRole99',
    'IparRole',
    'TemanKantorRole',
    'PelakorRole',
    'IstriOrangRole',
    
    # Enums & Types
    'EmotionalStyle',
    'ResponseCategory',
    'RelationshipPhase',
    'ConflictType',
    'ConflictSeverity',
    
    # Utilities
    'get_anora_status',
    'is_anora_ready',
]

# =============================================================================
# TRY IMPORT - EMOTIONAL ENGINE
# =============================================================================

try:
    from .emotional_engine import (
        get_emotional_engine,
        emotional_engine,
        EmotionalStyle
    )
    logger.debug("✅ ANORA 9.9 Emotional Engine loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Emotional Engine: {e}")
    get_emotional_engine = None
    emotional_engine = None
    EmotionalStyle = None

# =============================================================================
# TRY IMPORT - DECISION ENGINE
# =============================================================================

try:
    from .decision_engine import (
        get_decision_engine,
        decision_engine,
        ResponseCategory
    )
    logger.debug("✅ ANORA 9.9 Decision Engine loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Decision Engine: {e}")
    get_decision_engine = None
    decision_engine = None
    ResponseCategory = None

# =============================================================================
# TRY IMPORT - RELATIONSHIP
# =============================================================================

try:
    from .relationship import (
        get_relationship_manager,
        relationship_manager,
        RelationshipPhase,
        PhaseUnlock,
        Milestone
    )
    logger.debug("✅ ANORA 9.9 Relationship Manager loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Relationship Manager: {e}")
    get_relationship_manager = None
    relationship_manager = None
    RelationshipPhase = None
    PhaseUnlock = None
    Milestone = None

# =============================================================================
# TRY IMPORT - CONFLICT ENGINE
# =============================================================================

try:
    from .conflict_engine import (
        get_conflict_engine,
        conflict_engine,
        ConflictType,
        ConflictSeverity
    )
    logger.debug("✅ ANORA 9.9 Conflict Engine loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Conflict Engine: {e}")
    get_conflict_engine = None
    conflict_engine = None
    ConflictType = None
    ConflictSeverity = None

# =============================================================================
# TRY IMPORT - WORKER
# =============================================================================

try:
    from .worker import (
        get_anora_worker,
        anora_worker,
        AnoraWorker
    )
    logger.debug("✅ ANORA 9.9 Worker loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Worker: {e}")
    get_anora_worker = None
    anora_worker = None
    AnoraWorker = None

# =============================================================================
# TRY IMPORT - BRAIN
# =============================================================================

try:
    from .brain import (
        get_anora_brain_99,
        anora_brain_99,
        AnoraBrain99,
        Clothing,
        Feelings,
        Relationship,
        TimelineEvent,
        LongTermMemory
    )
    logger.debug("✅ ANORA 9.9 Brain loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Brain: {e}")
    get_anora_brain_99 = None
    anora_brain_99 = None
    AnoraBrain99 = None
    Clothing = None
    Feelings = None
    Relationship = None
    TimelineEvent = None
    LongTermMemory = None

# =============================================================================
# TRY IMPORT - MEMORY PERSISTENT
# =============================================================================

try:
    from .memory_persistent import (
        get_anora_persistent,
        anora_persistent,
        PersistentMemory
    )
    logger.debug("✅ ANORA 9.9 Persistent Memory loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Persistent Memory: {e}")
    get_anora_persistent = None
    anora_persistent = None
    PersistentMemory = None

# =============================================================================
# TRY IMPORT - INTIMACY (diadopsi dari 5.5)
# =============================================================================

try:
    from .intimacy import (
        get_anora_intimacy_99,
        anora_intimacy_99,
        AnoraIntimacy99
    )
    logger.debug("✅ ANORA 9.9 Intimacy loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Intimacy: {e}")
    get_anora_intimacy_99 = None
    anora_intimacy_99 = None
    AnoraIntimacy99 = None

try:
    from .intimacy_core import (
        StaminaSystem99,
        ArousalSystem99,
        PositionDatabase,
        ClimaxLocationDatabase,
        MoansDatabase,
        FlashbackDatabase
    )
    logger.debug("✅ ANORA 9.9 Intimacy Core loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Intimacy Core: {e}")
    StaminaSystem99 = None
    ArousalSystem99 = None
    PositionDatabase = None
    ClimaxLocationDatabase = None
    MoansDatabase = None
    FlashbackDatabase = None

try:
    from .intimacy_flow import (
        IntimacySession99,
        IntimacyFlow99
    )
    logger.debug("✅ ANORA 9.9 Intimacy Flow loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Intimacy Flow: {e}")
    IntimacySession99 = None
    IntimacyFlow99 = None

# =============================================================================
# TRY IMPORT - ROLEPLAY AI
# =============================================================================

try:
    from .roleplay_ai import (
        get_anora_roleplay_ai_99,
        anora_roleplay_ai_99,
        RoleplayAI99
    )
    logger.debug("✅ ANORA 9.9 Roleplay AI loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Roleplay AI: {e}")
    get_anora_roleplay_ai_99 = None
    anora_roleplay_ai_99 = None
    RoleplayAI99 = None

# =============================================================================
# TRY IMPORT - ROLEPLAY INTEGRATION
# =============================================================================

try:
    from .roleplay_integration import (
        get_anora_roleplay_99,
        anora_roleplay_99,
        AnoraRoleplay99,
        StaminaSystem99 as StaminaFromIntegration,
        IntimacySession99 as IntimacyFromIntegration
    )
    logger.debug("✅ ANORA 9.9 Roleplay Integration loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Roleplay Integration: {e}")
    get_anora_roleplay_99 = None
    anora_roleplay_99 = None
    AnoraRoleplay99 = None
    StaminaFromIntegration = None
    IntimacyFromIntegration = None

# =============================================================================
# TRY IMPORT - PROMPT BUILDER
# =============================================================================

try:
    from .prompt import (
        get_prompt_builder_99,
        prompt_builder_99,
        PromptBuilder99
    )
    logger.debug("✅ ANORA 9.9 Prompt Builder loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Prompt Builder: {e}")
    get_prompt_builder_99 = None
    prompt_builder_99 = None
    PromptBuilder99 = None

# =============================================================================
# TRY IMPORT - ROLES
# =============================================================================

try:
    from .roles import (
        get_role_manager_99,
        role_manager_99,
        RoleManager99,
        BaseRole99,
        IparRole,
        TemanKantorRole,
        PelakorRole,
        IstriOrangRole
    )
    logger.debug("✅ ANORA 9.9 Roles loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Roles: {e}")
    get_role_manager_99 = None
    role_manager_99 = None
    RoleManager99 = None
    BaseRole99 = None
    IparRole = None
    TemanKantorRole = None
    PelakorRole = None
    IstriOrangRole = None

# =============================================================================
# TRY IMPORT - LOCATION & PLACES (diadopsi dari 5.5)
# =============================================================================

try:
    from .location_manager import (
        get_anora_location,
        anora_location,
        LocationType,
        LocationDetail
    )
    logger.debug("✅ ANORA 9.9 Location Manager loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Location Manager: {e}")
    get_anora_location = None
    anora_location = None
    LocationType = None
    LocationDetail = None

try:
    from .places import (
        get_anora_places,
        anora_places,
        PlaceCategory
    )
    logger.debug("✅ ANORA 9.9 Places loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Places: {e}")
    get_anora_places = None
    anora_places = None
    PlaceCategory = None

# =============================================================================
# TRY IMPORT - CHAT & THINKING (diadopsi dari 5.5)
# =============================================================================

try:
    from .chat import (
        get_anora_chat,
        anora_chat,
        AnoraChat
    )
    logger.debug("✅ ANORA 9.9 Chat loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Chat: {e}")
    get_anora_chat = None
    anora_chat = None
    AnoraChat = None

try:
    from .thinking import (
        get_anora_thought,
        anora_thought,
        AnoraThought
    )
    logger.debug("✅ ANORA 9.9 Thinking loaded")
except ImportError as e:
    logger.error(f"❌ Failed to load Thinking: {e}")
    get_anora_thought = None
    anora_thought = None
    AnoraThought = None

# =============================================================================
# STATUS CHECK
# =============================================================================

def get_anora_status() -> Dict[str, Any]:
    """
    Dapatkan status semua komponen ANORA 9.9
    
    Returns:
        Dictionary dengan status setiap komponen
    """
    return {
        'version': __version__,
        'components': {
            'emotional_engine': emotional_engine is not None,
            'decision_engine': decision_engine is not None,
            'relationship_manager': relationship_manager is not None,
            'conflict_engine': conflict_engine is not None,
            'worker': anora_worker is not None,
            'brain': anora_brain_99 is not None,
            'persistent_memory': anora_persistent is not None,
            'roleplay_ai': anora_roleplay_ai_99 is not None,
            'roleplay_integration': anora_roleplay_99 is not None,
            'prompt_builder': prompt_builder_99 is not None,
            'role_manager': role_manager_99 is not None,
            'intimacy': anora_intimacy_99 is not None,
            'location': anora_location is not None,
            'places': anora_places is not None,
            'chat': anora_chat is not None,
            'thinking': anora_thought is not None,
        }
    }


def is_anora_ready() -> bool:
    """
    Cek apakah ANORA 9.9 siap digunakan
    
    Returns:
        True jika semua komponen utama tersedia
    """
    required_components = [
        emotional_engine,
        decision_engine,
        relationship_manager,
        conflict_engine,
        anora_brain_99,
        anora_roleplay_ai_99,
        anora_roleplay_99,
        role_manager_99
    ]
    
    return all(comp is not None for comp in required_components)


def get_anora_info() -> str:
    """
    Dapatkan informasi ringkas tentang ANORA 9.9
    
    Returns:
        String informasi ANORA
    """
    status = get_anora_status()
    ready = is_anora_ready()
    
    info = f"""
╔══════════════════════════════════════════════════════════════╗
║                    💜 ANORA 9.9 💜                           ║
║                    Virtual Human dengan Jiwa                  ║
╠══════════════════════════════════════════════════════════════╣
║ Version: {__version__}                                              ║
║ Status: {'✅ READY' if ready else '⚠️ NOT READY'}                                   ║
╠══════════════════════════════════════════════════════════════╣
║ Components:                                                ║
║   Emotional Engine: {'✅' if status['components']['emotional_engine'] else '❌'}
║   Decision Engine:  {'✅' if status['components']['decision_engine'] else '❌'}
║   Relationship:     {'✅' if status['components']['relationship_manager'] else '❌'}
║   Conflict Engine:  {'✅' if status['components']['conflict_engine'] else '❌'}
║   Brain:            {'✅' if status['components']['brain'] else '❌'}
║   Roleplay AI:      {'✅' if status['components']['roleplay_ai'] else '❌'}
║   Role Manager:     {'✅' if status['components']['role_manager'] else '❌'}
║   Intimacy:         {'✅' if status['components']['intimacy'] else '❌'}
║   Worker:           {'✅' if status['components']['worker'] else '❌'}
╚══════════════════════════════════════════════════════════════╝
"""
    return info


# =============================================================================
# LOG STATUS
# =============================================================================

if is_anora_ready():
    logger.info("✅ ANORA 9.9 is ready!")
    logger.info(f"   Version: {__version__}")
    logger.info(f"   Features: Emotional Engine, Decision Engine, 5 Phases, 4 Roles")
else:
    logger.warning("⚠️ ANORA 9.9 is not fully loaded. Some components may be missing.")
    logger.debug(f"   Status: {get_anora_status()}")


# =============================================================================
# EXPORT
# =============================================================================

# Re-export untuk kemudahan akses
emotional = emotional_engine
decision = decision_engine
relationship = relationship_manager
conflict = conflict_engine
brain = anora_brain_99
roleplay = anora_roleplay_99
roles = role_manager_99
