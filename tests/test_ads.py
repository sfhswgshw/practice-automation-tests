"""Тесты страницы «Ads» — https://practice-automation.com/ads/"""

from __future__ import annotations

import allure
import pytest
from selenium.common.exceptions import ElementClickInterceptedException

from pages.ads_page import AdsPage

# На сайте задана задержка автопоказа 4 500 мс; берём небольшой запас снизу.
MIN_AD_DELAY_MS = 4000
MAX_AD_DELAY_MS = 20000

pytestmark = [allure.epic("UI practice-automation.com"), allure.feature("Рекламные окна")]


@allure.story("Позитивные сценарии")
@pytest.mark.positive
class TestAdsPositive:
    @pytest.mark.smoke
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-ADS-01. Страница рекламы открывается и содержит предупреждение об отсчёте")
    def test_page_content(self, ads_page: AdsPage):
        with allure.step("Проверить заголовок и текст страницы"):
            assert ads_page.heading == "Ads"
            assert ads_page.countdown_text == "An ad will appear in 5…4…3…2…1"

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-ADS-02. Реклама появляется автоматически с задержкой около 5 секунд")
    def test_ad_appears_automatically_after_delay(self, ads_page: AdsPage):
        delay_ms = ads_page.wait_ad_and_measure_delay()
        with allure.step(f"Проверить, что задержка ({delay_ms:.0f} мс) в диапазоне "
                         f"{MIN_AD_DELAY_MS}–{MAX_AD_DELAY_MS} мс"):
            assert MIN_AD_DELAY_MS <= delay_ms <= MAX_AD_DELAY_MS

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-ADS-03. Содержимое рекламного окна")
    def test_ad_content(self, ads_page: AdsPage):
        ad = ads_page.wait_ad()
        with allure.step("Проверить заголовок, текст и кнопку закрытия"):
            assert ad.title == "Hi"
            assert ad.content_text == "I am an ad."
            assert ad.is_close_button_displayed()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-ADS-04. Открытая реклама перекрывает содержимое страницы")
    def test_ad_overlay_covers_page(self, ads_page: AdsPage):
        with allure.step("До появления рекламы текст страницы доступен"):
            if not ads_page.ad.is_opened():
                assert not ads_page.is_page_content_covered()
        ads_page.wait_ad()
        with allure.step("После появления рекламы текст страницы перекрыт оверлеем"):
            assert ads_page.is_page_content_covered()

    @allure.severity(allure.severity_level.BLOCKER)
    @allure.title("TC-ADS-05. Закрытие рекламы кнопкой «×»")
    def test_close_ad(self, ads_page: AdsPage):
        ad = ads_page.wait_ad()
        ad.close()
        ad.wait_closed()
        with allure.step("Проверить, что реклама закрыта"):
            assert not ad.is_opened()

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-ADS-06. После закрытия рекламы страница снова доступна для работы")
    def test_page_is_accessible_after_closing_ad(self, ads_page: AdsPage):
        ad = ads_page.wait_ad()
        ad.close()
        ad.wait_closed()
        with allure.step("Проверить, что оверлей не перекрывает текст и ссылку"):
            assert not ads_page.is_page_content_covered()
            assert ads_page.is_element_on_top(ads_page.how_to_link)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-ADS-07. После перезагрузки страницы реклама показывается снова")
    def test_ad_appears_again_after_reload(self, ads_page: AdsPage):
        ad = ads_page.wait_ad()
        ad.close()
        ad.wait_closed()
        ads_page.reload()
        ads_page.wait_ad()
        with allure.step("Проверить, что реклама снова открыта"):
            assert ad.is_opened()
            assert ad.title == "Hi"


@allure.story("Негативные сценарии")
@pytest.mark.negative
class TestAdsNegative:
    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-ADS-N1. Реклама не закрывается клавишей Esc")
    def test_ad_is_not_closed_by_escape(self, ads_page: AdsPage):
        ad = ads_page.wait_ad()
        ad.press_escape()
        with allure.step("Проверить, что реклама осталась открытой"):
            assert ad.stays_opened(2)

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-ADS-N2. Реклама не закрывается кликом по затемнённой области")
    def test_ad_is_not_closed_by_overlay_click(self, ads_page: AdsPage):
        ad = ads_page.wait_ad()
        ad.click_on_overlay()
        with allure.step("Проверить, что реклама осталась открытой"):
            assert ad.stays_opened(2)

    @allure.severity(allure.severity_level.CRITICAL)
    @allure.title("TC-ADS-N3. Пока открыта реклама, элементы страницы недоступны для клика")
    def test_page_link_is_not_clickable_while_ad_opened(self, ads_page: AdsPage):
        ads_page.wait_ad()
        windows_before = len(ads_page.driver.window_handles)
        with allure.step("Попытаться кликнуть по ссылке под рекламой — клик перехватывает оверлей"):
            with pytest.raises(ElementClickInterceptedException):
                ads_page.click_how_to_link()
        with allure.step("Проверить, что ссылка не открылась и реклама на месте"):
            assert len(ads_page.driver.window_handles) == windows_before
            assert ads_page.ad.is_opened()

    @allure.severity(allure.severity_level.NORMAL)
    @allure.title("TC-ADS-N4. Закрытая реклама не появляется повторно без перезагрузки страницы")
    def test_ad_does_not_reappear_after_closing(self, ads_page: AdsPage):
        ad = ads_page.wait_ad()
        ad.close()
        ad.wait_closed()
        with allure.step("Подождать дольше задержки автопоказа"):
            assert ad.stays_closed(7), "Реклама появилась повторно"
