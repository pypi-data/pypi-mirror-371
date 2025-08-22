from datetime import datetime
import jdatetime

def parse_gregorian(date_str: str, fmt: str = "%Y-%m-%d") -> datetime:
    try:
        return datetime.strptime(date_str, fmt)
    except ValueError:
        raise ValueError("Invalid Gregorian date format")

def parse_jalali(date_str: str, fmt: str = "%Y-%m-%d") -> jdatetime.date:
    try:
        return jdatetime.datetime.strptime(date_str, fmt).date()
    except ValueError:
        raise ValueError("Invalid Jalali date format")
