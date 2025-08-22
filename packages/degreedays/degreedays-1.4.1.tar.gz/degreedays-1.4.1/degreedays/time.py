"""
Classes for working with dates and date-ranges in the context of degree days
and energy data.
"""

import datetime
from degreedays._private import _Immutable
from degreedays._private import XmlElement
import degreedays._private as private
try:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        import sys
        if sys.version_info >= (3, 9):
            from collections.abc import Iterator, Iterable
        else:
            from typing import Iterator, Iterable
except ImportError:
    pass


__all__ = ['DayRange', 'DayRanges', 'DayOfWeek', 'StartOfMonth', 'StartOfYear']

_DAY_RANGE_EXAMPLE = ('DayRange(datetime.date(2012, 1, 1), '
        'datetime.date(2012, 11, 30)) '
    'or DayRange.singleDay(datetime.date.today() - datetime.timedelta(1)) '
    '(for yesterday only)')
# using datetime.date is perfect for us as it's timezone independent and immutable
class DayRange(_Immutable):
    """Specifies a range of one or more days e.g. 2020-01-01 to 2020-12-31.
    
    :param datetime.date first: the first day that the :py:class:`DayRange`
        should include.
    
    :param datetime.date last: the last day that the :py:class:`DayRange` should
        include.
    
    :raises TypeError: if either `first` or `last` is not a
        :py:class:`datetime.date`.
    
    :raises ValueError: if `first` is after `last`.
    
    For example::

        from datetime import date
        
        dayRange = DayRange(date(2020, 1, 1), date(2020, 12, 31))
    """
    __slots__ = ('__first', '__last')
    def __init__(self, first, last):
        # type: (datetime.date, datetime.date) -> None
        self.__first = private.checkDate(first, 'first')
        if last is not first:
            private.checkDate(last, 'last')
            if first > last:
                raise ValueError("first (%r) cannot be > last (%r)" % (first, last))
        self.__last = last
    def _equalityFields(self):
        return (self.__first, self.__last)
    @staticmethod
    def singleDay(firstAndLast): # type: (datetime.date) -> DayRange
        return DayRange(firstAndLast, firstAndLast)
    @property
    def first(self): # type: () -> datetime.date
        """The first day in this :py:class:`DayRange`."""
        return self.__first
    @property
    def last(self): # type: () -> datetime.date
        """The last day in this :py:class:`DayRange`."""
        return self.__last
    def __containsDate(self, testDate): # type: (datetime.date) -> bool
        return (testDate >= self.__first and testDate <= self.__last)
    def contains(self, testDateOrDayRange):
        # type: (datetime.date | DayRange) -> bool
        """Returns `True` if the specified `testDateOrDayRange` is contained
        within this :py:class:`DayRange`; `False` otherwise.
        
        :param datetime.date | DayRange testDateOrDayRange: a
            :py:class:`datetime.date` or :py:class:`DayRange` to test for
            containment within this :py:class:`DayRange`.

        :return: `True` if `testDateOrDayRange` is a :py:class:`datetime.date`
            that is equal to or after the :py:attr:`first` day of this
            :py:class:`DayRange` and equal to or before the :py:attr:`last` day
            of this :py:class:`DayRange`, or if `testDateOrDayRange` is a
            :py:class:`DayRange` with a :py:attr:`first` day equal to or after
            the :py:attr:`first` day of this :py:class:`DayRange` and a
            :py:attr:`last` day equal to or before the :py:attr:`last` day of
            this :py:class:`DayRange`; `False` otherwise.
        
        :raises TypeError: if `testDateOrDayRange` is neither a
            :py:class:`datetime.date` nor a :py:class:`DayRange`."""
        if type(testDateOrDayRange) is datetime.date:
            return self.__containsDate(testDateOrDayRange)
        elif type(testDateOrDayRange) is DayRange:
            return (self.__containsDate(testDateOrDayRange.first) and
                self.__containsDate(testDateOrDayRange.last))
        else:
            raise TypeError(('testDateOrDayRange should be either a '
                'datetime.date or a degreedays.time.DayRange, not a %s.') %
                private.fullNameOfClass(testDateOrDayRange.__class__))
    def __len__(self): # type: () -> int
        """To get the number of days covered by a :py:class:`DayRange` (always 1
        or more).  For example::

            numberOfDays = len(dayRange)
        """
        return (self.last - self.first).days + 1
    def __iter__(self): # type: () -> Iterator[datetime.date]
        """To iterate over each :py:class:`datetime.date` within a
        :py:class:`DayRange`.  For example::

            for d in dayRange:
                print(d)
        """
        for i in range(len(self)):
            yield self.first + datetime.timedelta(days=i)
    def __repr__(self):
        return 'DayRange(%r, %r)' % (self.__first, self.__last)
    def __str__(self):
        return '%s to %s' % (self.__first, self.__last)
    def _toXml(self, elementName = 'DayRange'): # type: (str) -> XmlElement
        return XmlElement(elementName) \
                .addAttribute("first", self.__first.isoformat()) \
                .addAttribute("last", self.__last.isoformat())
    @staticmethod
    def _check(param, paramName='dayRange'):
        # type: (DayRange, str) -> DayRange
        if type(param) is not DayRange:
            raise TypeError(private.wrongTypeString(param, paramName,
                DayRange, _DAY_RANGE_EXAMPLE))
        return param

