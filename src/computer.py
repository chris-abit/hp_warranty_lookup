from datetime import date


class Computer:
    def __init__(self, serial_number, product_number):
        self.serial_number = serial_number
        self.product_number = product_number
        self.warranty_start = date.min
        self.warranty_end = date.min
        self.url = ""
        self.error = ""

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
                warranty_start = date_read(element)
            if element.text == "End date":
                warranty_end = date_read(element)
        if warranty_start == None or warranty_end == None:
            url = driver.current_url
            raise ValueError(f"Warranty was not found in current page: {url}")
        self.warranty_start = warranty_start
        self.warranty_end = warranty_end
