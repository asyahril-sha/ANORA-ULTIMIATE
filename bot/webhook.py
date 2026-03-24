# bot/webhook.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Webhook Manager
=============================================================================
"""

import os
import asyncio
import logging
from typing import Optional
from telegram import Update
from telegram.ext import Application

from config import settings

logger = logging.getLogger(__name__)


def setup_webhook_sync(app: Application) -> bool:
    """
    Setup webhook synchronously (untuk main.py)
    
    Args:
        app: Application instance
        
    Returns:
        True if webhook setup successful
    """
    try:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_setup_webhook_async(app))
    except Exception as e:
        logger.error(f"Webhook setup failed: {e}")
        return False


async def _setup_webhook_async(app: Application) -> bool:
    """Setup webhook asynchronously"""
    # Dapatkan URL webhook
    railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
    
    if railway_url:
        webhook_url = f"https://{railway_url}{settings.webhook.path}"
    elif settings.webhook.url:
        webhook_url = settings.webhook.url.rstrip('/') + settings.webhook.path
    else:
        logger.warning("No webhook URL configured, using polling mode")
        return False
    
    logger.info(f"🔗 Setting webhook to: {webhook_url}")
    
    try:
        # Delete existing webhook
        await app.bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Existing webhook deleted")
        
        # Set new webhook
        secret_token = getattr(settings.webhook, 'secret_token', None)
        await app.bot.set_webhook(
            url=webhook_url,
            allowed_updates=['message', 'callback_query', 'inline_query'],
            drop_pending_updates=True,
            max_connections=40,
            timeout=30,
            secret_token=secret_token
        )
        logger.info("✅ New webhook set")
        
        # Verify
        info = await app.bot.get_webhook_info()
        if info.url == webhook_url:
            logger.info(f"✅ Webhook verified: {info.url}")
            logger.info(f"   Pending updates: {info.pending_update_count}")
            return True
        else:
            logger.error(f"❌ Webhook verification failed: {info.url}")
            return False
            
    except Exception as e:
        logger.error(f"Webhook setup failed: {e}")
        return False


async def check_webhook_status(app: Application) -> dict:
    """Check current webhook status"""
    try:
        info = await app.bot.get_webhook_info()
        return {
            "url": info.url,
            "pending_updates": info.pending_update_count,
            "last_error": info.last_error_message,
            "last_error_date": info.last_error_date,
            "max_connections": info.max_connections,
            "allowed_updates": info.allowed_updates
        }
    except Exception as e:
        return {"error": str(e)}


async def reset_webhook(app: Application, url: Optional[str] = None) -> bool:
    """Reset webhook (delete then set new)"""
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Existing webhook deleted")
        
        if url:
            await app.bot.set_webhook(url=url)
            logger.info(f"✅ New webhook set: {url}")
            return True
        else:
            logger.info("✅ Webhook deleted, now using polling mode")
            return True
            
    except Exception as e:
        logger.error(f"Error resetting webhook: {e}")
        return False


async def setup_polling(app: Application) -> bool:
    """Setup polling mode (fallback)"""
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Webhook deleted, using polling mode")
        return True
    except Exception as e:
        logger.error(f"Failed to setup polling: {e}")
        return False


__all__ = [
    'setup_webhook_sync',
    'check_webhook_status',
    'reset_webhook',
    'setup_polling'
]
