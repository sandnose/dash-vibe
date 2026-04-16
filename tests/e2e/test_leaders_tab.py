from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8501"


@pytest.fixture(autouse=True)
def navigate_to_leaders(page: Page) -> None:
    page.goto(BASE_URL)
    page.wait_for_selector(".stApp", timeout=30000)
    page.wait_for_timeout(3000)
    page.get_by_text("🏆 Leaders").click()
    page.wait_for_timeout(500)


def test_leaders_tab_loads(page: Page) -> None:
    """Leaders tab renders without errors."""
    expect(page.locator(".stException")).not_to_be_visible()


def test_leaders_has_charts(page: Page) -> None:
    """At least one Plotly chart is rendered."""
    expect(page.locator(".js-plotly-plot").first).to_be_visible()


def test_leaders_snapshot_date_shown(page: Page) -> None:
    """Snapshot date label is present."""
    expect(page.get_by_text("Based on snapshot:")).to_be_visible()
