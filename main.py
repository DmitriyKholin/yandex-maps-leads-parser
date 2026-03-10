import asyncio
from scrapers.yandex_maps import YandexMapsScraper
from utils.exporter import save_to_excel
from utils.logger import logger

async def main():
    # Ввод данных для поиска
    query = input("Введите нишу (например, 'салоны красоты', 'доставка еды'): ")
    city = input("Введите город (например, 'Москва', 'Казань'): ")

    logger.info("Запуск парсера...")

    # Инициализируем наш скрапер
    scraper = YandexMapsScraper()

    # Запускаем парсинг
    leads = await scraper.parse(query=query, city=city)

    # Если что-то нашли — сохраняем
    if leads:
        logger.info(f"Всего собрано лидов: {len(leads)}")
        save_to_excel(leads, filename_prefix=f"{query}_{city}".replace(" ", "_"))
    else:
        logger.warning("Парсер не нашел ни одной карточки.")

if __name__ == "__main__":
    try:
        # Убрали хак с политиками. Стандартный asyncio.run() сам во всем разберется.
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Парсинг остановлен пользователем.")