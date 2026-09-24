"""Создание экземпляра WebDriver.

Драйверы браузеров (chromedriver / geckodriver) скачиваются автоматически
встроенным в Selenium 4 менеджером Selenium Manager, поэтому ничего
устанавливать вручную не нужно — достаточно установленного Chrome или Firefox.
"""

from __future__ import annotations

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver

# Домены сторонней рекламы Google, которые перенаправляются в «никуда» в Chrome.
_AD_HOSTS = (
    "pagead2.googlesyndication.com",
    "*.googlesyndication.com",
    "*.doubleclick.net",
    "*.googleadservices.com",
    "adservice.google.com",
    "*.adtrafficquality.google",
    "fundingchoicesmessages.google.com",
)


def _chrome(headless: bool, width: int, height: int, block_ads: bool) -> WebDriver:
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument(f"--window-size={width},{height}")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-search-engine-choice-screen")
    options.add_argument("--no-first-run")
    options.add_argument("--lang=en-US")
    # Нужны в Docker/CI-окружениях, локально не мешают.
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    if block_ads:
        rules = ", ".join(f"MAP {host} 127.0.0.1" for host in _AD_HOSTS)
        options.add_argument(f"--host-resolver-rules={rules}")
    return webdriver.Chrome(options=options)


def _firefox(headless: bool, width: int, height: int) -> WebDriver:
    options = webdriver.FirefoxOptions()
    if headless:
        options.add_argument("-headless")
    options.add_argument(f"--width={width}")
    options.add_argument(f"--height={height}")
    options.set_preference("intl.accept_languages", "en-US, en")
    options.set_preference("dom.webnotifications.enabled", False)
    driver = webdriver.Firefox(options=options)
    driver.set_window_size(width, height)
    return driver


def create_driver(
    browser: str,
    *,
    headless: bool,
    width: int,
    height: int,
    block_ads: bool,
    page_load_timeout: int,
) -> WebDriver:
    browser = browser.lower()
    if browser == "chrome":
        driver = _chrome(headless, width, height, block_ads)
    elif browser == "firefox":
        driver = _firefox(headless, width, height)
    else:
        raise ValueError(f"Неподдерживаемый браузер: {browser!r}. Доступно: chrome, firefox")
    driver.set_page_load_timeout(page_load_timeout)
    return driver
