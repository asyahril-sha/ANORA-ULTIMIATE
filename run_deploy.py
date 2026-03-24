# run_deploy.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Deployment Runner for Railway - WITH SINGLETON BOT & CLEAN LOGGING
=============================================================================
"""

import os
import sys
import asyncio
import traceback
import logging
from pathlib import Path
from aiohttp import web

# =============================================================================
# LOGGING CONFIGURATION (HARUS DI AWAL)
# =============================================================================

# Set log level untuk environment
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()

# Filter library yang noisy
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.INFO)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("aiohttp").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.WARNING)

# Konfigurasi root logger
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s | %(levelname)-5s | %(name)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Logger utama
logger = logging.getLogger("AMORIA")

# =============================================================================
# IMPORT MODULES
# =============================================================================

sys.path.insert(0, str(Path(__file__).parent))

from utils.error_logger import get_error_logger, print_startup_banner

# Inisialisasi error logger
error_logger = get_error_logger()
print_startup_banner()

try:
    from config import settings
    from utils.logger import setup_logging
except Exception as e:
    logger.error(f"❌ Import failed: {e}")
    sys.exit(1)

# Setup logging untuk AMORIA
logger = setup_logging("AMORIA-DEPLOY")

# =============================================================================
# GLOBAL BOT INSTANCE (SINGLETON)
# =============================================================================
_bot_instance = None
_bot_initialized = False


async def init_bot():
    """Initialize bot once at startup"""
    global _bot_instance, _bot_initialized
    
    if _bot_initialized:
        logger.info("✅ Bot already initialized, reusing instance")
        return _bot_instance
    
    logger.info("🚀 Initializing bot instance (SINGLETON MODE)...")
    
    try:
        from main import AmoriaBot
        
        _bot_instance = AmoriaBot()
        
        # Initialize database
        await _bot_instance.init_database()
        
        # Initialize application
        await _bot_instance.init_application()
        
        # Delete old webhook
        await _bot_instance.application.bot.delete_webhook(drop_pending_updates=True)
        logger.info("✅ Old webhook deleted")
        
        _bot_initialized = True
        logger.info("✅ Bot instance initialized successfully (SINGLETON)")
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize bot: {e}")
        raise
    
    return _bot_instance


# =============================================================================
# WEBHOOK HANDLER
# =============================================================================

async def webhook_handler(request):
    """Handle Telegram webhook requests"""
    global _bot_instance
    
    if not _bot_initialized or not _bot_instance:
        logger.error("❌ Bot not initialized yet!")
        return web.Response(status=503, text='Bot not ready')
    
    try:
        # Get update data
        update_data = await request.json()
        
        if not update_data:
            return web.Response(status=400, text='No data')
        
        update_id = update_data.get('update_id', 'unknown')
        
        # Log incoming update (INFO level, bukan DEBUG)
        if 'message' in update_data:
            msg = update_data['message']
            text = msg.get('text', '')[:50]
            user = msg.get('from', {}).get('first_name', 'unknown')
            logger.info(f"📨 Message from {user}: {text}")
        elif 'callback_query' in update_data:
            callback_data = update_data['callback_query'].get('data', 'unknown')
            logger.info(f"🔘 Callback: {callback_data}")
        
        # Create Update object
        from telegram import Update
        update = Update.de_json(update_data, _bot_instance.application.bot)
        
        # Process update (WAIT for completion)
        await _bot_instance.application.process_update(update)
        
        return web.Response(text='OK', status=200)
        
    except Exception as e:
        logger.error(f"❌ Webhook error: {e}")
        logger.error(traceback.format_exc())
        return web.Response(status=500, text='Error')


async def health_handler(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "bot": "AMORIA",
        "version": "9.9.0",
        "bot_initialized": _bot_initialized,
        "log_level": LOG_LEVEL,
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
        "log_level": LOG_LEVEL,
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
    
    logger.info(f"🌍 Starting server on port {port}")
    logger.info(f"📊 Log level: {LOG_LEVEL}")
    
    # Initialize bot FIRST
    await init_bot()
    
    # Setup webhook after bot initialized
    if _bot_instance and _bot_instance.application:
        railway_url = os.getenv('RAILWAY_PUBLIC_DOMAIN') or os.getenv('RAILWAY_STATIC_URL')
        if railway_url:
            webhook_url = f"https://{railway_url}/webhook"
            logger.info(f"🔗 Setting webhook to: {webhook_url}")
            
            await _bot_instance.application.bot.set_webhook(
                url=webhook_url,
                allowed_updates=['message', 'callback_query', 'inline_query'],
                drop_pending_updates=True,
                max_connections=40,
            )
            
            info = await _bot_instance.application.bot.get_webhook_info()
            logger.info(f"✅ Webhook set: {info.url}")
            logger.info(f"   Pending updates: {info.pending_update_count}")
    
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
    
    logger.info(f"🌐 Web server running on port {port}")
    logger.info(f"   • GET  /         - API Info")
    logger.info(f"   • GET  /health   - Health Check")
    logger.info(f"   • POST /webhook  - Telegram Webhook")
    logger.info("=" * 60)
    logger.info("💜 AMORIA 9.9 is running on Railway (SINGLETON MODE)!")
    logger.info("=" * 60)
    
    # Keep running
    while True:
        await asyncio.sleep(3600)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Main entry point"""
    try:
        from config import settings
        logger.info(f"✅ Config loaded: Admin ID = {settings.admin_id}")
    except Exception as e:
        logger.error(f"❌ Config error: {e}")
        sys.exit(1)
    
    # Start web server
    try:
        asyncio.run(start_web_server())
    except KeyboardInterrupt:
        logger.info("👋 Bot stopped by user")
    except Exception as e:
        error_logger.log_error(e, {'stage': 'main'}, severity="CRITICAL")
        sys.exit(1)


if __name__ == "__main__":
    main()
