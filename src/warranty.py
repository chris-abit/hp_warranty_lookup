import time
from pathlib import Path
from datetime import datetime, date
from itertools import chain, batched
import pandas as pd
from selenium.webdriver import Firefox()
from selenium.common import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


WARRANTY_URL = "https://support.hp.com/us-en/check-warranty#multiple"



def initialize_browser():
    """
    Start selenium browser and load hp warranty page.
    Will accept all cookies.
    """
    fpath = Path(__file__).parent.resolve()
    ublock = fpath / "ublock.xpi"
    errors = [NoSuchElementException, ElementNotInteractableException]
    cookie_elem = "onetrust-accept-btn-handler"
    driver = Firefox()
    driver.implicitly_wait(4)
    driver.install_addon(ublock)
    driver.get(WARRANTY_URL)
    wait = WebDriverWait(driver, timeout=8, ignored_exceptions=errors)
    wait.until(
        lambda d : driver.find_element(By.ID, cookie_elem).click()
        or True
    )
    time.sleep(2)  # Wait for cookie prompt to dissapear.
    return driver
