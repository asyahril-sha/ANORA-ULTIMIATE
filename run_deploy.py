# run_deploy.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Deployment Runner for Railway - WITH SINGLETON BOT
=============================================================================
"""

import os
import sys
import asyncio
import traceback
from pathlib import Path
from aiohttp import web

sys.path.insert(0, str(Path(__file__).parent))

from utils.error_logger import get_error_logger, log_info, log_error, log_warning, print_startup_banner
from utils.logger import setup_logging

# =============================================================================
# GLOBAL BOT INSTANCE (SINGLETON)
# =============================================================================
_bot_instance = None
_bot_initialized = False


async def init_bot():
    """Initialize bot once at startup"""
    global _bot_instance, _bot_initialized
    
    if _bot_initialized:
        log_info("✅ Bot already initialized, reusing instance")
        return _bot_instance
    
    log_info("🚀 Initializing bot instance (SINGLETON MODE)...")
    
    try:
        from main import AmoriaBot
        
        _bot_instance = AmoriaBot()
        
        # Initialize database
        await _bot_instance.init_database()
        
        # Initialize application
        await _bot_instance.init_application()
        
        # Delete old webhook
        await _bot_instance.application.bot.delete_webhook(drop_pending_updates=True)
        log_info("✅ Old webhook deleted")
        
        _bot_initialized = True
        log_info("✅ Bot instance initialized successfully (SINGLETON)")
        
    except Exception as e:
        log_error(f"❌ Failed to initialize bot: {e}")
        raise
    
    return _bot_instance


# =============================================================================
# WEBHOOK HANDLER
# =============================================================================

async def webhook_handler(request):
    """Handle Telegram webhook requests"""
    global _bot_instance
    
    if not _bot_initialized or not _bot_instance:
        log_error("❌ Bot not initialized yet!")
        return web.Response(status=503, text='Bot not ready')
    
    try:
        # Get update data
        update_data = await request.json()
        
        if not update_data:
            return web.Response(status=400, text='No data')
        
        log_info(f"📨 Webhook received: update_id={update_data.get('update_id', 'unknown')}")
        
        # Create Update object
        from telegram import Update
        update = Update.de_json(update_data, _bot_instance.application.bot)
        
        # Process update (WAIT for completion, don't create task)
        await _bot_instance.application.process_update(update)
        
        return web.Response(text='OK', status=200)
        
    except Exception as e:
        log_error(f"❌ Webhook error: {e}")
        log_error(traceback.format_exc())
        return web.Response(status=500, text='Error')


async def health_handler(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "bot": "AMORIA",
        "version": "9.9.0",
        "bot_initialized": _bot_initialized,
        "timestamp": __import__('datetime').datetime.now().isoformat()
    })


async def root_handler(request):
    """Root endpoint"""
    return web.json_response({
        "name": "AMORIA",
        "description": "Virtual Human dengan Jiwa",
        "version": "9.9.0",
        "status": "running",
        "bot_initialized": _bot_initialized,
        "endpoints": {
            "health": "/health",
            "webhook": "/webhook"
        }
    })


# =============================================================================
# START WEB SERVER
# =============================================================================

async def start_web_server():
    """Start aiohttp web server with singleton bot"""
    port = int(os.getenv('PORT', 8080))
    
    # Initialize bot FIRST
    await init_bot()
    
    # Setup webhook after bot initialized
    if _bot_instance and _bot_instance.application:
        railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
        if railway_url:
            webhook_url = f"https://{railway_url}/webhook"
            log_info(f"🔗 Setting webhook to: {webhook_url}")
            
            await _bot_instance.application.bot.set_webhook(
                url=webhook_url,
                allowed_updates=['message', 'callback_query', 'inline_query'],
                drop_pending_updates=True,
                max_connections=40,
            )
            
            info = await _bot_instance.application.bot.get_webhook_info()
            log_info(f"✅ Webhook set: {info.url}")
            log_info(f"   Pending updates: {info.pending_update_count}")
    
    # Create web app
    app = web.Application()
    app.router.add_get('/', root_handler)
    app.router.add_get('/health', health_handler)
    app.router.add_post('/webhook', webhook_handler)
    
    # Run server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    
    log_info(f"🌐 Web server running on port {port}")
    log_info(f"   • GET  /         - API Info")
    log_info(f"   • GET  /health   - Health Check")
    log_info(f"   • POST /webhook  - Telegram Webhook")
    log_info("=" * 60)
    log_info("💜 AMORIA 9.9 is running on Railway (SINGLETON MODE)!")
    log_info("=" * 60)
    
    # Keep running
    while True:
        await asyncio.sleep(3600)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point"""
    error_logger = get_error_logger()
    print_startup_banner()
    
    # Check environment
    try:
        from config import settings
        log_info(f"✅ Config loaded: Admin ID = {settings.admin_id}")
    except Exception as e:
        log_error(f"❌ Config error: {e}")
        sys.exit(1)
    
    # Start web server
    try:
        asyncio.run(start_web_server())
    except KeyboardInterrupt:
        log_info("👋 Bot stopped by user")
    except Exception as e:
        error_logger.log_error(e, {'stage': 'main'}, severity="CRITICAL")
        sys.exit(1)


if __name__ == "__main__":
    main()
