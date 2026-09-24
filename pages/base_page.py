"""Базовый класс для всех Page Object и компонентов."""

from __future__ import annotations

import allure
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import settings

Locator = tuple[str, str]


class BaseElement:
    """Общие методы работы с элементами: ожидания, клики, ввод текста."""

    def __init__(self, driver: WebDriver, timeout: int = settings.timeout) -> None:
        self.driver = driver
        self.timeout = timeout

    # ---------- ожидания ----------
    def wait(self, timeout: float | None = None, poll: float = 0.25) -> WebDriverWait:
        # Календарь и формы перерисовывают DOM — «протухшие» элементы
        # внутри ожидания просто перепроверяем на следующей итерации.
        return WebDriverWait(
            self.driver,
            timeout if timeout is not None else self.timeout,
            poll_frequency=poll,
            ignored_exceptions=(NoSuchElementException, StaleElementReferenceException),
        )

    def find(self, locator: Locator, timeout: float | None = None) -> WebElement:
        return self.wait(timeout).until(
            EC.presence_of_element_located(locator),
            message=f"Элемент не найден: {locator}",
        )

    def find_all(self, locator: Locator) -> list[WebElement]:
        return self.driver.find_elements(*locator)

    def find_visible(self, locator: Locator, timeout: float | None = None) -> WebElement:
        return self.wait(timeout).until(
            EC.visibility_of_element_located(locator),
            message=f"Элемент не отображается: {locator}",
        )

    def wait_invisible(self, locator: Locator, timeout: float | None = None) -> bool:
        return self.wait(timeout).until(
            EC.invisibility_of_element_located(locator),
            message=f"Элемент не скрылся: {locator}",
        )

    def is_visible(self, locator: Locator, timeout: float = 0) -> bool:
        """Проверка видимости без исключения (timeout=0 — мгновенная проверка)."""
        if timeout:
            try:
                self.find_visible(locator, timeout)
                return True
            except TimeoutException:
                return False
        try:
            elements = self.find_all(locator)
            return bool(elements) and elements[0].is_displayed()
        except StaleElementReferenceException:
            return False

    def stays_invisible(self, locator: Locator, duration: float) -> bool:
        """True, если элемент так и не стал видимым за `duration` секунд."""
        try:
            self.find_visible(locator, duration)
            return False
        except TimeoutException:
            return True

    # ---------- действия ----------
    def scroll_into_view(self, element: WebElement) -> WebElement:
        # Прокрутка к центру экрана: sticky-шапка сайта не перекрывает элемент.
        # behavior: 'instant' обязателен — на сайте включён `scroll-behavior: smooth`,
        # и без него клик происходит раньше, чем закончится анимация прокрутки.
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center', inline: 'center', behavior: 'instant'});",
            element,
        )
        return element

    def click(self, locator: Locator, timeout: float | None = None) -> None:
        element = self.find_visible(locator, timeout)
        self.scroll_into_view(element)
        self.wait(timeout).until(EC.element_to_be_clickable(element)).click()

    def type_text(self, locator: Locator, text: str) -> WebElement:
        element = self.find_visible(locator)
        self.scroll_into_view(element)
        element.click()
        element.send_keys(text)
        return element

    def text_of(self, locator: Locator) -> str:
        return self.find_visible(locator).text.strip()

    def value_of(self, locator: Locator) -> str:
        return self.find(locator).get_attribute("value") or ""

    def is_element_on_top(self, element: WebElement) -> bool:
        """Проверяет, что в центре элемента нет перекрывающих его слоёв (оверлеев)."""
        self.scroll_into_view(element)
        return bool(
            self.driver.execute_script(
                """
                const el = arguments[0];
                const r = el.getBoundingClientRect();
                const top = document.elementFromPoint(r.left + r.width / 2, r.top + r.height / 2);
                return el === top || el.contains(top);
                """,
                element,
            )
        )


class BasePage(BaseElement):
    """Базовая страница сайта practice-automation.com."""

    PATH = "/"
    HEADING = (By.CSS_SELECTOR, "h1[itemprop='headline']")

    def __init__(self, driver: WebDriver, base_url: str | None = None) -> None:
        super().__init__(driver)
        self.base_url = (base_url or settings.base_url).rstrip("/")

    @property
    def url(self) -> str:
        return f"{self.base_url}{self.PATH}"

    def open(self):
        with allure.step(f"Открыть страницу {self.url}"):
            self.driver.get(self.url)
            self.find_visible(self.HEADING)
            self._disable_smooth_scroll()
        return self

    def reload(self):
        with allure.step("Перезагрузить страницу"):
            self.driver.refresh()
            self.find_visible(self.HEADING)
            self._disable_smooth_scroll()
        return self

    def _disable_smooth_scroll(self) -> None:
        """Отключает плавную прокрутку сайта, чтобы автопрокрутка WebDriver была мгновенной."""
        self.driver.execute_script("document.documentElement.style.scrollBehavior = 'auto';")

    @property
    def heading(self) -> str:
        return self.text_of(self.HEADING)

    def ms_since_navigation_start(self) -> float:
        """Сколько миллисекунд прошло с начала загрузки текущей страницы."""
        return float(self.driver.execute_script("return performance.now();"))
