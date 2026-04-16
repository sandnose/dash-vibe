from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8501"


@pytest.fixture(autouse=True)
def navigate_to_history(page: Page) -> None:
    page.goto(BASE_URL)
    page.wait_for_selector(".stApp", timeout=30000)
    page.wait_for_timeout(3000)
    # Click History tab
    page.get_by_text("📈 History").click()
    page.wait_for_timeout(500)


def test_history_tab_loads(page: Page) -> None:
    """History tab renders without errors."""
    expect(page.locator(".stException")).not_to_be_visible()


def test_history_no_auto_fetch(page: Page) -> None:
    """Chart does not appear before Load history is clicked."""
    expect(page.get_by_text("Select a municipality and click")).to_be_visible()


def test_history_load_button_triggers_fetch(page: Page) -> None:
    """Clicking Load history triggers a chart render."""
    page.get_by_role("button", name="Load history").click()
    # Wait for spinner to disappear and chart to appear
    page.wait_for_timeout(15000)
    expect(page.locator(".js-plotly-plot")).to_be_visible()
