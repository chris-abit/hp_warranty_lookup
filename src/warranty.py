import time
from itertools import batched
from pathlib import Path
from datetime import datetime, date
from selenium.webdriver import Firefox
from selenium.common import NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from computer import Computer, computers_read, computers_save


def initialize_browser():
    """ Start selenium browser and load hp warranty page.
    Will accept all cookies.
    """
    warranty_url = "https://support.hp.com/us-en/check-warranty#multiple"
    fpath = Path(__file__).parent.resolve()
    ublock = fpath / "ublock.xpi"
    errors = [NoSuchElementException, ElementNotInteractableException]
    cookie_elem = "onetrust-accept-btn-handler"
    driver = Firefox()
    driver.implicitly_wait(4)
    driver.install_addon(ublock)
    driver.get(warranty_url)
    wait = WebDriverWait(driver, timeout=8, ignored_exceptions=errors)
    wait.until(
        lambda d : driver.find_element(By.ID, cookie_elem).click()
        or True
    )
    time.sleep(2)  # Wait for cookie prompt to dissapear.
    return driver


def batch_warranty_get(driver, computers):
    """ Get warranties for computers in batch.
    Will filter out any with errors.
    """
    computers = map(lambda x: x.url_get(), computers)
    computers = filter(lambda x: x.error == "", computers)
    for computer in computers:
        computer.warranty_get(driver)


def hp_warranty_get():
    """ Retreive warranties for HP computers from hp warranty page.
    """
    start = time.time()
    output = "hp_warranty_result.csv"
    batch_size = 15
    driver = initialize_browser()
    computers = computers_read()
    batched_computers = batched(computers, batch_size)
    is_append = False
    print(f"Starting warranty lookup of {len(computers)} computers.")
    for computers in batched_computers:
        batch_warranty_get(driver, computers)
        computers_save(computers, output, append=is_append)
        is_append = True
    driver.quit()
    elapsed_time = time.time() - start
    print(f"Done. Process took {elapsed_time} s")


if __name__ == "__main__":
    hp_warranty_get()
