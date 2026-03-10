# Настройки (таймауты, прокси)
# Здесь будем хранить настройки парсера
class Config:
    HEADLESS_MODE = False
    SCROLL_RETRIES = 50     # Было 5, сделай 30 или 50! Он будет листать список дольше.
    TIMEOUT = 10000

    # Можно добавить прокси позже
    # PROXY = {"server": "http://ip:port", "username": "usr", "password": "pwd"}

config = Config()