# bot/middleware.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Bot Middleware - Rate Limiting, Logging, Metrics, Error Handling
Target Realism 9.9/10
=============================================================================
"""

import time
import logging
from typing import Dict, Callable, Awaitable, Optional, Any
from collections import defaultdict
from functools import wraps
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from config import settings
from utils.performance import get_performance_monitor
from utils.logger import logger

# =============================================================================
# RATE LIMITER
# =============================================================================

class RateLimiter:
    """
    Rate limiter untuk mencegah spam
    - Limit per user per interval
    - Cooldown untuk command tertentu
    """
    
    def __init__(self, default_limit: int = 30, default_interval: int = 60):
        """
        Args:
            default_limit: Jumlah maksimal request per interval
            default_interval: Interval dalam detik
        """
        self.default_limit = default_limit
        self.default_interval = default_interval
        self.user_requests: Dict[int, list] = defaultdict(list)
        self.command_cooldown: Dict[str, Dict[int, float]] = defaultdict(dict)
        
        # Cooldown khusus untuk command tertentu (detik)
        self.command_cooldowns = {
            '/start': 5,
            '/end': 10,
            '/close': 5,
            '/character-stop': 10,
            '/fwb-end': 10,
            '/backup': 30,
            '/recover': 60,
        }
        
        logger.info("✅ RateLimiter initialized")
    
    def is_rate_limited(self, user_id: int, command: Optional[str] = None) -> tuple:
        """
        Cek apakah user terkena rate limit
        
        Args:
            user_id: ID user
            command: Command yang dieksekusi (opsional)
        
        Returns:
            (is_limited, wait_time, message)
        """
        now = time.time()
        
        # Check command cooldown
        if command and command in self.command_cooldowns:
            cooldown = self.command_cooldowns[command]
            last_used = self.command_cooldown[command].get(user_id, 0)
            time_since = now - last_used
            
            if time_since < cooldown:
                wait_time = int(cooldown - time_since)
                return True, wait_time, f"Command ini bisa digunakan lagi dalam {wait_time} detik."
        
        # Check general rate limit
        requests = self.user_requests[user_id]
        requests = [t for t in requests if now - t < self.default_interval]
        self.user_requests[user_id] = requests
        
        if len(requests) >= self.default_limit:
            wait_time = int(self.default_interval - (now - requests[0]))
            return True, wait_time, f"Terlalu banyak pesan. Tunggu {wait_time} detik."
        
        # Add current request
        self.user_requests[user_id].append(now)
        
        return False, 0, ""
    
    def record_command(self, user_id: int, command: str):
        """Rekam penggunaan command untuk cooldown"""
        if command in self.command_cooldowns:
            self.command_cooldown[command][user_id] = time.time()
    
    def clear_user(self, user_id: int):
        """Hapus semua data user"""
        self.user_requests.pop(user_id, None)
        for cmd in self.command_cooldown:
            self.command_cooldown[cmd].pop(user_id, None)


# =============================================================================
# METRICS MIDDLEWARE
# =============================================================================

class MetricsMiddleware:
    """
    Middleware untuk tracking metrics
    - Response time
    - Command usage
    - Error tracking
    """
    
    def __init__(self):
        self.metrics = get_performance_monitor()
        logger.info("✅ MetricsMiddleware initialized")
    
    async def __call__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        next_handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]
    ):
        """Process update dengan metrics tracking"""
        start_time = time.time()
        operation = "unknown"
        
        try:
            # Detect operation type
            if update.message:
                if update.message.text and update.message.text.startswith('/'):
                    operation = update.message.text.split()[0]
                else:
                    operation = "message"
            elif update.callback_query:
                operation = "callback"
            elif update.inline_query:
                operation = "inline"
            
            # Track command usage
            if operation.startswith('/'):
                self.metrics.record_command_usage(operation)
            
            # Process
            await next_handler(update, context)
            
            # Record response time
            duration = time.time() - start_time
            self.metrics.record_response_time(duration, operation)
            
        except Exception as e:
            duration = time.time() - start_time
            self.metrics.record_error(type(e).__name__, operation)
            self.metrics.record_response_time(duration, f"{operation}_error")
            raise


# =============================================================================
# LOGGING MIDDLEWARE
# =============================================================================

class LoggingMiddleware:
    """
    Middleware untuk logging update
    - Log semua update yang masuk
    - Log error
    - Log performance
    """
    
    def __init__(self, log_level: str = "INFO"):
        self.log_level = log_level
        logger.info(f"✅ LoggingMiddleware initialized (level: {log_level})")
    
    async def __call__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        next_handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]
    ):
        """Process update dengan logging"""
        start_time = time.time()
        
        # Log incoming update
        await self._log_incoming(update, context)
        
        try:
            await next_handler(update, context)
            
            # Log completion
            duration = time.time() - start_time
            await self._log_completion(update, context, duration)
            
        except Exception as e:
            duration = time.time() - start_time
            await self._log_error(update, context, e, duration)
            raise
    
    async def _log_incoming(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log incoming update"""
        user = update.effective_user
        user_id = user.id if user else "unknown"
        user_name = user.first_name if user else "unknown"
        
        if update.message:
            if update.message.text:
                text = update.message.text[:100]
                logger.info(f"📨 [{user_id}] {user_name}: {text}")
            elif update.message.photo:
                logger.info(f"📸 [{user_id}] {user_name}: sent photo")
            elif update.message.sticker:
                logger.info(f"🎨 [{user_id}] {user_name}: sent sticker")
            else:
                logger.info(f"📨 [{user_id}] {user_name}: {update.message.content_type}")
        
        elif update.callback_query:
            data = update.callback_query.data[:100]
            logger.info(f"🔘 [{user_id}] {user_name}: callback {data}")
        
        elif update.inline_query:
            query = update.inline_query.query[:100]
            logger.info(f"🔍 [{user_id}] {user_name}: inline query {query}")
    
    async def _log_completion(self, update: Update, context: ContextTypes.DEFAULT_TYPE, duration: float):
        """Log completion update"""
        user = update.effective_user
        user_id = user.id if user else "unknown"
        
        if duration > 5:
            logger.warning(f"🐌 Slow response for {user_id}: {duration:.2f}s")
        elif duration > 2:
            logger.debug(f"⏱️ Response time for {user_id}: {duration:.2f}s")
    
    async def _log_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception, duration: float):
        """Log error"""
        user = update.effective_user
        user_id = user.id if user else "unknown"
        
        logger.error(f"❌ Error for {user_id}: {type(error).__name__}: {error} (took {duration:.2f}s)")


