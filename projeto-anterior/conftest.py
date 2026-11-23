"""Fixtures do projeto anterior (produtos-web).
BASE_URL (padrão http://localhost:4173 = vite preview), API_URL (padrão http://localhost:3000),
HEADLESS=1, CI=1, CHROMEDRIVER, CHROME_BINARY."""
from pathlib import Path
import os, re
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


@pytest.fixture
def base_url():
    return os.getenv("BASE_URL", "http://localhost:4173")


@pytest.fixture
def api_url():
    return os.getenv("API_URL", "http://localhost:3000")


@pytest.fixture
def driver():
    o = webdriver.ChromeOptions()
    if os.getenv("HEADLESS") == "1": o.add_argument("--headless=new")
    if os.getenv("CI") == "1": o.add_argument("--no-sandbox"); o.add_argument("--disable-dev-shm-usage")
    o.add_argument("--window-size=1280,900")
    if os.getenv("CHROME_BINARY"): o.binary_location = os.environ["CHROME_BINARY"]
    s = Service(os.environ["CHROMEDRIVER"]) if os.getenv("CHROMEDRIVER") else Service()
    d = webdriver.Chrome(options=o, service=s)
    d.implicitly_wait(0)
    yield d
    d.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if rep.when == "call" and rep.failed and "driver" in item.funcargs:
        dest = Path("evidencias"); dest.mkdir(exist_ok=True)
        item.funcargs["driver"].save_screenshot(str(dest / (re.sub(r"[^\w-]", "_", item.nodeid) + ".png")))
