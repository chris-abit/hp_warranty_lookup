from datetime import date
import pandas as pd
import numpy as np
from selenium.webdriver.common.by import By
from utility import wait_for_load


class Computer:
    def __init__(self, serial_number, product_number):
        self.serial_number = serial_number
        self.product_number = product_number
        self.warranty_start = date.min
        self.warranty_end = date.min
        self.url = ""
        self.error = ""

    def _date_read(element):
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