# =============================================================================
# ERROR HANDLER MIDDLEWARE
# =============================================================================

class ErrorHandlerMiddleware:
    """
    Middleware untuk error handling
    - Catch unhandled exceptions
    - Send friendly error messages to user
    - Log errors for debugging
    """
    
    async def __call__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        next_handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]
    ):
        """Process update dengan error handling"""
        try:
            await next_handler(update, context)
            
        except Exception as e:
            logger.exception(f"Unhandled error: {e}")
            
            # Try to send error message to user
            try:
                if update and update.effective_message:
                    await update.effective_message.reply_text(
                        "❌ **Terjadi kesalahan**\n\n"
                        "Maaf, terjadi error internal. Tim pengembang sudah diberitahu.\n\n"
                        "Silakan coba lagi nanti, atau gunakan `/help` untuk bantuan.",
                        parse_mode='HTML'
                    )
            except Exception:
                pass
            
            # Re-raise for global handler
            raise


# =============================================================================
# SESSION MIDDLEWARE
# =============================================================================

class SessionMiddleware:
    """
    Middleware untuk session management
    - Check session validity
    - Auto-renew session
    - Track active sessions
    """
    
    def __init__(self):
        self.session_timeout = 3600  # 1 hour
        self.active_sessions: Dict[int, float] = {}
        logger.info(f"✅ SessionMiddleware initialized (timeout: {self.session_timeout}s)")
    
    async def __call__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        next_handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]
    ):
        """Process update dengan session management"""
        user = update.effective_user
        user_id = user.id if user else None
        
        if user_id:
            # Update active session timestamp
            self.active_sessions[user_id] = time.time()
            
            # Check if session is still valid
            if user_id in context.user_data:
                last_activity = context.user_data.get('last_activity', 0)
                if time.time() - last_activity > self.session_timeout:
                    # Session expired
                    await self._handle_expired_session(update, context)
            
            # Update last activity
            context.user_data['last_activity'] = time.time()
        
        await next_handler(update, context)
    
    async def _handle_expired_session(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle expired session"""
        user_id = update.effective_user.id if update.effective_user else None
        
        logger.info(f"Session expired for user {user_id}")
        
        # Clear user data
        context.user_data.clear()
        
        # Notify user if it's a message
        if update and update.message:
            await update.message.reply_text(
                "⏰ **Session telah berakhir**\n\n"
                "Karena tidak ada aktivitas dalam 1 jam, session kamu telah di-reset.\n\n"
                "Ketik `/start` untuk memulai lagi.",
                parse_mode='HTML'
            )


# =============================================================================
# MAIN MIDDLEWARE CHAIN
# =============================================================================

class MiddlewareChain:
    """
    Chain untuk semua middleware
    - Execute middleware in order
    - Pass update through all layers
    """
    
    def __init__(self):
        self.middlewares = []
        logger.info("✅ MiddlewareChain initialized")
    
    def add(self, middleware):
        """Tambah middleware ke chain"""
        self.middlewares.append(middleware)
        logger.debug(f"Added middleware: {middleware.__class__.__name__}")
    
    async def process(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        handler: Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]
    ):
        """Process update melalui semua middleware"""
        # Build chain
        current = handler
        
        for middleware in reversed(self.middlewares):
            current = self._wrap(middleware, current)
        
        await current(update, context)
    
    def _wrap(self, middleware, next_handler):
        """Wrap handler dengan middleware"""
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            await middleware(update, context, next_handler)
        return wrapper


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================

_rate_limiter = None
_metrics_middleware = None
_logging_middleware = None
_error_handler = None
_session_middleware = None
_middleware_chain = None


def get_rate_limiter() -> RateLimiter:
    """Dapatkan instance RateLimiter (singleton)"""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def get_metrics_middleware() -> MetricsMiddleware:
    """Dapatkan instance MetricsMiddleware (singleton)"""
    global _metrics_middleware
    if _metrics_middleware is None:
        _metrics_middleware = MetricsMiddleware()
    return _metrics_middleware


def get_logging_middleware() -> LoggingMiddleware:
    """Dapatkan instance LoggingMiddleware (singleton)"""
    global _logging_middleware
    if _logging_middleware is None:
        _logging_middleware = LoggingMiddleware()
    return _logging_middleware


def get_error_handler() -> ErrorHandlerMiddleware:
    """Dapatkan instance ErrorHandlerMiddleware (singleton)"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandlerMiddleware()
    return _error_handler


def get_session_middleware() -> SessionMiddleware:
    """Dapatkan instance SessionMiddleware (singleton)"""
    global _session_middleware
    if _session_middleware is None:
        _session_middleware = SessionMiddleware()
    return _session_middleware


def get_middleware_chain() -> MiddlewareChain:
    """Dapatkan instance MiddlewareChain dengan semua middleware"""
    global _middleware_chain
    if _middleware_chain is None:
        _middleware_chain = MiddlewareChain()
        
        # Add middleware in order
        _middleware_chain.add(get_error_handler())
        _middleware_chain.add(get_logging_middleware())
        _middleware_chain.add(get_session_middleware())
        _middleware_chain.add(get_metrics_middleware())
        # Rate limiter optional - bisa ditambahkan nanti
        
        logger.info("✅ Middleware chain built")
    
    return _middleware_chain


__all__ = [
    'RateLimiter',
    'get_rate_limiter',
    'MetricsMiddleware',
    'get_metrics_middleware',
    'LoggingMiddleware',
    'get_logging_middleware',
    'ErrorHandlerMiddleware',
    'get_error_handler',
    'SessionMiddleware',
    'get_session_middleware',
    'MiddlewareChain',
    'get_middleware_chain',
]
