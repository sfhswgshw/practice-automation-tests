"""Компонент всплывающего окна плагина Popup Maker.

Разметка окна с идентификатором N:

* ``#pum-N``            — оверлей на весь экран; при открытии получает класс ``pum-active``;
* ``#popmake-N``        — само окно (контейнер);
* ``#pum_popup_title_N``— заголовок;
* ``.pum-content``      — содержимое;
* ``.pum-close``        — кнопка закрытия «×».
"""

from __future__ import annotations

import allure
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from pages.base_page import BaseElement, Locator


class Popup(BaseElement):
    def __init__(self, driver: WebDriver, popup_id: int, name: str) -> None:
        super().__init__(driver)
        self.name = name
        self.OVERLAY: Locator = (By.ID, f"pum-{popup_id}")
        self.CONTAINER: Locator = (By.ID, f"popmake-{popup_id}")
        self.TITLE: Locator = (By.ID, f"pum_popup_title_{popup_id}")
        self.CONTENT: Locator = (By.CSS_SELECTOR, f"#popmake-{popup_id} .pum-content")
        self.CLOSE_BUTTON: Locator = (By.CSS_SELECTOR, f"#popmake-{popup_id} .pum-close")
        self.css_root = f"#pum-{popup_id}"

    # ---------- состояние ----------
    def is_opened(self) -> bool:
        overlays = self.find_all(self.OVERLAY)
        if not overlays:
            return False
        is_active = "pum-active" in (overlays[0].get_attribute("class") or "")
        return is_active and self.is_visible(self.CONTAINER)

    def wait_opened(self, timeout: float | None = None) -> None:
        with allure.step(f"Дождаться появления окна «{self.name}»"):
            self.wait(timeout).until(
                lambda _: self.is_opened(), message=f"Окно «{self.name}» не открылось"
            )

    def wait_closed(self, timeout: float | None = None) -> None:
        with allure.step(f"Дождаться закрытия окна «{self.name}»"):
            self.wait_invisible(self.OVERLAY, timeout)

    def stays_opened(self, seconds: float = 2) -> bool:
        """True, если окно оставалось открытым всё время ожидания."""
        with allure.step(f"Убедиться, что окно «{self.name}» остаётся открытым {seconds} с"):
            try:
                self.wait(seconds).until(lambda _: not self.is_opened())
                return False
            except TimeoutException:  # окно так и не закрылось
                return True

    def stays_closed(self, seconds: float) -> bool:
        with allure.step(f"Убедиться, что окно «{self.name}» не появляется {seconds} с"):
            return self.stays_invisible(self.CONTAINER, seconds)

    @property
    def title(self) -> str:
        return self.text_of(self.TITLE)

    @property
    def content_text(self) -> str:
        return self.text_of(self.CONTENT)

    def is_close_button_displayed(self) -> bool:
        return self.is_visible(self.CLOSE_BUTTON)

    @property
    def overlay(self) -> WebElement:
        return self.find(self.OVERLAY)

    # ---------- действия ----------
    def close(self) -> None:
        with allure.step(f"Закрыть окно «{self.name}» кнопкой «×»"):
            self.click(self.CLOSE_BUTTON)

    def press_escape(self) -> None:
        with allure.step("Нажать клавишу Esc"):
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()

    def click_on_overlay(self) -> None:
        """Реальный клик мышью по затемнённой области слева от окна."""
        with allure.step("Кликнуть по затемнённой области вокруг окна"):
            overlay = self.overlay
            width = overlay.size["width"]
            # В Selenium 4 смещение отсчитывается от центра элемента.
            ActionChains(self.driver).move_to_element_with_offset(
                overlay, -width // 2 + 10, 0
            ).click().perform()
