from typing import Dict, Set
import holidays
from datetime import datetime

def get_trading_holidays(region: str, year: int) -> Set[str]:
    """
    Get trading holidays for a specific region and year using the holidays library.

    Args:
        region (str): Region code ("us", "eu", "jp")
        year (int): Year to get holidays for

    Returns:
        Set[str]: Set of holiday dates in YYYYMMDD format
    """
    holiday_dates = set()

    if region == "us":
        # US stock market holidays (NYSE/NASDAQ)
        us_holidays = holidays.NYSE(years=year)
        for date in us_holidays:
            holiday_dates.add(date.strftime("%Y%m%d"))

    elif region == "eu":
        # London Stock Exchange holidays (primary EU trading center)
        uk_holidays = holidays.UK(years=year)
        # Add specific LSE trading holidays
        for date in uk_holidays:
            holiday_dates.add(date.strftime("%Y%m%d"))

        # Add additional EU trading holidays not covered by UK holidays
        # Boxing Day, New Year's Eve (when markets are closed)
        additional_dates = {
            f"{year}1224",  # Christmas Eve (half day)
            f"{year}1231",  # New Year's Eve (half day)
        }
        holiday_dates.update(additional_dates)

    elif region == "jp":
        # Japan Stock Exchange holidays
        jp_holidays = holidays.Japan(years=year)
        for date in jp_holidays:
            holiday_dates.add(date.strftime("%Y%m%d"))

        # Add New Year's Eve for TSE
        holiday_dates.add(f"{year}1231")

    return holiday_dates

def get_trading_half_days(region: str, year: int) -> Set[str]:
    """
    Get trading half-day dates for a specific region and year.

    Args:
        region (str): Region code ("us", "eu", "jp")
        year (int): Year to get half-days for

    Returns:
        Set[str]: Set of half-day dates in YYYYMMDD format
    """
    half_days = set()

    if region == "us":
        # Common US half-day trading dates
        half_days.update({
            f"{year}0703",  # Day before July 4th (when July 4th falls on Friday)
            f"{year}1124",  # Day after Thanksgiving
            f"{year}1224",  # Christmas Eve
        })

    elif region == "eu":
        # LSE half-day trading
        half_days.update({
            f"{year}1224",  # Christmas Eve
            f"{year}1231",  # New Year's Eve
        })

    elif region == "jp":
        # Japan typically doesn't have half-day trading
        pass

    return half_days

# Cache for performance - holidays don't change frequently
_holiday_cache: Dict[str, Set[str]] = {}
_half_day_cache: Dict[str, Set[str]] = {}

def get_holidays_for_region_year(region: str, year: int) -> Set[str]:
    """Get holidays with caching."""
    cache_key = f"{region}_{year}"
    if cache_key not in _holiday_cache:
        _holiday_cache[cache_key] = get_trading_holidays(region, year)
    return _holiday_cache[cache_key]

def get_half_days_for_region_year(region: str, year: int) -> Set[str]:
    """Get half-days with caching."""
    cache_key = f"{region}_{year}"
    if cache_key not in _half_day_cache:
        _half_day_cache[cache_key] = get_trading_half_days(region, year)
    return _half_day_cache[cache_key]

# Legacy compatibility - maintain the old interface
def get_holidays_dict() -> Dict[str, Set[str]]:
    """
    Get current year holidays for backward compatibility.

    Returns:
        Dict[str, Set[str]]: Dictionary with region keys and holiday sets
    """
    current_year = datetime.now().year
    return {
        "us": get_holidays_for_region_year("us", current_year),
        "eu": get_holidays_for_region_year("eu", current_year),
        "jp": get_holidays_for_region_year("jp", current_year),
    }

def get_half_days_dict() -> Dict[str, Set[str]]:
    """
    Get current year half-days for backward compatibility.

    Returns:
        Dict[str, Set[str]]: Dictionary with region keys and half-day sets
    """
    current_year = datetime.now().year
    return {
        "us": get_half_days_for_region_year("us", current_year),
        "eu": get_half_days_for_region_year("eu", current_year),
        "jp": get_half_days_for_region_year("jp", current_year),
    }

# Maintain backward compatibility
holidays_dict = get_holidays_dict()
halfdays = get_half_days_dict()
