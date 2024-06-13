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


def submit_form(driver):
    """
    Submit hp warranty lookup form.
    Hp has three different id's for the submit button, which
    depends on the context.
    """
    variations = [
        "FindMyProduct",
        "FindMyProductNumber",
        "FindMyProductNumber-multiple",
    ]
    elem = None
    for var in variations:
        string = f'"{var}"'
        if string in driver.page_source:
            elem = driver.find_element(By.ID, var)
    if not elem:
        raise ValueError("No submit button found in page!")
    elem.click()


def urls_find(driver, field_name, n_fields):
    """
    Find the urls for computers in hp result page.
    """
    source = driver.page_source
    urls = [f"{field_name}[{i}]" for i in range(n_fields)]
    urls = filter(lambda x: x in source, urls)
    urls = map(lambda x: driver.find_element(By.ID, x), urls)
    urls = map(lambda x: x.get_attribute("href"), urls)
    return urls


def computer_urls_get(driver, computers):
    """
    Retreive urls for each computer.
    """
    n_items = len(computers)
    urls_det = urls_find(driver, "Viewdetails", n_items)
    urls_opt = urls_find(driver, "ViewOptions", n_items)
    urls = list(chain(urls_opt, urls_det))
    for computer in computers:
        computer.url_set(urls)
    return computers


def query_clear(driver, n_items):
    """
    Clears hp warranty entries such that information can be entred.
    Silly workaround, that abuses that clicking "Single product" clears
    results.
    Will add n fields using the add item button.
    """
    driver.find_element(By.ID, "SingleProduct").click()
    driver.find_element(By.ID, "MultipleProduct").click()
    add_item = driver.find_element(By.ID, "AddItem")
    for _ in range(n_items - 2):
        add_item.click()


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


def computers_form_fill_and_submit(driver, computers, targets, source):
    """
    Locate valid fields for filling hp computer info.
    Then write info in those fields and submit the form.
    """
    for computer, target in zip(computers, targets):
        elem_txt = f'"{target}"'
        if elem_txt in driver.page_source:
            computer.write_info(driver, target, source)
    submit_form(driver)


def handle_errors(driver, computers, sn_fields):
    """
    Detect errors in serial number fields. Removing them
    from the list of computers and setting an error of invalid serial number.
    This relies on that the serial number field has a error class 'is-invalid'.
    Rather than handling manually removing fields the query is cleared.
    """
    error_class = "is-invalid"
    for computer, field in zip(computers, sn_fields):
        f_class = driver.find_element(By.ID, field).get_attribute("class")
        if error_class in f_class:
            computer.error = "Invalid serial number."
    invalid_computers = list(filter(lambda x: x.error != "", computers))
    computers = list(filter(lambda x: x.error == "", computers))
    if invalid_computers:
        query_clear(driver, len(computers))
    return [computers, invalid_computers]


def products_get(driver, computers):
    """
    """
    wait = WebDriverWait(driver, timeout=120)
    n_items = len(computers)
    sn_field = "inputtextpfinder"
    sn_fields = [f"{sn_field}{i}" for i in range(1, n_items)]
    sn_fields.insert(0, sn_field)
    pn_field = "product-number inputtextPN"
    pn_fields = [f"{pn_field}{i}" for i in range(1, n_items + 1)]

    driver.get(WARRANTY_URL)
    query_clear(driver, n_items)
    computers_form_fill_and_submit(driver, computers, sn_fields, "serial")
    success = wait_for_errors_or_success(driver)
    computers, errors = handle_errors(driver, computers, sn_fields)
    if errors:
        # Rather than manually clearing fields, reinput valid serial numbers.
        computers_form_fill_and_submit(driver, computers, sn_fields, "serial")
        success = wait_for_errors_or_success(driver)
    if not success:
        computers_form_fill_and_submit(driver, computers, pn_fields, "product")
        wait_for_errors_or_success(driver)
    computers = computer_urls_get(driver, computers)
    for computer in computers:
        computer.warranty_get(driver)
    computers.extend(errors)
    return computers


def hp_warranty_get():
    """
    Retreive warranties for HP computers from hp warranty page.
    """
    output = "hp_warranty_result.csv"
    driver = initialize_browser()
    computers = computers_read()
    batched_computers = computers_batched(computers)
    is_append = False
    print(f"Starting warranty lookup of {len(computers)} computers.")
    for computers in batched_computers:
        products_get(driver, computers)
        computers_save(computers, output, append=is_append)
        is_append = True
    driver.quit()
    print("Done.")


if __name__ == "__main__":
    driver = hp_warranty_get()
