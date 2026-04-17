from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8501"


@pytest.fixture(autouse=True)
def navigate(page: Page) -> None:
    page.goto(BASE_URL)
    page.wait_for_selector(".stApp", timeout=30000)
    page.wait_for_timeout(3000)


def test_sidebar_renders(page: Page) -> None:
    expect(page.get_by_text("Norsk Elektrisitet")).to_be_visible()
    expect(page.get_by_text("Kapasitet")).to_be_visible()
    expect(page.get_by_text("Volum")).to_be_visible()


def test_kapasitet_mode_tabs(page: Page) -> None:
    expect(page.get_by_text("Kart")).to_be_visible()
    expect(page.get_by_text("Historikk")).to_be_visible()
    expect(page.get_by_text("Topp kommuner")).to_be_visible()


def test_map_renders(page: Page) -> None:
    expect(page.locator("iframe")).to_be_visible()
    expect(page.locator(".stException")).not_to_be_visible()


def test_map_no_raw_codes(page: Page) -> None:
    page_text = page.locator(".stApp").inner_text()
    assert "E18" not in page_text
    assert "E19" not in page_text


def test_deselect_all_groups_shows_info(page: Page) -> None:
    tags = page.locator("[data-baseweb='tag'] span[aria-label]")
    count = tags.count()
    for _ in range(count):
        page.locator("[data-baseweb='tag'] span[aria-label]").first.click()
        page.wait_for_timeout(300)
    expect(page.get_by_text("Velg minst én produksjonstype.")).to_be_visible()


def test_historikk_tab_auto_fetches(page: Page) -> None:
    page.get_by_text("Historikk").click()
    page.wait_for_timeout(15000)
    expect(page.locator(".js-plotly-plot")).to_be_visible()


def test_leaders_tab_renders(page: Page) -> None:
    page.get_by_text("Topp kommuner").click()
    page.wait_for_timeout(2000)
    expect(page.locator(".js-plotly-plot").first).to_be_visible()
    expect(page.locator(".stException")).not_to_be_visible()