_DAY_RANGES_EXAMPLE = ('DayRanges('
    'DayRange(datetime.date(2020, 1, 1), datetime.date(2020, 3, 31)), '
    'DayRange(datetime.date(2020, 4, 1), datetime.date(2020, 6, 30)))')
class _DayRangesTupleBuilder(object):
    __slots__ = ('__list', 'isContiguous', '__lastAddedOrNone')
    def __init__(self):
        self.__list = [] # type: list[DayRange]
        self.isContiguous = True
        self.__lastAddedOrNone = None
    def add(self, item): # type: (DayRange | Iterable[DayRange]) -> None
        if type(item) is DayRange:
            if self.__lastAddedOrNone is not None:
                daysAfter = (item.first - self.__lastAddedOrNone.last).days
                if daysAfter > 1:
                    self.isContiguous = False
                elif daysAfter <= 0:
                    raise ValueError(('Problem DayRange items: %s cannot be '
                        'followed by %s because DayRange items must be in '
                        'in chronological order, without overlap.') % \
                        (self.__lastAddedOrNone, item))
            self.__list.append(item)
            self.__lastAddedOrNone = item
        elif private.isString(item):
            DayRange._check(item, # type: ignore
                'An item passed into the DayRanges constructor')
        else:
            # assume it's a sequence, just let it throw error if not
            for innerItem in item:
                self.add(innerItem) # type: ignore
    def build(self): # type: () -> tuple[DayRange, ...]
        return tuple(self.__list)

class DayRanges(_Immutable):
    """A chronologically-ordered set of one or more non-overlapping
    :py:class:`DayRange` objects.

    Create by passing in any number of :py:class:`DayRange` objects e.g. ::
    
        dayRanges = DayRanges(dayRange1, dayRange2, dayRange3)

    or by passing in a sequence of :py:class:`DayRange` objects e.g. ::

        listOfDayRangeObjects = [dayRange1, dayRange2, dayRange3]
        dayRanges = DayRanges(listOfDayRangeObjects)

    :raises TypeError: if anything passed in is not a :py:class:`DayRange`
        object or sequence of :py:class:`DayRange` objects.

    :raises ValueError: if there is not at least one :py:class:`DayRange` passed
        in, or if any of the :py:class:`DayRange` objects overlap or are not in
        chronological order."""
    __slots__ = ('__dayRanges', '__isContiguous')
    def __init__(self, *args): # type: (DayRange | Iterable[DayRange]) -> None
        builder = _DayRangesTupleBuilder()
        for arg in args:
            builder.add(arg)
        self.__dayRanges = builder.build()
        if len(self.__dayRanges) == 0:
            raise ValueError('Must have at least one DayRange.')
        self.__isContiguous = builder.isContiguous
    def _equalityFields(self):
        return self.__dayRanges
    @property
    def isContiguous(self): # type: () -> bool
        """`True` if each contained :py:class:`DayRange` starts the day after
        the previous :py:class:`DayRange` ended (i.e. no gaps); `False`
        otherwise."""
        return self.__isContiguous
    @property
    def fullRange(self): # type: () -> DayRange
        """The :py:class:`DayRange` extending from the first day of the first
        :py:class:`DayRange` to the last day of the last :py:class:`DayRange` in
        this chronologically-ordered set."""
        return DayRange(self.__dayRanges[0].first, self.__dayRanges[-1].last)
    def __len__(self):
        """To get the number of :py:class:`DayRange` objects in this set.  For
        example::

            count = len(dayRanges)
        """
        return len(self.__dayRanges)
    def __iter__(self):
        """To iterate over the :py:class:`DayRange` objects in this set.  For
        example::

            for r in dayRanges:
                print(r)
        """
        return self.__dayRanges.__iter__()
    def __getitem__(self, index): # type: (int) -> DayRange
        """To get the :py:class:`DayRange` object at the specified `index`.  For
        example::

            first = dayRanges[0]
        """
        return self.__dayRanges[index]
    def __str__(self):
        length = len(self.__dayRanges)
        return 'DayRanges(%d value%s covering %s)' % (length,
            's' if length > 1 else '', self.fullRange)
    def __repr__(self):
        # self.__dayRanges is a tuple so that will add brackets.  But we don't
        # need double brackets, so we do DayRanges%r instead of DayRanges(%r).
        return 'DayRanges%r' % (self.__dayRanges,)
    def _toXml(self, elementName = 'DayRanges'): # type: (str) -> XmlElement
        e = XmlElement(elementName)
        for r in self.__dayRanges:
            e.addChild(r._toXml())
        return e
    @staticmethod
    def _check(param, paramName='dayRanges'):
        # type: (DayRanges, str) -> DayRanges
        if type(param) is not DayRanges:
            raise TypeError(private.wrongTypeString(param, paramName,
                DayRange, _DAY_RANGES_EXAMPLE))
        return param

