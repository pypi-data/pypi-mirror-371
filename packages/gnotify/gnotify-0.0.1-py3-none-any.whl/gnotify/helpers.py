from typing import Dict, Set
from datetime import datetime

from .trading_holiday import get_holidays_for_region_year


def is_it_holiday(region: str, _in_date: str) -> bool:
    """
    Check if a given date is a holiday in the specified region.

    Args:
        region (str): The region to check for holidays. Valid values are "us", "eu", and "jp".
        _in_date (str): The date to check in the format "YYYYMMDD".

    Returns:
        bool: True if the date is a holiday, False otherwise.

    Examples:
        >>> is_it_holiday("us", "20230102")
        True
        >>> is_it_holiday("eu", "20250101")
        True
        >>> is_it_holiday("jp", "20250101")
        True
    """
    try:
        # Extract year from date string
        year = int(_in_date[:4])
        holidays_for_year = get_holidays_for_region_year(region, year)
        return _in_date in holidays_for_year
    except (ValueError, IndexError):
        # Invalid date format, return False
        return False


def is_it_half_day(region: str, _in_date: str) -> bool:
    """
    Check if a given date is a half trading day in the specified region.

    Args:
        region (str): The region to check for half-days. Valid values are "us", "eu", and "jp".
        _in_date (str): The date to check in the format "YYYYMMDD".

    Returns:
        bool: True if the date is a half trading day, False otherwise.

    Examples:
        >>> is_it_half_day("us", "20231124")  # Day after Thanksgiving
        True
        >>> is_it_half_day("eu", "20231224")  # Christmas Eve
        True
    """
    try:
        from .trading_holiday import get_half_days_for_region_year
        year = int(_in_date[:4])
        half_days_for_year = get_half_days_for_region_year(region, year)
        return _in_date in half_days_for_year
    except (ValueError, IndexError):
        return False
