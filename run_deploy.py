# run_deploy.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Deployment Runner (Railway)
=============================================================================
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# ===== PENTING: Setup logging SEBELUM import module lain =====
# Ini untuk menghindari error import circular
from loguru import logger as loguru_logger

# Setup logging sederhana dulu
loguru_logger.remove()
loguru_logger.add(sys.stdout, level="INFO")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# ===== IMPORT SETELAH PATH DISET =====
# Import config dulu untuk cek environment
try:
    from config import settings
except Exception as e:
    loguru_logger.error(f"Failed to import config: {e}")
    sys.exit(1)

# Setup logging lengkap setelah config available
try:
    from utils.logger import setup_logging
    logger = setup_logging("AMORIA-DEPLOY")
except Exception as e:
    loguru_logger.error(f"Failed to setup logging: {e}")
    # Fallback ke loguru
    logger = loguru_logger

logger = logger  # type: ignore


def check_environment() -> bool:
    """Check environment without interactive input"""
    logger.info("=" * 60)
    logger.info("🔍 CHECKING ENVIRONMENT (DEPLOYMENT MODE)")
    logger.info("=" * 60)
    
    errors = []
    
    # Railway menggunakan environment variables, bukan .env file
    # Jadi kita langsung cek environment variables
    
    try:
        # Cek DeepSeek API Key
        deepseek_key = os.getenv('DEEPSEEK_API_KEY') or getattr(settings, 'deepseek_api_key', None)
        if not deepseek_key or deepseek_key == "your_deepseek_api_key_here":
            errors.append("DeepSeek API key not configured")
        else:
            logger.info(f"✅ DeepSeek API Key: {deepseek_key[:10]}...")
        
        # Cek Telegram Token
        telegram_token = os.getenv('TELEGRAM_TOKEN') or getattr(settings, 'telegram_token', None)
        if not telegram_token or telegram_token == "your_telegram_bot_token_here":
            errors.append("Telegram token not configured")
        else:
            logger.info(f"✅ Telegram Token: {telegram_token[:10]}...")
        
        # Cek Admin ID
        admin_id = os.getenv('ADMIN_ID') or getattr(settings, 'admin_id', 0)
        if admin_id == 0 or admin_id == "0":
            logger.warning("⚠️ Admin ID not configured")
        else:
            logger.info(f"✅ Admin ID: {admin_id}")
            
    except Exception as e:
        errors.append(f"Failed to load config: {e}")
    
    # Create directories
    required_dirs = [
        'data', 'data/logs', 'data/backups', 
        'data/sessions', 'data/vector_db', 'data/memory'
    ]
    
    for dir_name in required_dirs:
        dir_path = Path(dir_name)
        dir_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"✅ Directory: {dir_name}")
    
    if errors:
        logger.error("\n❌ ERRORS FOUND:")
        for err in errors:
            logger.error(f"   - {err}")
        return False
    
    logger.info("\n✅ Environment is ready!")
    return True


def run_migration() -> bool:
    """Run database migration"""
    logger.info("\n" + "=" * 60)
    logger.info("🗄️ RUNNING DATABASE MIGRATION")
    logger.info("=" * 60)
    
    try:
        # Import migration module
        import importlib.util
        migrate_path = Path("database/migrate.py")
        if not migrate_path.exists():
            logger.warning("⚠️ Migration file not found")
            return True
        
        spec = importlib.util.spec_from_file_location("migrate_module", migrate_path)
        migrate_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(migrate_module)
        
        # Run migration
        if hasattr(migrate_module, 'run_migrations'):
            success = asyncio.run(migrate_module.run_migrations())
        elif hasattr(migrate_module, 'migrate'):
            success = migrate_module.migrate()
        else:
            success = True
        
        if success:
            logger.info("✅ Migration completed")
            return True
        else:
            logger.error("❌ Migration failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def start_bot() -> bool:
    """Start the bot"""
    logger.info("\n" + "=" * 60)
    logger.info("🚀 STARTING AMORIA")
    logger.info("=" * 60)
    
    try:
        from main import main
        asyncio.run(main())
        return True
    except KeyboardInterrupt:
        logger.info("\n👋 Bot stopped")
        return True
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main runner untuk deployment"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     💜 AMORIA - Virtual Human dengan Jiwa                       ║
║     Deployment Mode (Railway)                                   ║
║                                                                  ║
║     🔧 Automatic Setup:                                         ║
║     • Checking environment variables                           ║
║     • Creating directories                                      ║
║     • Running database migration                                ║
║     • Starting bot                                              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check environment
    if not check_environment():
        logger.error("Environment check failed. Please set environment variables.")
        sys.exit(1)
    
    # Step 2: Run migration
    if not run_migration():
        logger.warning("Migration failed, but continuing...")
    
    # Step 3: Start bot
    logger.info("\n" + "=" * 60)
    logger.info("🚀 STARTING BOT...")
    logger.info("Press Ctrl+C to stop")
    logger.info("=" * 60)
    
    start_bot()


if __name__ == "__main__":
    main()
