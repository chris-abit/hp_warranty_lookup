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
from utility import computers_batched, write_results


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


def send_keys(driver, row, elem_name, elem_input):
    """
    Locates a element determined by row[elem_name] and
    sends the keys from row[elem_input].
    driver: Which driver.
    row: Row in dataframe.
    elem_name: Name of element to input data into.
    elem_input: Source for element input data.
    """
    elem = driver.find_element(By.ID, row[elem_name])
    elem.send_keys(row[elem_input])


def serial_numbers_send(driver, computers):
    """
    Fill serial numbers into hp warranty lookup page.
    """
    submit = driver.find_element(By.ID, "FindMyProduct")
    sn_field = "inputtextpfinder"
    sn_fields = [f"{sn_field}{i}" for i in range(1, len(computers))]
    sn_fields.insert(0, sn_field)
    computers["sn_field"] = sn_fields
    func = lambda x: send_keys(driver, "sn_field", "serial_number")
    computers.apply(func)
    submit.click()


def product_numbers_send(driver, computers):
    """
    Fill product numbers into hp warranty lookup page.
    """
    submit = driver.find_element(By.ID, "FindMyProductNumber-multiple")
    max_items = len(computers) + 1
    pn_field = "product-number inputtextPN"
    pn_fields = [f"{pn_field}{i}" for i in range(1, max_items)]
    computers["pn_field"] = pn_fields
    computers = computers[computers["pn_field"] in driver.page_source]
    func = lambda x: send_keys(driver, x, "pn_field", "product_number")
    computers.apply(func)
    submit.click()


def hp_warranty_get():
    """
    Retreive warranties for HP computers from hp warranty page.
    """
    output = "hp_warranty_result.csv"
    driver = initialize_browser()
    computers = products_read()
    batched_computers = computers_batched(computers)
    file_create = True
    print(f"Starting warranty lookup of {len(computers)}")
    for computers in batched_computers:
        df = products_get(driver, computers)
        write_results(output, df, file_create)
        file_create = False
    driver.quit()


if __name__ == "__main__":
    warranty = HPWarrantyLookup()
