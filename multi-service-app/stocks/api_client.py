import requests
from config import API_KEY


def get_stock_price(symbol):

    api_url = 'https://api.api-ninjas.com/v1/stockprice?ticker={}'.format(symbol)
    response = requests.get(api_url, headers={'X-Api-Key': API_KEY})

    if response.status_code == requests.codes.ok:
        data = response.json()
        if data and len(data) > 0:
            return round(float(data["price"]), 2)
        raise Exception("No data returned from API")
    raise Exception(f"API response code {response.status_code}")