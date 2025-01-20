import requests
from flask import jsonify
import os

# Load environment variables
STOCKS1_URL = os.getenv("STOCKS1_URL", "http://stocks1-a:8000")
STOCKS2_URL = os.getenv("STOCKS2_URL", "http://stocks2:8000")

ALLOWED_QUERY_PARAMS = {"portfolio", "numsharesgt", "numshareslt"}

def get_stocks(url):
    """Fetch stock data from the provided URL."""
    try:
        response = requests.get(f"{url}/stocks")
        if response.status_code != 200:
            raise Exception(f"API response code {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(str(e))

def get_stock_value(url, stock_id):
    """Fetch the current stock value using stock ID."""
    try:
        response = requests.get(f"{url}/stock-value/{stock_id}")
        if response.status_code != 200:
            raise Exception(f"Failed to fetch stock value: {response.status_code}")
        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(str(e))

def process_capital_gains_request(request):
    """Main function to process the capital gains calculation request."""
    # Validate and extract query parameters
    params = validate_query_parameters(request)
    portfolio, numsharesgt, numshareslt = extract_query_parameters(request)

    # Fetch stock data
    stock_data = fetch_stock_data(portfolio)

    # Calculate capital gains
    total_gain = calculate_capital_gains(stock_data, numsharesgt, numshareslt)
    return str(total_gain), 200


def validate_query_parameters(request):
    """Validate query parameters."""
    params = set(request.args.keys())
    for param in params:
        if param not in ALLOWED_QUERY_PARAMS:
            raise ValueError(f"Unexpected query parameters: {', '.join(param)}")
    return params


def extract_query_parameters(request):
    """Extract and validate query parameters."""
    portfolio = request.args.get("portfolio")
    if portfolio not in (None, "stocks1", "stocks2"):
        raise FileNotFoundError("Portfolio not found")
    numsharesgt = request.args.get("numsharesgt", type=int)
    numshareslt = request.args.get("numshareslt", type=int)
    return portfolio, numsharesgt, numshareslt


def fetch_stock_data(portfolio):
    """Fetch stock data from the appropriate sources."""
    stock_data = []
    if portfolio == "stocks1":
        stock_data.extend(augment_with_portfolio(get_stocks(STOCKS1_URL), "stocks1"))
    elif portfolio == "stocks2":
        stock_data.extend(augment_with_portfolio(get_stocks(STOCKS2_URL), "stocks2"))
    else:
        stock_data.extend(augment_with_portfolio(get_stocks(STOCKS1_URL), "stocks1"))
        stock_data.extend(augment_with_portfolio(get_stocks(STOCKS2_URL), "stocks2"))
    return stock_data


def augment_with_portfolio(stocks, portfolio_name):
    """Augment stock data with portfolio information."""
    for stock in stocks:
        stock["portfolio"] = portfolio_name
    return stocks


def calculate_capital_gains(stock_data, numsharesgt, numshareslt):
    """Calculate capital gains for the provided stock data."""
    capital_gains = []
    for stock in stock_data:
        stock_id, shares, purchase_price, portfolio = extract_stock_fields(stock)
        current_price = fetch_current_price(stock_id, portfolio)

        gain = compute_gain(shares, purchase_price, current_price)

        if not is_filtered_out(shares, numsharesgt, numshareslt):
            capital_gains.append(gain)

    return sum(capital_gains)


def extract_stock_fields(stock):
    """Extract essential fields from stock data."""
    stock_id = str(stock.get("id"))
    shares = stock.get("shares")
    purchase_price = stock.get("purchase price")
    portfolio = stock.get("portfolio")

    if stock_id is None or shares is None or purchase_price is None:
        raise ValueError(f"Malformed data: {shares, purchase_price, stock_id, stock}")
    return stock_id, shares, purchase_price, portfolio


def fetch_current_price(stock_id, portfolio):
    """Fetch the current price of a stock."""
    try:
        portfolio_url = STOCKS1_URL if portfolio == "stocks1" else STOCKS2_URL
        stock_value_data = get_stock_value(portfolio_url, stock_id)
        current_price = stock_value_data.get("stock value")
        if current_price is None:
            raise ValueError(f"Malformed stock value data: {stock_value_data}")
        return current_price
    except Exception as e:
        raise Exception(f"Error fetching current price for stock ID {stock_id}: {e}")


def compute_gain(shares, purchase_price, current_price):
    """Compute the capital gain for a stock."""
    try:
        current_value = shares * current_price
        purchase_cost = shares * purchase_price
        return current_value - purchase_cost
    except Exception as e:
        raise ValueError("Malformed data in calculation") from e


def is_filtered_out(shares, numsharesgt, numshareslt):
    """Determine if a stock should be filtered out based on share filters."""
    if numsharesgt is not None and shares <= numsharesgt:
        return True
    if numshareslt is not None and shares >= numshareslt:
        return True
    return False

