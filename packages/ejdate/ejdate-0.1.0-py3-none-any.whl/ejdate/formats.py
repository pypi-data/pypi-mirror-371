import jdatetime
from datetime import datetime

WEEKDAYS_FA = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
WEEKDAYS_FA_PERSIAN = ['دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنج‌شنبه', 'جمعه', 'شنبه', 'یک‌شنبه']

def format_jalali(date: jdatetime.date, style: str = "short", lang: str = "en") -> str:
    if style == "short":
        return date.strftime("%Y/%m/%d")
    elif style == "long":
        weekday = WEEKDAYS_FA_PERSIAN[date.weekday()] if lang == "fa" else WEEKDAYS_FA[date.weekday()]
        return f"{weekday} {date.strftime('%d %B %Y')}"
    elif style == "official":
        return f"{date.strftime('%d')} {date.strftime('%B')} {date.strftime('%Y')}"
    else:
        raise ValueError("Invalid date format style")

def format_gregorian(date: datetime, style: str = "short") -> str:
    if style == "short":
        return date.strftime("%Y-%m-%d")
    elif style == "long":
        return date.strftime("%A, %d %B %Y")
    elif style == "official":
        return date.strftime("%d %B %Y")
    else:
        raise ValueError("Invalid date format style")
