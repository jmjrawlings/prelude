"""
Datetime functions
"""

from threading import local
from pendulum.date import Date
from pendulum.datetime import DateTime
from pendulum.period import Period
from pendulum.duration import Duration
from datetime import timedelta
from datetime import datetime as pydatetime
from datetime import date as pydate
from pendulum.tz.timezone import Timezone

import pendulum as pn


NICE_DATETIME_FORMAT = "D MMM HH:mm"
SHORT_DATE_FORMAT = "DD/MM"
ISO_DATE_FORAT = "YYYY-MM-DD"
NICE_DATE_FORMAT = "MMM DD"
SHORT_DATE_FORMAT="DD/MM"
TIMEZONE = 'UTC'



def duration(*args, days=0, minutes=0, hours=0, seconds=0, milliseconds=0, microseconds=0, weeks=0, months=0, years=0) -> Duration:
    """
    Create a Duration from the given arguments
    """
        
    if not args:
        return pn.duration(
            days=days,
            minutes=minutes,
            hours=hours,
            seconds=seconds,
            milliseconds=milliseconds,
            microseconds=0,
            weeks=0,
            months=0,
            years=0
        )

    arg = args[0]
    
    if isinstance(arg, Period):
        return arg.as_interval()

    elif isinstance(arg, Duration):
        return arg

    elif isinstance(arg, timedelta):
        return pn.duration(seconds=arg.total_seconds())

    elif not arg:
        return pn.duration()

    else:
        raise ValueError(
            f"Could not parse a Duration value from args {args}"
        )


def elapsed(arg) -> str:
    """
    Convert the given argument to a 
    a human readable duration string
    elapsed(duration(seconds=70)) == "1m 10s"
    """
    msg : str = duration(arg).in_words() # type: ignore
    return msg


def now() -> DateTime:
    """
    Get the current datetime
    """
    return pn.now(tz=TIMEZONE)


def today() -> Date:
    return now().date()


def tomorrow() -> Date:
    return today().add(days=1)


def yesterday() -> Date:
    return today().add(days=1)
    

def datetime(
    *args, 
    year=1900,
    month=1,
    day=1,
    hour=1,
    minute=1,
    second=1,
    timezone=TIMEZONE,
    format="",
    warn_on_localize=True
    ) -> DateTime:
    """
    Convert the given argument to a datetime
    """
    if not args:
        return pn.datetime(year=year, month=month, day=day, hour=hour, minute=minute, second=second)

    arg = args[0]
    
    if isinstance(arg, DateTime):
        val = arg

    elif isinstance(arg, pydatetime):
        val = pn.instance(arg)

    elif isinstance(arg, pydate):
        val = pn.datetime(year=arg.year, month=arg.month, day=arg.day, tz=timezone)

    elif isinstance(arg, str):
        if format:
            val = pn.from_format(arg, format)
        else:
            val = pn.parse(arg) #type:ignore
            val = datetime(val)

    else:
        raise ValueError(f"Could not create a DateTime from {arg} of type {type(arg)}")

    localized = val.in_tz(timezone)
    
    if not val.tz and warn_on_localize:
        log.warn(f'DateTime {val} is being localized to {localized.tz.name}')
    elif val.tz != timezone and warn_on_localize:
        log.warn(f'DateTime {val} is changing timezones from {val.tz.name} to {localized.tz.name}')

    return localized


def date(
        *args,
        year=1900,
        month=1,
        day=1,
        format=""
        ) -> Date:
    """
    Create a from the given arguments
    """
    if not args:
        return pn.date(year, month, day)
    
    arg = args[0]

    if isinstance(arg, pydatetime):
        return Date(arg.year, arg.month, arg.day)
    
    elif isinstance(arg, pydate):
        return Date(arg.year, arg.month, arg.day)

    elif isinstance(arg, str):
        if format:
            parsed = pn.from_format(arg, format)
        else:
            parsed = pn.parse(arg) #type:ignore
        return date(parsed)
    else:
        raise ValueError(f'Could not create a Date from {arg}')
    
