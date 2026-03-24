# run_deploy.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Deployment Runner for Railway - With Webhook & Health Check
=============================================================================
"""

import os
import sys
import asyncio
import traceback
from pathlib import Path
from aiohttp import web

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import error logger first
from utils.error_logger import get_error_logger, log_info, log_error, log_warning, print_startup_banner

# Initialize error logger
error_logger = get_error_logger()
print_startup_banner()

try:
    from config import settings
    from utils.logger import setup_logging
    from bot.application import create_application
    from bot.webhook import setup_webhook_sync, setup_polling
    from database.migrate import run_migrations
except Exception as e:
    error_logger.log_error(e, {'stage': 'import_modules'}, severity="CRITICAL")
    sys.exit(1)

logger = setup_logging("AMORIA-DEPLOY")


def check_environment() -> bool:
    """Check environment without interactive input"""
    log_info("=" * 60)
    log_info("🔍 CHECKING ENVIRONMENT (DEPLOYMENT MODE)")
    log_info("=" * 60)
    
    errors = []
    warnings = []
    
    railway_env = os.getenv('RAILWAY_ENVIRONMENT')
    railway_domain = os.getenv('RAILWAY_PUBLIC_DOMAIN')
    railway_url = os.getenv('RAILWAY_STATIC_URL')
    
    log_info(f"📡 Railway Environment: {railway_env or 'Not detected'}")
    log_info(f"📡 Railway Domain: {railway_domain or 'Not set'}")
    log_info(f"📡 Railway URL: {railway_url or 'Not set'}")
    
    env_path = Path(".env")
    if not env_path.exists():
        log_warning("⚠️ .env file not found! Using environment variables.")
    
    try:
        if not settings.deepseek_api_key or settings.deepseek_api_key == "your_deepseek_api_key_here":
            errors.append("DeepSeek API key not configured")
            log_error("DeepSeek API key missing")
        else:
            log_info(f"✅ DeepSeek API Key: {settings.deepseek_api_key[:10]}...")
        
        if not settings.telegram_token or settings.telegram_token == "your_telegram_bot_token_here":
            errors.append("Telegram token not configured")
            log_error("Telegram token missing")
        else:
            log_info(f"✅ Telegram Token: {settings.telegram_token[:10]}...")
        
        if settings.admin_id == 0:
            warnings.append("Admin ID not configured")
            log_warning("⚠️ Admin ID not configured")
        else:
            log_info(f"✅ Admin ID: {settings.admin_id}")
            
    except Exception as e:
        errors.append(f"Failed to load config: {e}")
        error_logger.log_error(e, {'stage': 'config_load'})
    
    required_dirs = [
        'data', 'data/logs', 'data/backups', 
        'data/sessions', 'data/vector_db', 'data/memory'
    ]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        dir_path.mkdir(parents=True, exist_ok=True)
        log_info(f"✅ Directory: {dir_name}")
    
    if errors:
        log_error("\n❌ ERRORS FOUND:")
        for err in errors:
            log_error(f"   - {err}")
        return False
    
    if warnings:
        log_warning("\n⚠️ WARNINGS:")
        for warn in warnings:
            log_warning(f"   - {warn}")
    
    log_info("\n✅ Environment is ready!")
    return True


def run_migration() -> bool:
    """Run database migration"""
    log_info("\n" + "=" * 60)
    log_info("🗄️ RUNNING DATABASE MIGRATION")
    log_info("=" * 60)
    
    try:
        success = asyncio.run(run_migrations())
        
        if success:
            log_info("✅ Migration completed")
            return True
        else:
            log_error("❌ Migration failed")
            return False
            
    except Exception as e:
        error_logger.log_error(e, {'stage': 'migration'}, severity="ERROR")
        return False


async def health_handler(request):
    """Health check endpoint"""
    return web.json_response({
        "status": "healthy",
        "bot": "AMORIA",
        "version": "9.9.0",
        "timestamp": __import__('datetime').datetime.now().isoformat()
    })


async def root_handler(request):
    """Root endpoint"""
    return web.json_response({
        "name": "AMORIA",
        "description": "Virtual Human dengan Jiwa",
        "version": "9.9.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "webhook": "/webhook"
        }
    })


async def webhook_handler(request):
    """Webhook endpoint untuk Telegram"""
    try:
        from main import AmoriaBot
        bot = AmoriaBot()
        await bot.init_application()
        
        update_data = await request.json()
        log_info(f"📨 Received webhook update: {update_data.get('update_id', 'unknown')}")
        
        # Process update
        from telegram import Update
        update = Update.de_json(update_data, bot.application.bot)
        asyncio.create_task(bot.application.process_update(update))
        
        return web.Response(text='OK', status=200)
        
    except Exception as e:
        error_logger.log_error(e, {'stage': 'webhook_handler'})
        return web.Response(text='Error', status=500)


def start_web_server():
    """Start aiohttp web server with all endpoints"""
    log_info("\n" + "=" * 60)
    log_info("🌐 STARTING WEB SERVER")
    log_info("=" * 60)
    
    port = int(os.getenv('PORT', 8080))
    
    app = web.Application()
    app.router.add_get('/', root_handler)
    app.router.add_get('/health', health_handler)
    app.router.add_post('/webhook', webhook_handler)
    
    web.run_app(app, host='0.0.0.0', port=port)


def start_bot_with_polling():
    """Start bot with polling mode (fallback jika webhook tidak bisa)"""
    log_info("\n" + "=" * 60)
    log_info("🚀 STARTING AMORIA WITH POLLING MODE")
    log_info("=" * 60)
    
    try:
        from main import main
        asyncio.run(main())
        return True
        
    except ImportError as e:
        log_error(f"❌ ImportError: {e}")
        log_error(traceback.format_exc())
        return False
        
    except Exception as e:
        error_logger.log_error(e, {'stage': 'bot_start'}, severity="CRITICAL")
        log_error(traceback.format_exc())
        return False


def main():
    """Main runner untuk deployment"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     💜 AMORIA 9.9 - Virtual Human dengan Jiwa                   ║
║     Deployment Mode (Railway)                                   ║
║                                                                  ║
║     🔧 Automatic Setup:                                         ║
║     • Checking environment variables                           ║
║     • Creating directories                                      ║
║     • Running database migration                                ║
║     • Starting web server with webhook endpoint                 ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check environment
    if not check_environment():
        log_error("Environment check failed. Please set environment variables.")
        sys.exit(1)
    
    # Step 2: Run migration
    if not run_migration():
        log_warning("Migration failed, but continuing...")
    
    # Step 3: Start web server (with webhook endpoint)
    log_info("\n" + "=" * 60)
    log_info("🌐 STARTING WEB SERVER WITH WEBHOOK ENDPOINT...")
    log_info("📡 Endpoints:")
    log_info("   • GET  /         - API Info")
    log_info("   • GET  /health   - Health Check")
    log_info("   • POST /webhook  - Telegram Webhook")
    log_info("=" * 60)
    
    # Start web server (blocking)
    start_web_server()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error_logger = get_error_logger()
        error_logger.log_error(e, {'stage': 'deploy_main'}, severity="CRITICAL")
        sys.exit(1)
