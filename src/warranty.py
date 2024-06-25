import time
from pathlib import Path
from datetime import datetime, date
from itertools import chain
import pandas as pd
from selenium.webdriver import Firefox
from selenium.common import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from utility import wait_for_load
from computer import Computer, computers_read, computers_save, computers_batched

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


def wait_for_errors_or_success(driver, timeout=300):
    """
    Wait for results from query, then test if there is an error
    with product identification from HP.
    Returns False if there are any products which cannot be identified.
    Returns True if products are successfully identified.
    Will raise a ValueError on any other results.
    """
    poll_intervall = 0.5
    end_time = time.time() + timeout
    error_msg = "product cannot be identified"
    summary_msg = "multiple-products-summary"
    while (time.time() < end_time):
        time.sleep(poll_intervall)
        if error_msg in driver.page_source:
            return False
        if summary_msg in driver.current_url:
            return True
    raise ValueError("Unexpected result in page.")


def batch_warranty_get(driver, computers):
    """
    Get warranties for computers in batch.
    Will filter out any with errors.
    """
    computers = filter(lambda x: x.error == "", computers)
    for computer in computers:
        computer.warranty_get(driver)



def hp_warranty_get():
    """
    Retreive warranties for HP computers from hp warranty page.
    """
    start = time.time()
    output = "hp_warranty_result.csv"
    driver = initialize_browser()
    computers = computers_read()
    batched_computers = computers_batched(computers)
    is_append = False
    print(f"Starting warranty lookup of {len(computers)} computers.")
    [c.url_get() for c in computers]
    for computers in batched_computers:
        batch_warranty_get(driver, computers)
        computers_save(computers, output, append=is_append)
        is_append = True
    driver.quit()
    elapsed_time = time.time() - start
    print(f"Done. Process took {elapsed_time} s")


if __name__ == "__main__":
    hp_warranty_get()