_DAY_OF_WEEK_EXAMPLE = ('DayOfWeek.MONDAY, DayOfWeek.TUESDAY, ..., or '
    'DayOfWeek(0) for Monday etc. (using the int constants that Python uses in '
    'its calendar module)')
# This metaclass stuff is to make it possible to iterate over the values, like
# "for dow in DayOfWeek".  See TemperatureUnit for an explanation and
# references.
class _DayOfWeekMetaclass(type):
    def __iter__(cls): # type: () -> Iterator[DayOfWeek]
        for i in range(7):
            yield DayOfWeek(i)
    #EnumCopyStart(DayOfWeek)
    @property
    def MONDAY(cls): # type: () -> DayOfWeek
        """Representing Monday, with a `str` value of ``'Monday'``, an
        :py:attr:`index` of 0, and an :py:attr:`isoIndex` of 1.

        Access via: ``DayOfWeek.MONDAY``"""
        return DayOfWeek(0)
    @property
    def TUESDAY(cls): # type: () -> DayOfWeek
        """Representing Tuesday, with a `str` value of ``'Tuesday'``, an
        :py:attr:`index` of 1, and an :py:attr:`isoIndex` of 2.

        Access via: ``DayOfWeek.TUESDAY``"""
        return DayOfWeek(1)
    @property
    def WEDNESDAY(cls): # type: () -> DayOfWeek
        """Representing Wednesday, with a `str` value of ``'Wednesday'``, an
        :py:attr:`index` of 2, and an :py:attr:`isoIndex` of 3.

        Access via: ``DayOfWeek.WEDNESDAY``"""
        return DayOfWeek(2)
    @property
    def THURSDAY(cls): # type: () -> DayOfWeek
        """Representing Thursday, with a `str` value of ``'Thursday'``, an
        :py:attr:`index` of 3, and an :py:attr:`isoIndex` of 4.

        Access via: ``DayOfWeek.THURSDAY``"""
        return DayOfWeek(3)
    @property
    def FRIDAY(cls): # type: () -> DayOfWeek
        """Representing Friday, with a `str` value of ``'Friday'``, an
        :py:attr:`index` of 4, and an :py:attr:`isoIndex` of 5.

        Access via: ``DayOfWeek.FRIDAY``"""
        return DayOfWeek(4)
    @property
    def SATURDAY(cls): # type: () -> DayOfWeek
        """Representing Saturday, with a `str` value of ``'Saturday'``, an
        :py:attr:`index` of 5, and an :py:attr:`isoIndex` of 6.

        Access via: ``DayOfWeek.SATURDAY``"""
        return DayOfWeek(5)
    @property
    def SUNDAY(cls): # type: () -> DayOfWeek
        """Representing Sunday, with a `str` value of ``'Sunday'``, an
        :py:attr:`index` of 6, and an :py:attr:`isoIndex` of 7.

        Access via: ``DayOfWeek.SUNDAY``"""
        return DayOfWeek(6)
    #EnumCopyEnd
