"""Страница «Ads»: https://practice-automation.com/ads/

Через ~5 секунд после загрузки страницы автоматически открывается
рекламное окно Popup Maker (id 1272) с заголовком «Hi» и текстом «I am an ad.».
"""

from __future__ import annotations

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from pages.base_page import BasePage
from pages.components.popup import Popup

AD_POPUP_ID = 1272


class AdsPage(BasePage):
    PATH = "/ads/"

    # Ожидание рекламы: задержка на сайте 4,5 с + время на загрузку скриптов.
    AD_APPEAR_TIMEOUT = 20

    COUNTDOWN_TEXT = (By.XPATH, "//div[contains(@class,'entry-content')]/p[1]")
    CONTENT_PARAGRAPHS = (By.CSS_SELECTOR, ".entry-content p")
    HOW_TO_LINK = (By.CSS_SELECTOR, ".entry-content a[href*='youtube.com']")

    def __init__(self, driver: WebDriver, base_url: str | None = None) -> None:
        super().__init__(driver, base_url)
        self.ad = Popup(driver, AD_POPUP_ID, "Реклама")

    @property
    def countdown_text(self) -> str:
        return self.text_of(self.COUNTDOWN_TEXT)

    @property
    def how_to_link(self) -> WebElement:
        return self.find(self.HOW_TO_LINK)

    def wait_ad(self) -> Popup:
        self.ad.wait_opened(self.AD_APPEAR_TIMEOUT)
        return self.ad

    def wait_ad_and_measure_delay(self) -> float:
        """Ждёт рекламу и возвращает, через сколько мс от начала загрузки она открылась.

        Время берётся из performance.now() самой страницы, поэтому не зависит
        от того, сколько длилась загрузка в WebDriver. Опрос идёт каждые 100 мс,
        так что измеренное значение может быть больше реального не более чем
        на ~0,1 с, но никогда не меньше.
        """
        with allure.step("Дождаться автоматического появления рекламы и замерить задержку"):
            self.wait(self.AD_APPEAR_TIMEOUT, poll=0.1).until(
                lambda _: self.ad.is_opened(), message="Реклама не появилась"
            )
            delay = self.ms_since_navigation_start()
            allure.attach(f"{delay:.0f} мс", name="Задержка появления рекламы")
            return delay

    @allure.step("Кликнуть по ссылке в тексте страницы")
    def click_how_to_link(self) -> None:
        link = self.how_to_link
        self.scroll_into_view(link)
        link.click()

    def is_page_content_covered(self) -> bool:
        """True, если текст страницы перекрыт каким-либо слоем (оверлеем рекламы)."""
        return not self.is_element_on_top(self.find(self.COUNTDOWN_TEXT))
