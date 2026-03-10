import asyncio
import re
import random
from scrapers.base import BaseScraper
from core.models import Lead
from core.config import config
from utils.logger import logger

class YandexMapsScraper(BaseScraper):
    async def parse(self, query: str, city: str) -> list[Lead]:
        leads = []
        search_query = f"{query} {city}"

        await self.start_browser()

        try:
            logger.info(f"Ищем в Яндексе: {search_query}")
            await self.page.goto("https://yandex.ru/maps/")

            # Вводим запрос
            search_input = self.page.locator(".search-form-view__input input")
            await search_input.wait_for(timeout=config.TIMEOUT)
            await search_input.fill(search_query)
            await search_input.press("Enter")

            # Ждем появления списка результатов
            await self.page.wait_for_selector(".search-snippet-view", timeout=15000)
            await asyncio.sleep(2)

            # Скроллим левое меню вниз для подгрузки результатов
            logger.info("Прокручиваем список для подгрузки результатов...")
            sidebar = self.page.locator('.scroll__container')

            for _ in range(config.SCROLL_RETRIES):
                await sidebar.press("PageDown")
                await asyncio.sleep(1)

            # Собираем ссылки на карточки (с правильным форматом /maps/org/)
            link_elements = await self.page.locator("a[href*='/org/']").all()
            clean_links = set()

            for el in link_elements:
                href = await el.get_attribute("href")
                if href:
                    # Вытаскиваем только чистую ссылку на карточку
                    match = re.search(r'/org/([^/]+/\d+)', href)
                    if match:
                        clean_links.add(f"https://yandex.ru/maps/org/{match.group(1)}/")

            links = list(clean_links)
            logger.info(f"Собрано {len(links)} уникальных заведений. Начинаем обход.")

            # Обходим ВСЕ собранные ссылки
            for link in links:
                card_page = await self.context.new_page()
                try:
                    await card_page.goto(link, timeout=30000)

                    # Имитируем человека: пауза
                    await asyncio.sleep(random.uniform(1.5, 3.0))

                    # 1. Парсим Название
                    name = "Не указано"
                    try:
                        name_el = card_page.locator("h1.orgpage-header-view__header")
                        if await name_el.is_visible(timeout=3000):
                            name = await name_el.inner_text()
                    except Exception:
                        pass

                    # 2. Парсим Телефон и вычисляем Telegram
                    phone = None
                    tg_link = None
                    try:
                        show_phone_btn = card_page.locator("text='Показать телефон'").first
                        if await show_phone_btn.is_visible(timeout=2000):
                            await show_phone_btn.click()
                            await asyncio.sleep(0.5)

                        phone_el = card_page.locator(".card-phones-view__phone-number").first
                        if await phone_el.is_visible(timeout=2000):
                            raw_phone = await phone_el.inner_text()
                            phone = raw_phone.split('\n')[0].strip() # Берем только сам номер

                            # === ЛОГИКА ОПРЕДЕЛЕНИЯ МОБИЛЬНОГО ===
                            # Оставляем только цифры
                            digits = re.sub(r'\D', '', phone)

                            # Проверяем, что это мобильный РФ (11 цифр, начинается с 79 или 89)
                            if len(digits) == 11 and (digits.startswith('79') or digits.startswith('89')):
                                # Приводим к формату 79...
                                if digits.startswith('8'):
                                    digits = '7' + digits[1:]
                                tg_link = f"https://t.me/+{digits}"
                            else:
                                tg_link = "Городской (нет ТГ)"

                    except Exception:
                        pass

                    # 3. Парсим Сайт или ВК
                    website = None
                    vk_link = None
                    try:
                        social_links = await card_page.locator(".business-urls-view__link").all()
                        for s_link in social_links:
                            href = await s_link.get_attribute("href")
                            if href:
                                if "vk.com" in href:
                                    vk_link = href
                                else:
                                    website = href
                    except Exception:
                        pass

                    # Создаем модель лида
                    lead = Lead(
                        name=name,
                        phone=phone,
                        website=website,
                        vk_link=vk_link,
                        yandex_url=link,
                        tg_link=tg_link  # Передаем ссылку на ТГ
                    )
                    leads.append(lead)

                    # Логируем красиво: мобильный или городской
                    tg_status = "📱 Мобильный" if tg_link and "t.me" in tg_link else "☎️ Городской"
                    logger.success(f"Спарсили: {name} | {phone} [{tg_status}]")

                except Exception as e:
                    logger.error(f"Ошибка карточки {link}: {e}")

                finally:
                    # Закрываем вкладку, чтобы не перегружать ОЗУ
                    await card_page.close()

        except Exception as e:
            logger.error(f"Глобальная ошибка парсинга: {e}")

        finally:
            await self.close_browser()

        return leads