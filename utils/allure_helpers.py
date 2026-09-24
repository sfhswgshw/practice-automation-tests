"""Вспомогательные функции для отчёта Allure."""

from __future__ import annotations

import allure
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.remote.webdriver import WebDriver


def attach_screenshot(driver: WebDriver, name: str = "Скриншот") -> None:
    try:
        allure.attach(
            driver.get_screenshot_as_png(),
            name=name,
            attachment_type=allure.attachment_type.PNG,
        )
    except WebDriverException:
        # Например, открыт alert — скриншот сделать нельзя, это не должно ронять отчёт.
        pass


def attach_page_state(driver: WebDriver) -> None:
    """Прикладывает к отчёту всё, что помогает разобрать падение."""
    attach_screenshot(driver, "Скриншот при ошибке")
    try:
        allure.attach(driver.current_url, name="URL", attachment_type=allure.attachment_type.URI_LIST)
        allure.attach(
            driver.page_source,
            name="HTML страницы",
            attachment_type=allure.attachment_type.HTML,
        )
    except WebDriverException:
        pass
