# Pydantic модели для валидации данных
from pydantic import BaseModel, HttpUrl
from typing import Optional

class Lead(BaseModel):
    name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    website: Optional[str] = None
    vk_link: Optional[str] = None
    yandex_url: str
    tg_link: Optional[str] = None

    # Pydantic сам проверит, чтобы все поля соответствовали типам