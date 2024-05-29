import time
from pathlib import Path
from datetime import datetime, date
from itertools import chain, batched
import pandas as pd
import numpy as np
from selenium.webdriver import Firefox
from selenium.common import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


WARRANTY_URL = "https://support.hp.com/us-en/check-warranty#multiple"


def products_read():
    """
    Read products from hp_products.csv.
    Drops any entries missing either serial number or
    product number.
    Returns a pandas dataframe.
    """
    columns = [
        "serial_number",
        "product_number",
    ]
    info_cols = [
        "warranty_start",
        "warranty_end",
        "url",
    ]
    products_data = "hp_products.csv"
    df = pd.read_csv(products_data)
    if not np.array_equal(df.columns, columns):
        raise ValueError(f"The columns {columns} are required!")
    df = df.dropna()
    df[info_cols] = None
    return df


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


def hp_warranty_get():
    """
    Retreive warranties for HP computers from hp warranty page.
    """
    driver = initialize_browser()
    driver.quit()


if __name__ == "__main__":
    load()
