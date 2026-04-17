from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8501"


@pytest.fixture(autouse=True)
def navigate_to_volum(page: Page) -> None:
    page.goto(BASE_URL)
    page.wait_for_selector(".stApp", timeout=30000)
    page.wait_for_timeout(3000)
    page.get_by_text("Volum").click()
    page.wait_for_timeout(500)


def test_volum_mode_tabs(page: Page) -> None:
    expect(page.get_by_text("Analyse")).to_be_visible()
    expect(page.locator(".stException")).not_to_be_visible()


def test_analyse_geo_level_selector(page: Page) -> None:
    expect(page.get_by_text("Prisområde")).to_be_visible()
    expect(page.get_by_text("Kommune")).to_be_visible()


def test_analyse_placeholder_before_load(page: Page) -> None:
    expect(page.get_by_text("Velg parametere")).to_be_visible()


def test_analyse_load_button_present(page: Page) -> None:
    expect(page.get_by_role("button", name="Last inn data")).to_be_visible()
