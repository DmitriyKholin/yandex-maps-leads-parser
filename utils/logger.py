# Настройка логирования
import sys
from loguru import logger

# Удаляем стандартный обработчик и настраиваем свой
logger.remove()
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{message}</cyan>")
logger.add("logs/parser.log", rotation="10 MB", retention="10 days", level="DEBUG")

# Теперь мы будем использовать logger.info(), logger.error() вместо print()