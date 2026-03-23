# main.py
import os
import sys
import asyncio
from pathlib import Path
from aiohttp import web

sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from utils.logger import setup_logging
from bot.application import create_application

logger = setup_logging("AMORIA")


class AmoriaBot:
    def __init__(self):
        self.application = None
        logger.info("=" * 50)
        logger.info("💜 AMORIA Starting...")
        logger.info("=" * 50)
    
    async def init_application(self):
        self.application = create_application()
        await self.application.initialize()
        logger.info("✅ Bot ready")
    
    async def start(self):
        try:
            await self.init_application()
            
            await self.application.bot.delete_webhook(drop_pending_updates=True)
            await self.application.start()
            logger.info("✅ Polling started")
            
            port = int(os.getenv('PORT', 8080))
            app = web.Application()
            app.router.add_get('/health', self.health_handler)
            runner = web.AppRunner(app)
            await runner.setup()
            site = web.TCPSite(runner, '0.0.0.0', port)
            await site.start()
            
            logger.info(f"✅ Server on port {port}")
            logger.info("💜 AMORIA RUNNING!")
            
            await asyncio.Event().wait()
            
        except Exception as e:
            logger.error(f"Error: {e}")
            import traceback
            traceback.print_exc()
    
    async def health_handler(self, request):
        return web.json_response({"status": "healthy"})


if __name__ == "__main__":
    bot = AmoriaBot()
    asyncio.run(bot.start())
