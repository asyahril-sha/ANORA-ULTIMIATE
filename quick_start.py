# quick_start.py
# -*- coding: utf-8 -*-
"""
=============================================================================
AMORIA - Virtual Human dengan Jiwa
Quick Start - Setup Cepat untuk Pemula
=============================================================================
"""

import os
import sys
import subprocess
from pathlib import Path

print("""
╔══════════════════════════════════════════════════════════════════╗
║     💜 AMORIA - QUICK START                                     ║
║                                                                  ║
║     Virtual Human dengan Jiwa                                   ║
║                                                                  ║
║     This script will:                                           ║
║     1. Install dependencies                                     ║
║     2. Setup .env file                                          ║
║     3. Run database migration                                   ║
║     4. Start the bot                                            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")


def install_dependencies() -> bool:
    """Install dependencies from requirements.txt"""
    print("\n📦 Installing dependencies...")
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], 
                      capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ pip not found. Please install pip first.")
        return False
    
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("✅ Dependencies installed")
        return True
    else:
        print("❌ Failed to install dependencies")
        print(result.stderr)
        return False


def setup_env() -> bool:
    """Setup .env file"""
    print("\n🔧 Setting up .env file...")
    
    if Path(".env").exists():
        print("⚠️ .env already exists. Do you want to overwrite?")
        response = input("Overwrite? (y/n) [n]: ").strip().lower()
        if response != 'y':
            print("Skipping .env setup")
            return True
    
    print("\nPlease enter your credentials:")
    telegram_token = input("Telegram Bot Token (from @BotFather): ").strip()
    deepseek_key = input("DeepSeek API Key: ").strip()
    admin_id = input("Admin Telegram ID (from @userinfobot): ").strip()
    
    with open(".env", "w") as f:
        f.write(f"""# AMORIA - Environment Variables
TELEGRAM_TOKEN={telegram_token}
DEEPSEEK_API_KEY={deepseek_key}
ADMIN_ID={admin_id}

# Database
DB_PATH=data/amoria.db

# AI Configuration
AI_TEMPERATURE=0.95
AI_MAX_TOKENS=4000

# Feature Toggles
SEXUAL_CONTENT_ENABLED=true
MEMORY_ENABLED=true
EMOTIONAL_FLOW_ENABLED=true
SPATIAL_AWARENESS_ENABLED=true
ROLE_BEHAVIOR_ENABLED=true
""")
    
    print("✅ .env file created")
    return True


def run_migration() -> bool:
    """Run database migration"""
    print("\n🗄️ Running database migration...")
    try:
        from database.migrate import run_migrations
        import asyncio
        
        success = asyncio.run(run_migrations())
        
        if success:
            print("✅ Migration completed")
            return True
        else:
            print("❌ Migration failed")
            return False
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False


def start_bot() -> bool:
    """Start the bot"""
    print("\n🚀 Starting bot...")
    print("Press Ctrl+C to stop\n")
    
    try:
        from main import main
        import asyncio
        asyncio.run(main())
        return True
    except KeyboardInterrupt:
        print("\n👋 Bot stopped")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    print("\n" + "=" * 60)
    print("QUICK START SETUP")
    print("=" * 60)
    
    # Step 1: Install dependencies
    print("\n📦 Step 1/4: Installing dependencies...")
    if not install_dependencies():
        print("\n❌ Setup failed. Please install dependencies manually:")
        print("   pip install -r requirements.txt")
        return
    
    # Step 2: Setup .env
    print("\n🔧 Step 2/4: Setting up configuration...")
    if not setup_env():
        print("\n❌ Setup failed. Please create .env manually")
        return
    
    # Step 3: Run migration
    print("\n🗄️ Step 3/4: Initializing database...")
    if not run_migration():
        print("\n⚠️ Migration failed, but continuing...")
    
    # Step 4: Start bot
    print("\n🚀 Step 4/4: Starting AMORIA...")
    print("\n" + "=" * 60)
    print("AMORIA is starting...")
    print("=" * 60)
    
    start_bot()


if __name__ == "__main__":
    main()
