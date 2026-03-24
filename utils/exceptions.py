# utils/exceptions.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Custom Exceptions
=============================================================================
"""

import sys
import traceback
from typing import Optional, Any
from loguru import logger


class AmoriaError(Exception):
    """Base exception untuk semua error AMORIA"""
    
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Any] = None):
        self.message = message
        self.code = code or "AMORIA_ERROR"
        self.details = details
        super().__init__(self.message)
    
    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


# =============================================================================
# CONFIGURATION ERRORS
# =============================================================================

class ConfigurationError(AmoriaError):
    """Error dalam konfigurasi"""
    
    def __init__(self, message: str, config_key: Optional[str] = None):
        super().__init__(
            message=f"Configuration error: {message}",
            code="CONFIG_ERROR",
            details={"config_key": config_key}
        )


class MissingAPIKeyError(ConfigurationError):
    """API key tidak ditemukan"""
    
    def __init__(self, key_name: str):
        super().__init__(
            message=f"Missing API key: {key_name}",
            config_key=key_name
        )


# =============================================================================
# DATABASE ERRORS
# =============================================================================

class DatabaseError(AmoriaError):
    """Error database"""
    
    def __init__(self, message: str, query: Optional[str] = None):
        super().__init__(
            message=f"Database error: {message}",
            code="DB_ERROR",
            details={"query": query}
        )


class ConnectionError(DatabaseError):
    """Error koneksi database"""
    
    def __init__(self, db_path: str):
        super().__init__(
            message=f"Cannot connect to database: {db_path}",
            query=None
        )


# =============================================================================
# AI ERRORS
# =============================================================================

class AINotAvailableError(AmoriaError):
    """AI service tidak tersedia"""
    
    def __init__(self, model: str, reason: str = "unknown"):
        super().__init__(
            message=f"AI service {model} not available: {reason}",
            code="AI_UNAVAILABLE",
            details={"model": model, "reason": reason}
        )


class AITimeoutError(AINotAvailableError):
    """Timeout saat call AI"""
    
    def __init__(self, model: str, timeout: int):
        super().__init__(
            model=model,
            reason=f"timeout after {timeout}s"
        )


class AIResponseError(AmoriaError):
    """Error pada response AI"""
    
    def __init__(self, message: str, response: Optional[str] = None):
        super().__init__(
            message=f"AI response error: {message}",
            code="AI_RESPONSE_ERROR",
            details={"response_preview": response[:200] if response else None}
        )


# =============================================================================
# IDENTITY & REGISTRATION ERRORS
# =============================================================================

class RegistrationNotFoundError(AmoriaError):
    """Registrasi tidak ditemukan"""
    
    def __init__(self, registration_id: str):
        super().__init__(
            message=f"Registration not found: {registration_id}",
            code="REGISTRATION_NOT_FOUND",
            details={"registration_id": registration_id}
        )


class RegistrationLimitError(AmoriaError):
    """Melebihi batas registrasi per role"""
    
    def __init__(self, role: str, max_characters: int):
        super().__init__(
            message=f"Cannot create more than {max_characters} characters for role {role}",
            code="REGISTRATION_LIMIT",
            details={"role": role, "max": max_characters}
        )


class CharacterNotFoundError(AmoriaError):
    """Karakter tidak ditemukan"""
    
    def __init__(self, role: str, sequence: int):
        super().__init__(
            message=f"Character not found: {role}-{sequence:03d}",
            code="CHARACTER_NOT_FOUND",
            details={"role": role, "sequence": sequence}
        )


# =============================================================================
# SESSION ERRORS
# =============================================================================

class SessionNotFoundError(AmoriaError):
    """Session tidak ditemukan"""
    
    def __init__(self, registration_id: str):
        super().__init__(
            message=f"Session not found: {registration_id}",
            code="SESSION_NOT_FOUND",
            details={"registration_id": registration_id}
        )


class SessionNotActiveError(AmoriaError):
    """Session tidak aktif"""
    
    def __init__(self, registration_id: str, status: str):
        super().__init__(
            message=f"Session {registration_id} is not active (status: {status})",
            code="SESSION_INACTIVE",
            details={"registration_id": registration_id, "status": status}
        )


# =============================================================================
# ROLE ERRORS
# =============================================================================

class RoleNotFoundError(AmoriaError):
    """Role tidak ditemukan"""
    
    def __init__(self, role: str):
        super().__init__(
            message=f"Role not found: {role}",
            code="ROLE_NOT_FOUND",
            details={"role": role}
        )


# =============================================================================
# INTIMACY ERRORS
# =============================================================================

class IntimacyLevelError(AmoriaError):
    """Error terkait intimacy level"""
    
    def __init__(self, message: str, current: int, required: int):
        super().__init__(
            message=message,
            code="INTIMACY_ERROR",
            details={"current": current, "required": required}
        )


class IntimacyTooLowError(IntimacyLevelError):
    """Intimacy level terlalu rendah"""
    
    def __init__(self, current: int, required: int, action: str):
        super().__init__(
            message=f"Intimacy level too low for {action} (current: {current}, required: {required})",
            current=current,
            required=required
        )
        self.current = current
        self.required = required


class StaminaTooLowError(AmoriaError):
    """Stamina terlalu rendah untuk intim"""
    
    def __init__(self, stamina: int):
        super().__init__(
            message=f"Stamina too low ({stamina}%) to start intimacy",
            code="STAMINA_TOO_LOW",
            details={"stamina": stamina}
        )
        self.stamina = stamina


class CooldownActiveError(AmoriaError):
    """Cooldown masih aktif"""
    
    def __init__(self, remaining_minutes: int):
        super().__init__(
            message=f"Still in aftercare cooldown ({remaining_minutes} minutes remaining)",
            code="COOLDOWN_ACTIVE",
            details={"remaining_minutes": remaining_minutes}
        )
        self.remaining_minutes = remaining_minutes


# =============================================================================
# MEMORY ERRORS
# =============================================================================

class MemoryError(AmoriaError):
    """Error pada sistem memory"""
    
    def __init__(self, message: str):
        super().__init__(
            message=f"Memory error: {message}",
            code="MEMORY_ERROR"
        )


# =============================================================================
# VALIDATION ERRORS
# =============================================================================

class ValidationError(AmoriaError):
    """Error validasi input"""
    
    def __init__(self, field: str, reason: str, value: Optional[Any] = None):
        super().__init__(
            message=f"Validation error for {field}: {reason}",
            code="VALIDATION_ERROR",
            details={"field": field, "value": value, "reason": reason}
        )


class InvalidCommandError(ValidationError):
    """Command tidak valid"""
    
    def __init__(self, command: str, reason: str = "unknown"):
        super().__init__(
            field="command",
            reason=reason,
            value=command
        )


# =============================================================================
# BACKUP ERRORS
# =============================================================================

class BackupError(AmoriaError):
    """Error backup/restore"""
    
    def __init__(self, message: str, filename: Optional[str] = None):
        super().__init__(
            message=f"Backup error: {message}",
            code="BACKUP_ERROR",
            details={"filename": filename}
        )


class BackupNotFoundError(BackupError):
    """File backup tidak ditemukan"""
    
    def __init__(self, filename: str):
        super().__init__(
            message=f"Backup file not found: {filename}",
            filename=filename
        )


# =============================================================================
# GLOBAL EXCEPTION HANDLER
# =============================================================================

def global_exception_handler(exc_type, exc_value, exc_traceback):
    """Handle uncaught exceptions"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.opt(exception=(exc_type, exc_value, exc_traceback)).critical(
        f"🔥 Uncaught exception in AMORIA: {exc_type.__name__}: {exc_value}"
    )


# Set global exception handler
sys.excepthook = global_exception_handler


__all__ = [
    # Base
    'AmoriaError',
    
    # Configuration
    'ConfigurationError',
    'MissingAPIKeyError',
    
    # Database
    'DatabaseError',
    'ConnectionError',
    
    # AI
    'AINotAvailableError',
    'AITimeoutError',
    'AIResponseError',
    
    # Identity
    'RegistrationNotFoundError',
    'RegistrationLimitError',
    'CharacterNotFoundError',
    
    # Session
    'SessionNotFoundError',
    'SessionNotActiveError',
    
    # Role
    'RoleNotFoundError',
    
    # Intimacy
    'IntimacyLevelError',
    'IntimacyTooLowError',
    'StaminaTooLowError',
    'CooldownActiveError',
    
    # Memory
    'MemoryError',
    
    # Validation
    'ValidationError',
    'InvalidCommandError',
    
    # Backup
    'BackupError',
    'BackupNotFoundError',
]
