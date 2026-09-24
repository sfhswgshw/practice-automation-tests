"""Настройки запуска тестов.

Значения берутся из переменных окружения (удобно для CI) и могут быть
переопределены параметрами командной строки pytest (см. conftest.py).
"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    base_url: str = os.getenv("BASE_URL", "https://practice-automation.com").rstrip("/")
    browser: str = os.getenv("BROWSER", "chrome").lower()
    headless: bool = _env_bool("HEADLESS", True)
    # Блокировать сторонние рекламные сети Google (AdSense/DoubleClick) в Chrome.
    # Всплывающая «реклама» на /ads/ — это собственный попап сайта (Popup Maker),
    # поэтому блокировка на неё не влияет, но делает тесты стабильнее:
    # баннеры Google не перекрывают элементы и не замедляют загрузку страниц.
    block_third_party_ads: bool = _env_bool("BLOCK_ADS", True)
    window_width: int = int(os.getenv("WINDOW_WIDTH", "1920"))
    window_height: int = int(os.getenv("WINDOW_HEIGHT", "1080"))
    # Явное ожидание по умолчанию, секунды.
    timeout: int = int(os.getenv("TIMEOUT", "15"))
    page_load_timeout: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "60"))


settings = Settings()
