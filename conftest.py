"""Общие фикстуры и хуки pytest."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import allure
import pytest
from selenium.webdriver.remote.webdriver import WebDriver

from config import settings
from pages.ads_page import AdsPage
from pages.calendar_page import CalendarPage
from pages.form_fields_page import FormFieldsPage
from pages.modals_page import ModalsPage
from utils.allure_helpers import attach_page_state
from utils.driver_factory import create_driver


# ---------------------------------------------------------------- параметры CLI
def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup("ui", "Настройки UI-тестов")
    group.addoption(
        "--browser",
        action="store",
        default=settings.browser,
        choices=("chrome", "firefox"),
        help="Браузер для запуска тестов (по умолчанию chrome)",
    )
    group.addoption(
        "--headed",
        action="store_true",
        default=not settings.headless,
        help="Запустить браузер с окном (по умолчанию — headless)",
    )
    group.addoption(
        "--site-url",
        action="store",
        default=settings.base_url,
        help="Адрес тестируемого сайта",
    )


# ---------------------------------------------------------------- фикстуры
@pytest.fixture(scope="session")
def site_url(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--site-url").rstrip("/")


@pytest.fixture
def driver(request: pytest.FixtureRequest) -> Iterator[WebDriver]:
    """Новый браузер на каждый тест — тесты полностью независимы друг от друга."""
    browser = request.config.getoption("--browser")
    with allure.step(f"Запустить браузер {browser}"):
        web_driver = create_driver(
            browser,
            headless=not request.config.getoption("--headed"),
            width=settings.window_width,
            height=settings.window_height,
            block_ads=settings.block_third_party_ads,
            page_load_timeout=settings.page_load_timeout,
        )
    yield web_driver
    web_driver.quit()


@pytest.fixture
def calendar_page(driver: WebDriver, site_url: str) -> CalendarPage:
    return CalendarPage(driver, site_url).open()


@pytest.fixture
def modals_page(driver: WebDriver, site_url: str) -> ModalsPage:
    return ModalsPage(driver, site_url).open()


@pytest.fixture
def ads_page(driver: WebDriver, site_url: str) -> AdsPage:
    return AdsPage(driver, site_url).open()


@pytest.fixture
def form_fields_page(driver: WebDriver, site_url: str) -> FormFieldsPage:
    return FormFieldsPage(driver, site_url).open()


# ---------------------------------------------------------------- хуки
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """При падении теста прикладываем к Allure скриншот, URL и HTML страницы."""
    outcome = yield
    report = outcome.get_result()
    if report.when in ("setup", "call") and report.failed:
        web_driver = item.funcargs.get("driver") if hasattr(item, "funcargs") else None
        if web_driver is not None:
            attach_page_state(web_driver)


def pytest_sessionfinish(session: pytest.Session) -> None:
    """Пишем environment.properties — блок «Environment» на главной отчёта Allure."""
    results_dir = session.config.getoption("--alluredir", default=None)
    if not results_dir or not os.path.isdir(results_dir):
        return
    config = session.config
    lines = {
        "Browser": config.getoption("--browser"),
        "Headless": str(not config.getoption("--headed")),
        "Base.URL": config.getoption("--site-url"),
        "Window.Size": f"{settings.window_width}x{settings.window_height}",
        "Block.Third.Party.Ads": str(settings.block_third_party_ads),
    }
    Path(results_dir, "environment.properties").write_text(
        "\n".join(f"{key}={value}" for key, value in lines.items()), encoding="utf-8"
    )
