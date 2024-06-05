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
    sn_field = "inputtextpfinder"
    sn_fields = [f"{sn_field}{i}" for i in range(1, len(computers))]
    sn_fields.insert(0, sn_field)
    computers["sn_field"] = sn_fields
    func = lambda x: send_keys(driver, x, "sn_field", "serial_number")
    computers.apply(func, axis=1)
    submit_form(driver)


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


def product_numbers_send(driver, computers):
    """
    Fill product numbers into hp warranty lookup page.
    """
    max_items = len(computers) + 1
    pn_field = "product-number inputtextPN"
    pn_fields = [f"{pn_field}{i}" for i in range(1, max_items)]
    computers["pn_field"] = pn_fields
    pn_fields = filter(lambda x: x in driver.page_source, pn_fields)
    missing = computers[computers["pn_field"].isin(pn_fields)]
    func = lambda x: send_keys(driver, x, "pn_field", "product_number")
    missing.apply(func, axis=1)
    submit_form(driver)


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


def set_url(row, sn_urls):
    serial_number = row["serial_number"]
    url = sn_urls[serial_number]
    row["url"] = url
    return row


def append_missing_product_number_to_url(row):
    url = row["url"]
    product_number = row["product_number"]
    if product_number not in url:
        row["url"] = f"{url}&sgu={product_number}"
    return row


def computer_urls_get(driver, computers):
    """
    Retreive urls for each computer.
    """
    n_items = len(computers)
    urls_det = urls_find(driver, "Viewdetails", n_items)
    urls_opt = urls_find(driver, "ViewOptions", n_items)
    urls = list(chain(urls_opt, urls_det))
    sn_urls = {}
    for url in urls:
        serial_number = url.split("serialnumber=")[1]
        sn_urls[serial_number] = url
    computers = computers.apply(lambda x: set_url(x, sn_urls), axis=1)
    computers = computers.apply(append_missing_product_number_to_url, axis=1)
    return computers


def query_clear(driver):
    """
    Clears hp warranty entries such that information can be entred.
    Silly workaround, that abuses that clicking "Single product" clears
    results.
    """
    driver.find_element(By.ID, "SingleProduct").click()
    driver.find_element(By.ID, "MultipleProduct").click()


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


def products_get(driver, computers):
    """
    """
    wait = WebDriverWait(driver, timeout=120)
    n_items = len(computers)

    driver.get(WARRANTY_URL)
    query_clear(driver)
    add_item = driver.find_element(By.ID, "AddItem")
    for _ in range(n_items - 2):
        add_item.click()
    serial_numbers_send(driver, computers)
    success = wait_for_errors_or_success(driver)
    if not success:
        product_numbers_send(driver, computers)
        wait_for_errors_or_success(driver)
    computers = computer_urls_get(driver, computers)
    return computers


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
    hp_warranty_get()
