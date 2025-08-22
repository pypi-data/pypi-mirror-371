from datetime import datetime
import jdatetime
from .formats import format_jalali, format_gregorian, WEEKDAYS_FA_PERSIAN
from .exceptions import InvalidDateFormat

class EJdate:
    def __init__(self, date: datetime = None):
        self.gregorian = date or datetime.now()
        self.jalali = jdatetime.datetime.fromgregorian(datetime=self.gregorian).date()

    @classmethod
    def now(cls):
        """Return current date (wrapped object)"""
        return cls()

    @classmethod
    def now_gregorian(cls):
        """Return current Gregorian datetime"""
        return datetime.now()

    @staticmethod
    def to_jalali(date: datetime) -> jdatetime.date:
        """Convert Gregorian to Jalali"""
        if not isinstance(date, datetime):
            raise InvalidDateFormat("Expected datetime object for Gregorian date")
        return jdatetime.datetime.fromgregorian(datetime=date).date()

    @staticmethod
    def to_gregorian(date: jdatetime.date) -> datetime:
        """Convert Jalali to Gregorian"""
        if not isinstance(date, jdatetime.date):
            raise InvalidDateFormat("Expected jdatetime.date object for Jalali date")
        return date.togregorian()

    def weekday(self, lang: str = "fa") -> str:
        """Return day of week in Persian or English"""
        return WEEKDAYS_FA_PERSIAN[self.jalali.weekday()] if lang == "fa" else self.gregorian.strftime("%A")

    def is_weekend(self) -> bool:
        """Check if the date is Friday (weekend in Iran)"""
        return self.jalali.weekday() == 4  # Friday

    def diff_days(self, other_date: datetime) -> int:
        """Calculate absolute day difference with another Gregorian date"""
        if not isinstance(other_date, datetime):
            raise InvalidDateFormat("Expected datetime object for other_date")
        delta = self.gregorian.date() - other_date.date()
        return abs(delta.days)

    def format(self, calendar: str = "jalali", style: str = "short", lang: str = "en") -> str:
        """Format date in Jalali or Gregorian calendar"""
        if calendar == "jalali":
            return format_jalali(self.jalali, style, lang)
        elif calendar == "gregorian":
            return format_gregorian(self.gregorian, style)
        else:
            raise ValueError("Invalid calendar type. Use 'jalali' or 'gregorian'")
