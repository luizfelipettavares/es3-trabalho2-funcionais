"""Fixtures do Desafio B (baseado em funcionais/conftest.py do pacote).

Variáveis: BASE_URL (padrão http://127.0.0.1:8000), HEADLESS=1, CI=1 (contêiner),
CHROMEDRIVER e CHROME_BINARY (driver/navegador fora do padrão).
"""
from pathlib import Path
import os, re
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000")


@pytest.fixture
def base_url():
    return BASE_URL


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    if os.environ.get('HEADLESS') == '1': options.add_argument('--headless=new')
    if os.environ.get('CI') == '1':
        options.add_argument('--no-sandbox'); options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1280,900')
    if os.environ.get('CHROME_BINARY'): options.binary_location = os.environ['CHROME_BINARY']
    service = Service(os.environ['CHROMEDRIVER']) if os.environ.get('CHROMEDRIVER') else Service()
    browser = webdriver.Chrome(options=options, service=service)
    browser.implicitly_wait(0)          # somente esperas explícitas
    yield browser
    browser.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when == 'call' and report.failed and 'driver' in item.funcargs:
        dest = Path('evidencias'); dest.mkdir(exist_ok=True)
        name = re.sub(r'[^a-zA-Z0-9_-]', '_', item.nodeid)
        item.funcargs['driver'].save_screenshot(str(dest / (name + '.png')))
