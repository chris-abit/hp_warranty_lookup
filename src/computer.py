import time
from itertools import batched
from datetime import datetime, date
import pandas as pd
import numpy as np
from selenium.webdriver.common.by import By
from utility import wait_for_load


def computers_read(fname="hp_products.csv"):
    """
    Read computers from hp_products.csv.
    Drops any entries missing either serial number or
    product number.
    Returns a list of computers.
    """
    columns = [
        "serial_number",
        "product_number",
    ]
    df = pd.read_csv(fname, dtype=object)
    if not np.array_equal(df.columns, columns):
        raise ValueError(f"The columns {columns} are required!")
    df = df.dropna()
    func = lambda x: Computer(x["serial_number"], x["product_number"])
    computers = list(df.apply(func, axis=1))
    return computers


def computers_save(computers, fname="hp_warranty_info.csv", append=False):
    """
    Save computer info to a csv file.
    Will append computers to file if append is True.
    """
    d_computers = {
        "serial_number": [],
        "product_number": [],
        "warranty_start": [],
        "warranty_end": [],
        "url": [],
        "error": [],
    }
    for computer in computers:
        d_computers["serial_number"].append(computer.serial_number)
        d_computers["product_number"].append(computer.product_number)
        d_computers["warranty_start"].append(computer.warranty_start)
        d_computers["warranty_end"].append(computer.warranty_end)
        d_computers["url"].append(computer.url)
        d_computers["error"].append(computer.error)
    df = pd.DataFrame(d_computers)
    if append:
        df.to_csv(fname, index=False, header=False, mode="a")
    else:
        df.to_csv(fname, index=False)


def computers_batched(computers):
    """
    Creates batches of computers.
    Guarantees that the last batch is atleast two computers, such
    that hp warranty lookup of a batch is possible.
    """
    max_items = 15
    n_items = len(computers)
    if n_items < 2:
        raise ValueError("A minimum of two computers is required.")
    batches = map(list, batched(computers, max_items))
    batches = list(batches)
    if n_items % max_items == 1:
        last_batch = batches.pop()
        second_last = batches.pop()
        last_batch.insert(0, second_last.pop())
        batches.extend([second_last, last_batch])
    return batches


class Computer:
    def __init__(self, serial_number, product_number):
        self.serial_number = serial_number
        self.product_number = product_number
        self.warranty_start = date.min
        self.warranty_end = date.min
        self.url = ""
        self.error = ""

    def _date_read(self, element):
        """
        Read a date from a element on the page.
        Returns a date.
        """
        dateformat = "%B %d, %Y"
        tmp = element.find_element(By.XPATH, "..")
        tmp = tmp.find_element(By.CLASS_NAME, "text")
        time = datetime.strptime(tmp.text, dateformat)
        return time.date()

    def url_set(self, urls):
        """
        Gets the computer url from urls.
        Will append the product number if it is missing.
        """
        urls = filter(lambda x: self.serial_number in x, urls)
        url = list(urls).pop()
        product_number = self.product_number
        if product_number not in url:
            url = f"{url}&sku={product_number}"
        self.url = url

    def _wait_for_warranty(self, driver):
        """
        Wait for warranty information to load.
        This is to cover cases where the page "finishes" a load
        but warranty information is not yet present.
        """
        timeout = 5
        poll_intervall = 0.5
        endtime = time.time() + timeout
        while time.time() < endtime:
            time.sleep(poll_intervall)
            if "Coverage type" in driver.page_source:
                return True
        return False

    def warranty_get(self, driver):
        """
        Get the warranty for a computer.
        """
        warranty_start = None
        warranty_end = None
        driver.get(self.url)
        is_loaded = wait_for_load(driver)
        if not is_loaded:
            self.error = "Timeout"
            return
        self._wait_for_warranty(driver)
        elements = driver.find_elements(By.CLASS_NAME, "label")
        for element in elements:
            if element.text == "Start date":
                warranty_start = self._date_read(element)
            if element.text == "End date":
                warranty_end = self._date_read(element)
        if warranty_start == None or warranty_end == None:
            url = driver.current_url
            raise ValueError(f"Warranty was not found in current page: {url}")
        self.warranty_start = warranty_start
        self.warranty_end = warranty_end

    def write_info(self, driver, target, source="serial"):
        """
        Write information from computer into a web element.
        driver: Which webdriver.
        target: Which element to send info to.
        source: Which data to read, serial or product number.
        """
        elem = driver.find_element(By.ID, target)
        data = ""
        if source == "serial":
            data = self.serial_number
        elif source == "product":
            data = self.product_number
        else:
            raise ValueError("Only serial or product is valid source.")
        elem.send_keys(data)

    def __repr__(self):
        return f"{self.serial_number}, {self.product_number}"
