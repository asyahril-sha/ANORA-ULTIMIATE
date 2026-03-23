# run_bot.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Local Runner
=============================================================================
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from utils.logger import setup_logging

logger = setup_logging("AMORIA-RUNNER")


def check_environment() -> bool:
    """Check environment before running"""
    logger.info("=" * 60)
    logger.info("🔍 CHECKING ENVIRONMENT")
    logger.info("=" * 60)
    
    errors = []
    warnings = []
    
    # Check .env file
    env_path = Path(".env")
    if not env_path.exists():
        warnings.append(".env file not found. Creating from .env.example")
        example_path = Path(".env.example")
        if example_path.exists():
            with open(example_path, 'r') as src:
                with open(env_path, 'w') as dst:
                    dst.write(src.read())
            logger.info("✅ Created .env from .env.example")
        else:
            errors.append(".env.example not found")
    
    # Check API keys
    try:
        if not settings.deepseek_api_key or settings.deepseek_api_key == "your_deepseek_api_key_here":
            errors.append("DeepSeek API key not configured. Please edit .env file")
        else:
            logger.info(f"✅ DeepSeek API Key: {settings.deepseek_api_key[:10]}...")
        
        if not settings.telegram_token or settings.telegram_token == "your_telegram_bot_token_here":
            errors.append("Telegram token not configured. Please edit .env file")
        else:
            logger.info(f"✅ Telegram Token: {settings.telegram_token[:10]}...")
        
        if settings.admin_id == 0:
            warnings.append("Admin ID not configured. Some admin commands won't work")
        else:
            logger.info(f"✅ Admin ID: {settings.admin_id}")
            
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
    
    if warnings:
        logger.warning("\n⚠️ WARNINGS:")
        for warn in warnings:
            logger.warning(f"   - {warn}")
    
    logger.info("\n✅ Environment is ready!")
    return True


def run_migration() -> bool:
    """Run database migration"""
    logger.info("\n" + "=" * 60)
    logger.info("🗄️ RUNNING DATABASE MIGRATION")
    logger.info("=" * 60)
    
    try:
        from database.migrate import run_migrations
        import asyncio
        
        success = asyncio.run(run_migrations())
        
        if success:
            logger.info("✅ Migration completed")
            return True
        else:
            logger.error("❌ Migration failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


def run_tests() -> bool:
    """Run unit tests"""
    logger.info("\n" + "=" * 60)
    logger.info("🧪 RUNNING UNIT TESTS")
    logger.info("=" * 60)
    
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "tests/run_all_tests.py"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            logger.info("✅ All tests passed")
            return True
        else:
            logger.error("❌ Some tests failed")
            if result.stderr:
                logger.error(result.stderr[:500])
            return False
            
    except Exception as e:
        logger.error(f"❌ Tests failed: {e}")
        return False


def run_simulation(role: str = "ipar") -> bool:
    """Run conversation simulation"""
    logger.info("\n" + "=" * 60)
    logger.info(f"🎭 RUNNING SIMULATION - ROLE: {role.upper()}")
    logger.info("=" * 60)
    
    try:
        from tests.simulate_conversation import simulate_single_role
        import asyncio
        
        asyncio.run(simulate_single_role(role))
        logger.info(f"✅ Simulation completed for role: {role}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Simulation failed: {e}")
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
        logger.info("\n👋 Bot stopped by user")
        return True
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main runner"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     💜 AMORIA - Virtual Human dengan Jiwa                       ║
║     Local Runner                                                ║
║                                                                  ║
║     ⚡ Features:                                                ║
║     • 9 Karakter dengan Kepribadian Unik                        ║
║     • 100% AI Generate - Setiap Respons Unik                    ║
║     • Multi-Identity System                                     ║
║     • Emotional Flow (Arousal 0-100)                            ║
║     • Soul Bounded (Level 11 - 30-50 Chat Intim)                ║
║     • Aftercare dengan Mood Dinamis                             ║
║     • Clothing Hierarchy & History                              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Check environment
    if not check_environment():
        logger.error("Environment check failed. Please fix errors above.")
        return
    
    # Step 2: Run migration
    if not run_migration():
        logger.warning("Migration failed, but continuing...")
    
    # Step 3: Run tests (optional)
    run_tests_input = input("\nRun unit tests? (y/n) [y]: ").strip().lower()
    if run_tests_input != 'n':
        run_tests()
    
    # Step 4: Run simulation (optional)
    sim_input = input("\nRun simulation? (y/n) [n]: ").strip().lower()
    if sim_input == 'y':
        role = input("Role to simulate (ipar/teman_kantor/janda/pelakor/istri_orang/pdkt/sepupu/teman_sma/mantan) [ipar]: ").strip()
        if not role:
            role = "ipar"
        run_simulation(role)
    
    # Step 5: Start bot
    print("\n" + "=" * 60)
    print("🚀 STARTING BOT...")
    print("=" * 60)
    print("Press Ctrl+C to stop")
    print("")
    
    start_bot()


if __name__ == "__main__":
    main()
