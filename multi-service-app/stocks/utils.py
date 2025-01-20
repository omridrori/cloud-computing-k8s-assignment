
import json
from datetime import datetime

def is_valid_stock_data(data, check_id=False,require_all_fields=False):
    required_fields = {"symbol", "purchase price", "shares"}
    if check_id:
        required_fields.add("id")


    if require_all_fields:
        required_fields = {"id","symbol", "purchase price", "shares","purchase date","name"}

    return all(field in data for field in required_fields)






def validate_json_request(json_data):
    """
    Validates and processes a JSON request according to the provided rules.

    :param json_data: The JSON object to validate.
    :param request_type: Type of request ('POST' or 'GET').
    :return: Tuple (Boolean, Processed JSON object or None)
    """
    def round_to_two_decimals(value):
        """Rounds a float to 2 decimal places."""
        return round(value, 2)

    def format_date(date_str):
        """Validates and formats the date to DD-MM-YYYY."""
        try:
            return datetime.strptime(date_str, '%d-%m-%Y').strftime('%d-%m-%Y')
        except ValueError:
            return False

    if not isinstance(json_data, dict):
        return False, None

    processed_json = {}

    for key, value in json_data.items():
        if isinstance(value, float):
            # Rule for floats
            processed_json[key] = round_to_two_decimals(value)
        elif key.lower() == "stock symbol" and isinstance(value, str):
            # Rule for stock symbols
            processed_json[key] = value.upper()
        elif key.lower() == "purchase date" and isinstance(value, str):
            # Rule for dates
            formatted_date = format_date(value)
            if not formatted_date:
                return False, None
            processed_json[key] = formatted_date
        elif isinstance(value, str):
            # General rule for strings
            processed_json[key] = value.strip()
        else:
            # Keep other types as is
            processed_json[key] = value



    return True, processed_json