import time
from itertools import batched
from datetime import datetime, date
import requests
import pandas as pd
import numpy as np
from selenium.webdriver.common.by import By
from utility import wait_for_load


def computers_read(fname="hp_products.csv"):
    """ Read computers from csv file.

    Drops any entries missing the serial number.
    Returns a list of computers.
    """
    columns = [
        "serial_number",
        "product_number",
    ]
    df = pd.read_csv(fname, dtype=object)
    if not np.array_equal(df.columns, columns):
        raise ValueError(f"The columns {columns} are required!")
    df = df.dropna(subset=columns[0])
    func = lambda x: Computer(x["serial_number"], x["product_number"])
    computers = list(df.apply(func, axis=1))
    return computers


def computers_save(computers, fname="hp_warranty_info.csv", append=False):
    """ Save computer info to a csv file.

    Will append computers to file if append is True.
    """
    computers = map(vars, computers)
    df = pd.DataFrame(computers)
    if append:
        df.to_csv(fname, index=False, header=False, mode="a")
    else:
        df.to_csv(fname, index=False)


class Computer:
    """ A class representing a HP computer.
    """
    def __init__(self, serial_number, product_number):
        self.serial_number = serial_number
        self.product_number = product_number
        self.warranty_start = date.min
        self.warranty_end = date.min
        self.url = ""
        self.error = ""

    def _date_read(self, element):
        """ Read a date from a element on the page.
        Returns a date.
        """
        dateformat = "%B %d, %Y"
        tmp = element.find_element(By.XPATH, "..")
        tmp = tmp.find_element(By.CLASS_NAME, "text")
        time = datetime.strptime(tmp.text, dateformat)
        return time.date()

    def _url_get_error_handle(self, response):
        """ Handle any errors obtaining a url.

        Handles any errors obtaining a url to a computer warranty page
        from HP. Takes a naive approach, assuming that the error
        message provided by HP is sufficient.
        """
        data = response.json().get("data").get("verifyResponse")
        status_code = data.get("code")
        if status_code != requests.codes.ok:
            self.error = data.get("message")
            return True
        return False

    def url_get(self):
        """ Use requests to obtain the url for the computer warranty page.

        Returns self to be friendly for map function.
        """
        warranty_url = "https://support.hp.com/us-en/warrantyresult/"
        headers = {
            "Referer": "https://support.hp.com/us-en/check-warranty",
        }
        url = "https://support.hp.com/wcc-services/searchresult/us-en"
        params = {
            "q": self.serial_number,
            "productNumber": self.product_number,
            "context": "pdp",
            "authState": "anonymous",
            "template": "checkWarranty",
        }
        r = requests.get(url, headers=headers, params=params, timeout=5)
        error = self._url_get_error_handle(r)
        if error:
            return self
        data = r.json().get("data").get("verifyResponse").get("data")
        product_series = data.get("productSeriesOID")
        target_url = data.get("targetUrl")
        target_url = target_url.strip("/product/details/")
        target_url = f"{warranty_url}{target_url}"
        target_url = target_url.replace("/model/", f"/{product_series}/model/")
        self.url = target_url
        return self

    def _wait_for_warranty(self, driver):
        """ Wait for warranty information to load.

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
        """ Get the warranty for a computer.

        Depends on the fact that the Hardware maintenance warranty
        is the first warranty present.
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
            if element.text == "Start date" and warranty_start == None:
                warranty_start = self._date_read(element)
            if element.text == "End date" and warranty_end == None:
                warranty_end = self._date_read(element)
        if warranty_start == None or warranty_end == None:
            url = driver.current_url
            raise ValueError(f"Warranty was not found in current page: {url}")
        self.warranty_start = warranty_start
        self.warranty_end = warranty_end

    def __repr__(self):
        """ Return a string containing computer serial and product number."""
        return f"{self.serial_number}, {self.product_number}"