_DayOfWeekSuper = _DayOfWeekMetaclass('_DayOfWeekSuper', (_Immutable,),
    {'__slots__': ()})
class DayOfWeek(_DayOfWeekSuper):
    """Defines the day of the week, with class constants to represent all 7
    (Monday to Sunday)."""
    __slots__ = ('__index', '__name', '__nameUpper', '__isoIndex')
    __map = {} # type: dict[int, DayOfWeek]
    #EnumPaste(DayOfWeek)
    # Make new source to build sphinx from, remove for final source or just make
    # it look like a comment.
    def __initImpl(self, index, name): # type: (int, str) -> None
        self.__index = index
        self.__name = name
        self.__nameUpper = name.upper()
        self.__isoIndex = index + 1
    # We need this because of the way we're caching values and allowing direct
    # use of the constructor with indexes (e.g. DayOfWeek(0) for Monday) so we
    # can take the int constants python's calendar module uses.  This prevents
    # direct use of the constructor from creating a new instance each time.
    def __new__(cls, index): # type: (int) -> DayOfWeek
        """:meta private:"""
        existing = DayOfWeek.__map.get(index, None)
        if existing is not None:
            return existing
        newItem = super(DayOfWeek, cls).__new__(cls)
        if index == 0:
            newItem.__initImpl(0, 'Monday')
        elif index == 1:
            newItem.__initImpl(1, 'Tuesday')
        elif index == 2:
            newItem.__initImpl(2, 'Wednesday')
        elif index == 3:
            newItem.__initImpl(3, 'Thursday')
        elif index == 4:
            newItem.__initImpl(4, 'Friday')
        elif index == 5:
            newItem.__initImpl(5, 'Saturday')
        elif index == 6:
            newItem.__initImpl(6, 'Sunday')
        else:
            raise ValueError('Invalid int value for day of week (%r) - '
                'expecting int between 0 (Monday) and 6 (Sunday).')
        DayOfWeek.__map[newItem.__index] = newItem
        return newItem
    def __getattr__(self, name): # type: (str) -> str
        return getattr(_DayOfWeekMetaclass, name)
    def _equalityFields(self): # type: () -> object
        return self.__index
    @property
    def index(self): # type: () -> int
        """The index used by Python's :py:mod:`calendar` module to represent
        this day of the week: 0 for Monday, 1 for Tuesday, 2 for Wednesday, 3
        for Thursday, 4 for Friday, 5 for Saturday, and 6 for Sunday."""
        return self.__index
    @property
    def isoIndex(self): # type: () -> int
        """The ISO weekday number for this :py:class:`DayOfWeek`: 1 for
        Monday, 2 for Tuesday, 3 for Wednesday, 4 for Thursday, 5 for Friday, 6
        for Saturday, and 7 for Sunday."""
        return self.__isoIndex
    def __str__(self):
        return self.__name
    def __repr__(self):
        return 'DayOfWeek.' + self.__nameUpper
    @staticmethod
    def _check(param, paramName='dayOfWeek'):
        # type: (DayOfWeek, str) -> DayOfWeek
        if type(param) is not DayOfWeek:
            raise TypeError(private.wrongTypeString(param, paramName,
                DayOfWeek, _DAY_OF_WEEK_EXAMPLE))
        return param

_START_OF_MONTH_EXAMPLE = ("StartOfMonth(1) for regular calendar months "
    "starting on the 1st of each month, "
    "StartOfMonth(2) for the \"months\" starting on the 2nd of each month, "
    "etc.")
