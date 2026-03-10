# Базовый класс парсера
from playwright.async_api import async_playwright
from core.config import config
from utils.logger import logger

class BaseScraper:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    async def start_browser(self):
        logger.info("Запускаем браузер...")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=config.HEADLESS_MODE)

        # Подменяем User-Agent, чтобы не выглядеть как дефолтный бот Playwright
        self.context = await self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = await self.context.new_page()

    async def close_browser(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        logger.info("Браузер закрыт.")