import time


def wait_for_load(driver, timeout=300):
    """
    Wait for loading of computer page to finish.
    """
    poll_interwall = 0.5
    end_time = time.time() + timeout
    load_msg = '"loading-screen-wrapper'
    error_msg = "Refresh page"

    while time.time() < end_time:
        time.sleep(poll_interwall)
        if error_msg in driver.page_source:
            time.sleep(5)
            driver.refresh()
        elif load_msg not in driver.page_source:
            return True
    return False