class StartOfMonth(_Immutable):
    """Specifies a definition of "months" that begin on a specified day of the
    month (e.g. 1 for calendar months).
    
    :param int dayOfMonth: a number between 1 and 28 (inclusive) indicating
        which day should be taken as the start of the "month". Pass 1 to specify
        regular calendar months.

    :raises TypeError: if `dayOfMonth` is not an `int`.

    :raises ValueError: if `dayOfMonth` is less than 1 or greater than 28."""
    __slots__ = ('__dayOfMonth',)
    def __init__(self, dayOfMonth): # type: (int) -> None
        private.checkInt(dayOfMonth, 'dayOfMonth')
        if (dayOfMonth < 1 or dayOfMonth > 28):
            raise ValueError('Invalid dayOfMonth (' +
                str(dayOfMonth) + ') - it cannot be less than 1 '
                'or greater than 28 (to ensure it can work for all '
                'months of all years).')
        self.__dayOfMonth = dayOfMonth
    def _equalityFields(self):
        return self.__dayOfMonth
    @property
    def dayOfMonth(self): # type: () -> int
        """A number between 1 and 28 (inclusive) indicating which day should be
        taken as the first of the month."""
        return self.__dayOfMonth
    def __repr__(self):
        return 'StartOfMonth(%d)' % self.__dayOfMonth
    def __str__(self):
        return '---%02d' % self.__dayOfMonth
    @staticmethod
    def _check(param, paramName='startOfMonth'):
        # type: (StartOfMonth, str) -> StartOfMonth
        if type(param) is not StartOfMonth:
            raise TypeError(private.wrongTypeString(param, paramName,
                StartOfMonth, _START_OF_MONTH_EXAMPLE))
        return param

def _minNoDaysInMonth(monthOfYear): # type: (int) -> int
    return [
        0, # dummy value, just so the first month index is 1.
        31, # Jan
        29, # Feb
        31, # Mar
        30, # Apr
        31, # May
        30, # Jun
        31, # Jul
        31, # Aug
        30, # Sep
        31, # Oct
        30, # Nov
        31 # Dec
    ][monthOfYear]

_START_OF_YEAR_EXAMPLE = ("StartOfYear(1, 1) for regular calendar years "
    "starting on the 1st of January, "
    "StartOfYear(4, 6) for \"years\" starting on the 6th of April, etc.")
class StartOfYear(_Immutable):
    """Specifies a definition of "years" that begin on a specified day of the
    year (e.g. January 1st for calendar years).

    :param int monthOfYear: a number between 1 and 12 (inclusive) indicating the
        month of the year in which the "year" should start.  For example, if
        you're working with UK financial years, choose 4 to specify that your
        "years" start in April.

    :param int dayOfMonth: a number between 1 and the number of days in
        `monthOfYear` (inclusive) indicating which day in `monthOfYear` should
        be taken as the first day of the "year". Note that the upper limit for
        February (``monthOfYear == 2``) is 28, not 29, since February only has
        29 days on leap years and a :py:class:`StartOfYear` must be applicable
        to *all* years.
    
    :raises TypeError: if `monthOfYear` or `dayOfMonth` is not an `int`.

    :raises ValueError: if `monthOfYear` and/or `dayOfMonth` are invalid
        according to the rules explained above."""
    __slots__ = ('__monthOfYear', '__dayOfMonth')
    def __init__(self, monthOfYear, dayOfMonth): # type: (int, int) -> None
        private.checkInt(monthOfYear, 'monthOfYear')
        private.checkInt(dayOfMonth, 'dayOfMonth')
        if (monthOfYear < 1 or monthOfYear > 12):
            raise ValueError('Invalid monthOfYear (' + str(monthOfYear) +
                ') - it cannot be less than 1 (January) or greater than 12 '
                '(December).')
        if dayOfMonth < 1:
            raise ValueError('Invalid dayOfMonth (' + str(dayOfMonth) +
                ') - it cannot be less than 1.')
        if (monthOfYear == 2 and dayOfMonth > 28):
            raise ValueError('Invalid dayOfMonth (' + str(dayOfMonth) + ') - '
                'when when the month is February (2), the day cannot be '
                'greater than 28.')
        noDaysInMonth = _minNoDaysInMonth(monthOfYear)
        if dayOfMonth > noDaysInMonth:
            raise ValueError('Invalid dayOfMonth (' + str(dayOfMonth) +
                ') - it cannot be greater than ' + str(noDaysInMonth) +
                ' when the month is ' + str(monthOfYear) + '.')
        self.__monthOfYear = monthOfYear
        self.__dayOfMonth = dayOfMonth
    def _equalityFields(self):
        return (self.__monthOfYear, self.__dayOfMonth)
    @property
    def monthOfYear(self): # type: () -> int
        """The number between 1 (January) and 12 (December) indicating the month
        of the calendar year in which the "year" defined by this
        :py:class:`StartOfYear` starts."""
        return self.__monthOfYear
    @property
    def dayOfMonth(self): # type: () -> int
        """The number between 1 and the number of days in :py:attr:`monthOfYear`
        (inclusive) indicating which day in :py:attr:`monthOfYear` is the first
        day of the "year" defined by this :py:class:`StartOfYear`.
        
        If :py:attr:`monthOfYear` is 2 (for February), this
        :py:attr:`dayOfMonth` will never be greater than 28, as February 29th
        only exists in leap years, and :py:class:`StartOfYear` has to be
        applicable to all years."""
        return self.__dayOfMonth
    def __repr__(self):
        return 'StartOfYear(%d, %d)' % (self.__monthOfYear, self.__dayOfMonth)
    def __str__(self):
        return '--%02d-%02d' % (self.monthOfYear, self.dayOfMonth)
    @staticmethod
    def _check(param, paramName='startOfYear'):
        # type: (StartOfYear, str) -> StartOfYear
        if type(param) is not StartOfYear:
            raise TypeError(private.wrongTypeString(param, paramName,
                StartOfYear, _START_OF_YEAR_EXAMPLE))
        return param

