# config.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA 9.9 - Virtual Human dengan Jiwa
Konfigurasi Utama - Complete with Error Handling
=============================================================================
"""

import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import Field, field_validator, ConfigDict
from pydantic_settings import BaseSettings

# Setup basic logging for config loading
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# DATABASE SETTINGS
# =============================================================================
class DatabaseSettings(BaseSettings):
    """Konfigurasi database"""
    model_config = ConfigDict(env_prefix="DB_", extra="ignore")
    
    type: str = Field("sqlite", alias="DB_TYPE")
    path: Path = Field(Path("data/amoria.db"), alias="DB_PATH")
    pool_size: int = Field(5, alias="DB_POOL_SIZE")
    timeout: int = Field(30, alias="DB_TIMEOUT")
    
    @property
    def url(self) -> str:
        return f"sqlite+aiosqlite:///{self.path}"
    
    @field_validator('path', mode='before')
    @classmethod
    def validate_path(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v


# =============================================================================
# AI SETTINGS
# =============================================================================
class AISettings(BaseSettings):
    """Konfigurasi AI DeepSeek"""
    model_config = ConfigDict(env_prefix="AI_", extra="ignore")
    
    temperature: float = Field(0.95, alias="AI_TEMPERATURE")
    max_tokens: int = Field(2000, alias="AI_MAX_TOKENS")
    timeout: int = Field(45, alias="AI_TIMEOUT")
    model: str = Field("deepseek-chat", alias="AI_MODEL")
    
    min_response_length: int = Field(300, alias="MIN_RESPONSE_LENGTH")
    max_response_length: int = Field(2000, alias="MAX_RESPONSE_LENGTH")
    min_sentences: int = Field(2, alias="MIN_SENTENCES")
    max_sentences: int = Field(8, alias="MAX_SENTENCES")
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError(f'Temperature must be between 0 and 2, got {v}')
        return v


# =============================================================================
# MEMORY SETTINGS
# =============================================================================
class MemorySettings(BaseSettings):
    """Konfigurasi memory system"""
    model_config = ConfigDict(env_prefix="", extra="ignore")
    
    working_memory_size: int = Field(1000, alias="WORKING_MEMORY_SIZE")
    long_term_memory_size: int = Field(10000, alias="LONG_TERM_MEMORY_SIZE")
    emotional_memory_size: int = Field(500, alias="EMOTIONAL_MEMORY_SIZE")
    memory_dir: Path = Field(Path("data/memory"), alias="MEMORY_DIR")
    
    @field_validator('memory_dir', mode='before')
    @classmethod
    def validate_memory_dir(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v


# =============================================================================
# LEVEL & INTIMACY SETTINGS
# =============================================================================
class LevelSettings(BaseSettings):
    """Konfigurasi level system untuk Realism 9.9"""
    model_config = ConfigDict(env_prefix="", extra="ignore")
    
    # Level 1-10 (sekali seumur registrasi)
    level_1_target: int = Field(7, alias="LEVEL_1_TARGET")
    level_2_target: int = Field(15, alias="LEVEL_2_TARGET")
    level_3_target: int = Field(25, alias="LEVEL_3_TARGET")
    level_4_target: int = Field(35, alias="LEVEL_4_TARGET")
    level_5_target: int = Field(45, alias="LEVEL_5_TARGET")
    level_6_target: int = Field(55, alias="LEVEL_6_TARGET")
    level_7_target: int = Field(65, alias="LEVEL_7_TARGET")
    level_8_target: int = Field(75, alias="LEVEL_8_TARGET")
    level_9_target: int = Field(85, alias="LEVEL_9_TARGET")
    level_10_target: int = Field(95, alias="LEVEL_10_TARGET")
    
    # Level 11-12 (siklus berulang)
    level_11_min: int = Field(96, alias="LEVEL_11_MIN")
    level_11_max: int = Field(125, alias="LEVEL_11_MAX")
    level_12_min: int = Field(126, alias="LEVEL_12_MIN")
    level_12_max: int = Field(135, alias="LEVEL_12_MAX")
    
    @property
    def level_targets(self) -> Dict[int, int]:
        return {
            1: self.level_1_target,
            2: self.level_2_target,
            3: self.level_3_target,
            4: self.level_4_target,
            5: self.level_5_target,
            6: self.level_6_target,
            7: self.level_7_target,
            8: self.level_8_target,
            9: self.level_9_target,
            10: self.level_10_target,
        }
    
    @property
    def level_names(self) -> Dict[int, str]:
        return {
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


# =============================================================================
# STAMINA SETTINGS
# =============================================================================
class StaminaSettings(BaseSettings):
    """Konfigurasi stamina system"""
    model_config = ConfigDict(env_prefix="STAMINA_", extra="ignore")
    
    bot_start: int = Field(100, alias="BOT_START")
    user_start: int = Field(100, alias="USER_START")
    drop_first: int = Field(30, alias="DROP_FIRST")
    drop_second: int = Field(50, alias="DROP_SECOND")
    drop_third: int = Field(70, alias="DROP_THIRD")
    recovery_per_hour: int = Field(5, alias="RECOVERY_PER_HOUR")
    
    @property
    def drops(self) -> Dict[int, int]:
        return {
            1: self.drop_first,
            2: self.drop_second,
            3: self.drop_third,
        }


# =============================================================================
# SESSION & IDENTITY SETTINGS
# =============================================================================
class IdentitySettings(BaseSettings):
    """Konfigurasi multi-identity system"""
    model_config = ConfigDict(env_prefix="", extra="ignore")
    
    session_dir: Path = Field(Path("data/sessions"), alias="SESSION_DIR")
    retention_days: int = Field(30, alias="SESSION_RETENTION_DAYS")
    max_characters_per_role: int = Field(10, alias="MAX_CHARACTERS_PER_ROLE")
    
    @field_validator('session_dir', mode='before')
    @classmethod
    def validate_session_dir(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v


# =============================================================================
# FEATURE SETTINGS
# =============================================================================
class FeatureSettings(BaseSettings):
    """Feature toggles untuk Realism 9.9"""
    model_config = ConfigDict(env_prefix="", extra="ignore")
    
    sexual_content_enabled: bool = Field(True, alias="SEXUAL_CONTENT_ENABLED")
    threesome_enabled: bool = Field(True, alias="THREESOME_ENABLED")
    public_risk_enabled: bool = Field(True, alias="PUBLIC_RISK_ENABLED")
    aftercare_enabled: bool = Field(True, alias="AFTERCARE_ENABLED")
    flashback_enabled: bool = Field(True, alias="FLASHBACK_ENABLED")
    sixth_sense_enabled: bool = Field(True, alias="SIXTH_SENSE_ENABLED")
    
    # New features for 9.9
    weighted_memory_enabled: bool = Field(True, alias="WEIGHTED_MEMORY_ENABLED")
    emotional_bias_enabled: bool = Field(True, alias="EMOTIONAL_BIAS_ENABLED")
    spatial_awareness_enabled: bool = Field(True, alias="SPATIAL_AWARENESS_ENABLED")


# =============================================================================
# BACKUP SETTINGS
# =============================================================================
class BackupSettings(BaseSettings):
    """Konfigurasi backup system"""
    model_config = ConfigDict(env_prefix="BACKUP_", extra="ignore")
    
    enabled: bool = Field(True, alias="ENABLED")
    interval: int = Field(3600, alias="INTERVAL")
    retention_days: int = Field(7, alias="RETENTION_DAYS")
    backup_dir: Path = Field(Path("data/backups"), alias="DIR")
    s3_bucket: Optional[str] = Field(None, alias="S3_BUCKET")
    
    @field_validator('backup_dir', mode='before')
    @classmethod
    def validate_backup_dir(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v


# =============================================================================
# LOGGING SETTINGS
# =============================================================================
class LoggingSettings(BaseSettings):
    """Konfigurasi logging untuk Railway"""
    model_config = ConfigDict(env_prefix="LOG_", extra="ignore")
    
    level: str = Field("INFO", alias="LEVEL")
    log_dir: Path = Field(Path("data/logs"), alias="DIR")
    json_format: bool = Field(True, alias="JSON_FORMAT")
    railway_mode: bool = Field(True, alias="RAILWAY_MODE")
    
    @field_validator('log_dir', mode='before')
    @classmethod
    def validate_log_dir(cls, v):
        if isinstance(v, str):
            return Path(v)
        return v
    
    @field_validator('level')
    @classmethod
    def validate_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Log level must be one of {valid_levels}, got {v}')
        return v.upper()


# =============================================================================
# WEBHOOK SETTINGS
# =============================================================================
class WebhookSettings(BaseSettings):
    """Konfigurasi webhook untuk Railway"""
    model_config = ConfigDict(env_prefix="", extra="ignore")
    
    port: int = Field(8080, alias="PORT")
    path: str = Field("/webhook", alias="WEBHOOK_PATH")
    secret_token: Optional[str] = Field(None, alias="WEBHOOK_SECRET")
    railway_domain: Optional[str] = Field(None, alias="RAILWAY_PUBLIC_DOMAIN")
    railway_static_url: Optional[str] = Field(None, alias="RAILWAY_STATIC_URL")
    
    @property
    def url(self) -> Optional[str]:
        if self.railway_domain:
            return f"https://{self.railway_domain}{self.path}"
        if self.railway_static_url:
            return f"https://{self.railway_static_url}{self.path}"
        return None
    
    @property
    def is_railway(self) -> bool:
        return bool(self.railway_domain or self.railway_static_url)


# =============================================================================
# MONITORING SETTINGS
# =============================================================================
class MonitoringSettings(BaseSettings):
    """Konfigurasi monitoring untuk Railway"""
    model_config = ConfigDict(env_prefix="MONITORING_", extra="ignore")
    
    enabled: bool = Field(True, alias="ENABLED")
    metrics_port: int = Field(9090, alias="METRICS_PORT")
    health_check_interval: int = Field(30, alias="HEALTH_CHECK_INTERVAL")
    slow_operation_threshold: float = Field(5.0, alias="SLOW_OPERATION_THRESHOLD")


# =============================================================================
# MAIN SETTINGS CLASS
# =============================================================================
class Settings(BaseSettings):
    """
    AMORIA 9.9 - Virtual Human dengan Jiwa
    Main Settings with Railway Support
    """
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # ===== API KEYS (WAJIB) =====
    deepseek_api_key: str = Field(..., alias="DEEPSEEK_API_KEY")
    telegram_token: str = Field(..., alias="TELEGRAM_TOKEN")
    admin_id: int = Field(..., alias="ADMIN_ID")
    
    # ===== COMPONENT SETTINGS =====
    database: DatabaseSettings = DatabaseSettings()
    ai: AISettings = AISettings()
    memory: MemorySettings = MemorySettings()
    level: LevelSettings = LevelSettings()
    stamina: StaminaSettings = StaminaSettings()
    identity: IdentitySettings = IdentitySettings()
    features: FeatureSettings = FeatureSettings()
    backup: BackupSettings = BackupSettings()
    logging: LoggingSettings = LoggingSettings()
    webhook: WebhookSettings = WebhookSettings()
    monitoring: MonitoringSettings = MonitoringSettings()
    
    # ===== BASE DIRECTORY =====
    base_dir: Path = Path(__file__).parent
    
    # ===== VALIDATORS =====
    @field_validator('deepseek_api_key')
    @classmethod
    def validate_deepseek_key(cls, v):
        if not v or v == "your_deepseek_api_key_here":
            raise ValueError("DEEPSEEK_API_KEY tidak boleh kosong. Set di Railway Variables atau .env")
        if len(v) < 10:
            raise ValueError("DEEPSEEK_API_KEY seems invalid (too short)")
        return v
    
    @field_validator('telegram_token')
    @classmethod
    def validate_telegram_token(cls, v):
        if not v or v == "your_telegram_bot_token_here":
            raise ValueError("TELEGRAM_TOKEN tidak boleh kosong. Set di Railway Variables atau .env")
        if not v.replace(':', '').replace('-', '').isalnum():
            raise ValueError("TELEGRAM_TOKEN seems invalid (should be alphanumeric with colon)")
        return v
    
    @field_validator('admin_id')
    @classmethod
    def validate_admin_id(cls, v):
        if v == 0:
            logger.warning("⚠️ ADMIN_ID = 0. Admin commands won't work. Set from @userinfobot")
        return v
    
    # ===== HELPER METHODS =====
    def create_directories(self):
        """Create all necessary directories"""
        dirs = [
            self.logging.log_dir,
            self.memory.memory_dir,
            self.backup.backup_dir,
            self.identity.session_dir,
            self.database.path.parent,
            self.base_dir / "data",
        ]
        for dir_path in dirs:
            try:
                dir_path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                logger.warning(f"Could not create directory {dir_path}: {e}")
        return self
    
    def validate_all(self) -> Dict[str, Any]:
        """Validate all settings and return status"""
        status = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'railway_mode': self.webhook.is_railway
        }
        
        # Check required keys
        if not self.deepseek_api_key or self.deepseek_api_key == "your_deepseek_api_key_here":
            status['valid'] = False
            status['errors'].append("DeepSeek API Key missing")
        
        if not self.telegram_token or self.telegram_token == "your_telegram_bot_token_here":
            status['valid'] = False
            status['errors'].append("Telegram Token missing")
        
        if self.admin_id == 0:
            status['warnings'].append("Admin ID not set (use /start with @userinfobot)")
        
        # Check directories
        for dir_path in [self.logging.log_dir, self.memory.memory_dir, self.backup.backup_dir]:
            if not dir_path.exists():
                try:
                    dir_path.mkdir(parents=True, exist_ok=True)
                    status['warnings'].append(f"Created missing directory: {dir_path}")
                except Exception as e:
                    status['warnings'].append(f"Cannot create directory {dir_path}: {e}")
        
        return status
    
    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information for Railway logging"""
        import platform
        
        return {
            'version': '9.9.0',
            'python_version': platform.python_version(),
            'platform': platform.platform(),
            'railway_mode': self.webhook.is_railway,
            'railway_domain': self.webhook.railway_domain,
            'database_type': self.database.type,
            'database_path': str(self.database.path),
            'ai_model': self.ai.model,
            'ai_temperature': self.ai.temperature,
            'admin_id': self.admin_id,
            'working_memory_size': self.memory.working_memory_size,
            'level_10_target': self.level.level_10_target,
            'features_enabled': {
                'sexual_content': self.features.sexual_content_enabled,
                'weighted_memory': self.features.weighted_memory_enabled,
                'emotional_bias': self.features.emotional_bias_enabled,
                'spatial_awareness': self.features.spatial_awareness_enabled,
            }
        }
    
    def log_configuration(self):
        """Log configuration to Railway console"""
        logger.info("=" * 70)
        logger.info("💜 AMORIA 9.9 - Configuration Loaded")
        logger.info("=" * 70)
        logger.info(f"🗄️  Database: {self.database.type} @ {self.database.path}")
        logger.info(f"🤖 AI Model: {self.ai.model} | Temperature: {self.ai.temperature}")
        logger.info(f"👑 Admin ID: {self.admin_id}")
        logger.info(f"📊 Working Memory: {self.memory.working_memory_size} chat")
        logger.info(f"💕 Level System: {self.level.level_targets[10]} chat → Level 10")
        logger.info(f"🔥 Soul Bounded: {self.level.level_11_min}-{self.level.level_11_max} chat")
        logger.info(f"💤 Aftercare: {self.level.level_12_min}-{self.level.level_12_max} chat")
        logger.info(f"🌍 Railway Mode: {self.webhook.is_railway}")
        if self.webhook.railway_domain:
            logger.info(f"🌐 Webhook URL: https://{self.webhook.railway_domain}{self.webhook.path}")
        logger.info("=" * 70)


# =============================================================================
# GLOBAL SETTINGS INSTANCE
# =============================================================================

_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get global settings instance with caching"""
    global _settings
    if _settings is None:
        try:
            _settings = Settings()
            _settings.create_directories()
            _settings.log_configuration()
            
            # Validate
            status = _settings.validate_all()
            if not status['valid']:
                for err in status['errors']:
                    logger.error(f"❌ Configuration error: {err}")
                raise ValueError("Invalid configuration")
            
            for warn in status['warnings']:
                logger.warning(f"⚠️ {warn}")
                
        except Exception as e:
            logger.error(f"❌ Failed to load configuration: {e}")
            raise
    
    return _settings


# For backward compatibility
settings = get_settings()


__all__ = ['settings', 'get_settings', 'Settings']
