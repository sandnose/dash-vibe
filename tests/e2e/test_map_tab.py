from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://localhost:8501"


@pytest.fixture(autouse=True)
def navigate(page: Page) -> None:
    page.goto(BASE_URL)
    # Wait for Streamlit to finish loading
    page.wait_for_selector(".stApp", timeout=30000)
    page.wait_for_timeout(3000)  # allow data fetch to complete


def test_map_tab_loads(page: Page) -> None:
    """Map tab is active by default and renders without errors."""
    expect(page.locator(".stApp")).to_be_visible()
    # No error messages visible
    expect(page.locator(".stException")).not_to_be_visible()


def test_map_tab_has_controls(page: Page) -> None:
    """Sidebar has production source multiselect and scale radio."""
    expect(page.get_by_text("Production source")).to_be_visible()
    expect(page.get_by_text("Scale")).to_be_visible()


def test_map_tab_has_snapshot_date(page: Page) -> None:
    """Snapshot date label is shown."""
    expect(page.get_by_text("Snapshot date:")).to_be_visible()


def test_map_tab_folium_renders(page: Page) -> None:
    """Folium iframe is present (map rendered)."""
    expect(page.locator("iframe")).to_be_visible()


def test_deselect_all_groups_shows_info(page: Page) -> None:
    """Deselecting all production groups shows info message, not error."""
    # Clear multiselect by removing all tags
    tags = page.locator("[data-baseweb='tag'] span[aria-label]")
    count = tags.count()
    for _ in range(count):
        page.locator("[data-baseweb='tag'] span[aria-label]").first.click()
        page.wait_for_timeout(300)
    expect(page.get_by_text("Select at least one production source.")).to_be_visible()