# Like datetime.timezone, but works in Python < 3.2.  Private because some
# day we may want to discontinue it and use only datetime.timezone instead.
# But we keep it here as opposed to putting it in _private.py because we want
# a good namespace for pickling.  Pickling is important for this because it
# goes inside datetime objects, and, as those are part of standard python,
# people will probably expect to be able to pickle them.
class _TimeZone(_Immutable, datetime.tzinfo):
    __slots__ = ('__offset',)
    # See datetime.timezone for and tzinfo docs for this curious structure.
    # We need a no-args init for pickling, says tzinfo.
    def __new__(cls, offset): # type: (datetime.timedelta) -> _TimeZone
        if type(offset) is not datetime.timedelta:
            raise ValueError('Expecting a datetime.timedelta')
        # we don't use offset.total_seconds() cos it was only added in 3.2
        totalMinutes = (offset.days * 1440) + (offset.seconds // 60)
        if totalMinutes < -1080 or totalMinutes > 1080:
            raise ValueError(('Invalid offset (%s) - it cannot be '
                'less than -1080 or greater than 1080, to correspond with a '
                'time-zone range of -18:00 to +18:00.') % offset)
        # Could disallow seconds and microseconds as we don't need them or
        # use them.
        return cls._create(offset)
    @classmethod
    def _create(cls, offset): # type: (datetime.timedelta) -> _TimeZone
        self = object.__new__(cls)
        self.__offset = offset
        return self
    def __getinitargs__(self):
        # for pickling.  tzinfo.__reduce__ calls this.
        return (self.__offset,)
    def _equalityFields(self): # type: () -> object
        return self.__offset
    def utcoffset(self, dt):
        # type: (datetime.datetime | None) -> datetime.timedelta
        return self.__offset
    def tzname(self, dt): # type: (datetime.datetime | None) -> str
        # aim for same format as datetime.timezone
        iso = private.formatUtcOffset(self.__offset)
        if iso == 'Z':
            # This is what python 3.8's timezone class does.  Python 3.4
            # returns UTC+00:00.  We go with UTC cos that makes more sense.
            return 'UTC'
        else:
            return 'UTC' + iso
    def dst(self, dt): # type: (datetime.datetime | None) -> None
        return None
    def fromutc(self, dt): # type: (datetime.datetime) -> datetime.datetime
        if not isinstance(dt, datetime.datetime):
            raise TypeError('dt should be a datetime')
        elif dt.tzinfo is not self:
            raise ValueError('dt.tzinfo should be self')
        return dt + self.__offset
    def __str__(self):
        return self.tzname(None)
    def __repr__(self):
        return '%s(%r)' % (private.fullNameOfClass(self.__class__),
            self.__offset)

try:
    datetime.timezone  # attempt to evaluate datetime.timezone
    def _createTimeZone(offset):
        # type: (datetime.timedelta) -> datetime.timezone
        return datetime.timezone(offset)
except AttributeError:
    def _createTimeZone(offset):
        # type: (datetime.timedelta) -> _TimeZone
        return _TimeZone(offset)
