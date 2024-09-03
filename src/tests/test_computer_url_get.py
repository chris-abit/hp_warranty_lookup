import requests
from computer import Computer


def url_get(serial_number, product_number):
    product_number = ""
    headers = {
        "Referer": "https://support.hp.com/us-en/check-warranty",
    }
    url = "https://support.hp.com/wcc-services/searchresult/us-en"
    params = {
        "q": serial_number,
        "productNumber": product_number,
        "context": "pdp",
        "authState": "anonymous",
        "template": "checkWarranty",
    }
    r = requests.get(url, headers=headers, params=params, timeout=5)
    return r


def test_endpoint_is_still_valid():
    """ Test if HP endpoint for getting urls for computers is still valid.

    Requires an internett connection.
    """
    serial_number = "HU265BM18V"
    response = url_get(serial_number, "")
    assert response.ok


def test_endpoint_still_has_target_url():
    serial_number = "HU265BM18V"
    response = url_get(serial_number, "")
    assert "targetUrl" in response.text
