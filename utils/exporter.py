# Сохранение в CSV/Excel
import pandas as pd
from datetime import datetime
from typing import List
from core.models import Lead
from utils.logger import logger

def save_to_excel(leads: List[Lead], filename_prefix: str = "leads"):
    if not leads:
        logger.warning("Нет данных для сохранения!")
        return

    try:
        # Pydantic v2 использует model_dump() для конвертации в словарь
        data = [lead.model_dump() for lead in leads]

        df = pd.DataFrame(data)

        # Переименуем колонки для красоты в Excel
        # Переименуем колонки для красоты в Excel
        df.rename(columns={
            "name": "Название",
            "phone": "Телефон",
            "address": "Адрес",
            "website": "Сайт",
            "vk_link": "ВКонтакте",
            "yandex_url": "Ссылка на Яндекс",
            "tg_link": "Ссылка на Telegram"   # <--- ДОБАВЬ ЭТУ СТРОКУ
        }, inplace=True)

        # Генерируем имя файла с текущей датой и временем
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{filename_prefix}_{timestamp}.xlsx"

        # Сохраняем
        df.to_excel(filename, index=False, engine='openpyxl')
        logger.success(f"Данные успешно сохранены в файл: {filename}")

    except Exception as e:
        logger.error(f"Ошибка при сохранении в Excel: {e}")