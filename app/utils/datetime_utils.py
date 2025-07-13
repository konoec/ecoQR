from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import pytz
from loguru import logger


def get_current_utc() -> datetime:
    """Get current UTC datetime with timezone info"""
    return datetime.now(timezone.utc)


def utc_now() -> datetime:
    """Get current UTC datetime with timezone info - alias for get_current_utc()"""
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string"""
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse datetime from string"""
    return datetime.strptime(dt_str, format_str)


def add_timezone(dt: datetime, timezone: str = "UTC") -> datetime:
    """Add timezone to naive datetime"""
    tz = pytz.timezone(timezone)
    return tz.localize(dt)


def convert_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
    """Convert datetime from one timezone to another"""
    from_timezone = pytz.timezone(from_tz)
    to_timezone = pytz.timezone(to_tz)
    
    if dt.tzinfo is None:
        dt = from_timezone.localize(dt)
    
    return dt.astimezone(to_timezone)


def get_date_range(start_date: datetime, end_date: datetime) -> list[datetime]:
    """Get list of dates between start and end date"""
    dates = []
    current_date = start_date
    
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=1)
    
    return dates


def get_month_start(dt: Optional[datetime] = None) -> datetime:
    """Get start of month for given date"""
    if dt is None:
        dt = get_current_utc()
    
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def get_month_end(dt: Optional[datetime] = None) -> datetime:
    """Get end of month for given date"""
    if dt is None:
        dt = get_current_utc()
    
    # Get first day of next month, then subtract one day
    next_month = dt.replace(day=28) + timedelta(days=4)
    end_of_month = next_month - timedelta(days=next_month.day)
    
    return end_of_month.replace(hour=23, minute=59, second=59, microsecond=999999)


def get_week_start(dt: Optional[datetime] = None) -> datetime:
    """Get start of week (Monday) for given date"""
    if dt is None:
        dt = get_current_utc()
    
    days_since_monday = dt.weekday()
    monday = dt - timedelta(days=days_since_monday)
    
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def is_expired(expiry_date: datetime) -> bool:
    """Check if a date has expired"""
    return get_current_utc() > expiry_date


def days_until_expiry(expiry_date: datetime) -> int:
    """Get number of days until expiry"""
    delta = expiry_date - get_current_utc()
    return delta.days


def format_duration(seconds: float) -> str:
    """Format duration in seconds to human readable string"""
    if seconds < 1:
        return f"{seconds*1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


def get_business_days(start_date: datetime, end_date: datetime) -> int:
    """Get number of business days between two dates"""
    current_date = start_date
    business_days = 0
    
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Monday = 0, Sunday = 6
            business_days += 1
        current_date += timedelta(days=1)
    
    return business_days


def get_quarters_in_year(year: int) -> list[tuple[datetime, datetime]]:
    """Get quarters start and end dates for a given year"""
    quarters = []
    
    # Q1: Jan-Mar
    q1_start = datetime(year, 1, 1)
    q1_end = datetime(year, 3, 31, 23, 59, 59)
    quarters.append((q1_start, q1_end))
    
    # Q2: Apr-Jun
    q2_start = datetime(year, 4, 1)
    q2_end = datetime(year, 6, 30, 23, 59, 59)
    quarters.append((q2_start, q2_end))
    
    # Q3: Jul-Sep
    q3_start = datetime(year, 7, 1)
    q3_end = datetime(year, 9, 30, 23, 59, 59)
    quarters.append((q3_start, q3_end))
    
    # Q4: Oct-Dec
    q4_start = datetime(year, 10, 1)
    q4_end = datetime(year, 12, 31, 23, 59, 59)
    quarters.append((q4_start, q4_end))
    
    return quarters
