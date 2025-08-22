
"""
Implementations of abstract types from :doc:`degreedays.api.data`.  These
classes provide a range of options for specifying the data you want as part of a
:py:class:`LocationDataRequest <degreedays.api.data.LocationDataRequest>`.

Instead of accessing these classes directly, it's generally easier to use the
static factory methods on the abstract types in :doc:`degreedays.api.data`.  For
example, when you need to create a :py:class:`Location
<degreedays.api.data.Location>` object, type ``Location.`` and your IDE should
pop up static factory methods for the various location types that you can choose
from, like :py:meth:`Location.stationId
<degreedays.api.data.Location.stationId>` and :py:meth:`Location.postalCode
<degreedays.api.data.Location.postalCode>`.

Whether you're using the static-factory methods or not, this module is the place
to look for detailed documentation on the types it contains.
"""

import re
from degreedays._private import XmlElement
import degreedays._private as private
import degreedays.time
import degreedays.geo
import degreedays.api.data as data

# Define __all__ as it's the easiest way to make sure that none of our other
# imports (things from geo, time, and _private) become available to anyone that
# does an import * on this module.
__all__ = ['StationIdLocation', 'LongLatLocation', 'PostalCodeLocation',
    'LatestValuesPeriod', 'DayRangePeriod',
    'DailyBreakdown', 'WeeklyBreakdown', 'MonthlyBreakdown', 'YearlyBreakdown',
    'CustomBreakdown', 'FullYearsAverageBreakdown',
    'HeatingDegreeDaysCalculation', 'CoolingDegreeDaysCalculation',
    'TemperatureTimeSeriesCalculation']

class StationIdLocation(data.Location):
    #1 inheritance-diagram:: StationIdLocation
    """Specifies a location in terms of a weather station ID (you can find these
    IDs through the website at `www.degreedays.net
    <https://www.degreedays.net/>`__ or by requesting data for
    :py:class:`GeographicLocation <degreedays.api.data.GeographicLocation>`
    types).

    :param str stationId: the ID of the weather station that the
        ``StationIdLocation`` should represent (i.e. the station you want data
        for). Cannot be empty, cannot contain contain any characters other than
        ``[-_0-9a-zA-Z]``, and cannot contain more than 60 characters (a limit
        that is significantly larger than the length of any station ID that we
        are currently aware of, but that is set high to allow for "virtual
        station IDs" to be introduced in the future, combining data from
        multiple stations).
    :raises TypeError: if `stationId` is not a ``str``.
    :raises ValueError: if tests indicate that `stationId` fails to match the
        specification detailed above."""
    __slots__ = ('__stationId',)
    def __init__(self, stationId): # type: (str) -> None
        self.__stationId = private.checkStationId(stationId, True).upper()
    def _equalityFields(self):
        return self.__stationId
    @property
    def stationId(self): # type: () -> str
        """The non-empty string ID of the weather station that this
        ``StationIdLocation`` represents."""
        return self.__stationId
    def __repr__(self):
        return "StationIdLocation('%s')" % self.__stationId
    def _toXml(self):
        return XmlElement("StationIdLocation").addChild(
                XmlElement("StationId").setValue(self.__stationId))

class LongLatLocation(data.GeographicLocation):
    #1 inheritance-diagram:: LongLatLocation
    """Specifies a location in terms of longitude and latitude coordinates. The
    API will hunt for a weather station near the specified location that is able
    to supply the requested data, or it might (at some point) average data from
    multiple weather stations around the specified location if it thinks that
    might significantly improve results.

    :param LongLat longLat: the longitude/latitude position.
    :raises TypeError: if `longLat` is not a :py:class:`degreedays.geo.LongLat`
        object.

    Make sure to specify the full range of data that you want when using this
    location type - some weather stations have less data than others so it's
    important for the API to have the full range when it's choosing which
    station(s) to use. The :py:class:`LocationDataResponse
    <degreedays.api.data.LocationDataResponse>` will include an station ID that
    will enable you to fetch new data calculated from the same weather
    station(s) used by the API initially.

    See also: :py:class:`GeographicLocation
    <degreedays.api.data.GeographicLocation>`"""
    __slots__ = ('__longLat',)
    def __init__(self, longLat): # type: (degreedays.geo.LongLat) -> None
        self.__longLat = degreedays.geo.LongLat._check(longLat)
    def _equalityFields(self):
        return self.__longLat
    @property
    def longLat(self): # type: () -> degreedays.geo.LongLat
        """The longitude/latitude position of this ``LongLatLocation``."""
        return self.__longLat
    def __repr__(self):
        return 'LongLatLocation(%r)' % self.__longLat
    def _toXml(self):
        return XmlElement("LongLatLocation").addChild(
                self.__longLat._toXml())

# See notes in private on regexp testing.
_POSTAL_CODE_REGEXP_STRING = '[- 0-9a-zA-Z]{1,16}$'
_POSTAL_CODE_REGEXP = re.compile(_POSTAL_CODE_REGEXP_STRING)
def _getValidPostalCode(postalCode): # type: (str) -> str
    private.checkString(postalCode, 'postalCode')
    # Work on assumption that this could be user input, so auto-correct for
    # leading or trailing whitespace.
    postalCode = postalCode.strip()
    if not _POSTAL_CODE_REGEXP.match(postalCode):
        raise ValueError('Invalid postalCode (%r) - it should match the '
            'regular expression %s.' % (postalCode, _POSTAL_CODE_REGEXP_STRING))
    return postalCode.upper()

_COUNTRY_CODE_REGEXP = re.compile('[A-Z]{2}$')
def _getValidCountryCode(countryCode): # type: (str) -> str
    private.checkString(countryCode, 'countryCode')
    # Be strict about this - it's unlikely to be user input as the user would
    # probably select from a list of countries mapped to valid codes.  i.e. we
    # don't do any whitespace stripping, and we're strict about case.
    if not _COUNTRY_CODE_REGEXP.match(countryCode):
        raise ValueError('Invalid country code (%r) - it should be 2 upper-'
            'case alphabetical characters (A - Z).' % countryCode)
    return countryCode

class PostalCodeLocation(data.GeographicLocation):
    #1 inheritance-diagram:: PostalCodeLocation
    """Specifies a location using a postal code (or zip code, post code, or
    postcode - the terminology depends on the country). The API servers will
    attempt to find the longitude/latitude location of the specified postal
    code, and from that point on will treat the location as if it were a
    :py:class:`LongLatLocation` (see the notes for that class for more relevant
    information).

    :param str postalCode: the postal code (or zip code, post code, or postcode)
        of the location you want data for. Cannot be empty, cannot be longer
        than 16 characters (a length that we believe allows for all current
        postal codes worldwide), and cannot contain any characters other than
        ``[- 0-9a-zA-Z]``.
    :param str twoLetterIsoCountryCodeInUpperCase: the `ISO 3166-1-alpha-2
        country code <http://www.iso.org/iso/country_codes/
        iso_3166_code_lists/country_names_and_code_elements.htm>`__ of the
        country that `postalCode` belongs to. It must be a two-character string
        comprised of only characters A-Z (i.e. upper case only). For example,
        pass "US" if `postalCode` is a US zip code, pass "GB" (for "Great
        Britain") if `postalCode` is a UK post code, and pass "CA" if
        `postalCode` is a Canadian zip code.
    :raises TypeError: if `postalCode` or `twoLetterIsoCountryCodeInUpperCase`
        is not a ``str``.
    :raises ValueError: if tests indicate that `postalCode` or
        `twoLetterIsoCountryCodeInUpperCase` fails to match the specifications
        detailed above."""
    __slots__ = ('__postalCode', '__countryCode')
    def __init__(self, postalCode, countryCode): # type: (str, str) -> None
        self.__postalCode = _getValidPostalCode(postalCode)
        self.__countryCode = _getValidCountryCode(countryCode)
    def _equalityFields(self):
        return (self.__postalCode, self.__countryCode)
    @property
    def postalCode(self): # type: () -> str
        """The non-empty postal code (or zip code, post code, or postcode - the
        terminology depends on the country)."""
        return self.__postalCode
    @property
    def countryCode(self): # type: () -> str
        """The two-letter upper-case `ISO 3166-1-alpha-2 country code
        <http://www.iso.org/iso/country_codes/
        iso_3166_code_lists/country_names_and_code_elements.htm>`__ of the
        country that the postal code belongs to."""
        return self.__countryCode
    def __repr__(self):
        return ("PostalCodeLocation('%s', '%s')" %
            (self.__postalCode, self.__countryCode))
    def _toXml(self):
        e = XmlElement("PostalCodeLocation")
        e.addChild(XmlElement("PostalCode").setValue(self.__postalCode))
        e.addChild(XmlElement("CountryCode").setValue(self.__countryCode))
        return e

class LatestValuesPeriod(data.Period):
    #1 inheritance-diagram:: LatestValuesPeriod
    """A type of :py:class:`Period <degreedays.api.data.Period>` that
    automatically resolves to a date range including the latest available data
    and the specified number of degree-day values.

    :param int numberOfValues: a number, greater than zero, that specifies how
        many degree-day values the period should cover (see below for an
        explanation of how the values in question can be daily, weekly, monthly,
        or yearly). This is effectively an upper bound: if there isn't enough
        good data to cover the `numberOfValues` specified, the API will assemble
        and return what it can.
    :param int | None minimumNumberOfValuesOrNone: you can specify this if you
        would rather have a failure than a partial set of data with less than
        your specified minimum number of values.  Otherwise you may get back
        less data than you asked for if there aren't enough weather-data records
        to generate a full set for your specified location.
    :raises TypeError: if `numberOfValues` is not an `int`, or if
        `minimumNumberOfValuesOrNone` is not an `int` or `None`.
    :raises ValueError: if `numberOfValues` is less than 1, or if
        `minimumNumberOfValuesOrNone` is an `int` that is less than 1 or greater
        than `numberOfValues`.
    
    The meaning of the specified number of values depends on the type of the
    :py:class:`Breakdown <degreedays.api.data.Breakdown>` that holds this
    period. For example, if you create a ``LatestValuesPeriod`` specifying *x*
    values then:

    * Used as the ``Period`` in a :py:class:`DailyBreakdown` it would specify
      the *x* most recent *days* of data.
    * Used as the ``Period`` in a :py:class:`WeeklyBreakdown` it would specify
      the *x* most recent *weeks* of data.
    * Used as the ``Period`` in a :py:class:`MonthlyBreakdown` it would specify
      the *x* most recent *months* of data.
    * Used as the ``Period`` in a :py:class:`YearlyBreakdown` it would specify
      the *x* most recent *years* of data.
    * Used as the ``Period`` in a :py:class:`FullYearsAverageBreakdown` it would
      specify the *x* most recent *full calendar years* of data.

    If you want data covering specific dates, you may be better off using a
    :py:class:`DayRangePeriod`. But this class can be a useful convenience if
    you want the latest available data containing a specific number of daily,
    weekly, monthly, or yearly values. It can save you from some date
    arithmetic, and you won't need to consider the time-zones or update delays
    of the weather stations that you're getting data from to figure out the
    exact dates of the latest data that is likely to be available."""
    __slots__ = ('__numberOfValues', '__minimumNumberOfValuesOrNone')
    def __init__(self, numberOfValues, minimumNumberOfValuesOrNone = None):
        # type: (int, int | None) -> None
        self.__numberOfValues = private.checkInt(
            numberOfValues, 'numberOfValues')
        if numberOfValues < 1:
            raise ValueError('Invalid numberOfValues (%s) - cannot be < 1.'
                % numberOfValues)
        self.__minimumNumberOfValuesOrNone = minimumNumberOfValuesOrNone
        if minimumNumberOfValuesOrNone is not None:
            private.checkInt(minimumNumberOfValuesOrNone, 'minimumNumberOfValuesOrNone')
            if minimumNumberOfValuesOrNone < 1:
                raise ValueError('Invalid minimumNumberOfValuesOrNone (%s) - cannot '
                    'be < 1 (though it can be None if there is to be no '
                    'minimum (the default).' % minimumNumberOfValuesOrNone)
            elif minimumNumberOfValuesOrNone > numberOfValues:
                raise ValueError('Invalid minimumNumberOfValuesOrNone (%s) - cannot '
                    'be > numberOfValues (%s).' %
                    (minimumNumberOfValuesOrNone, numberOfValues))
    def _equalityFields(self):
        return (self.__numberOfValues, self.__minimumNumberOfValuesOrNone)
    @property
    def numberOfValues(self): # type: () -> int
        """A number, greater than zero, indicating how many degree-day values
        this period should cover (the values in question can be daily, weekly,
        monthly, or yearly, depending on the type of the :py:class:`Breakdown
        <degreedays.api.data.Breakdown>` that holds this period)."""
        return self.__numberOfValues
    @property
    def minimumNumberOfValuesOrNone(self): # type: () -> int | None
        """The minimium number of values, greater than zero, that the API must
        include to provide data to the specification of this
        ``LatestValuesPeriod``, or `None` if no such minimum number is
        specified.
        
        If this is `None`, the API can decide what to do if there is not enough
        data available to satisfy the :py:attr:`numberOfValues` requested, and
        it will typically return as many values as it can. If a minimum number
        of values is specified, then a request for data will fail unless that
        minimum number of values can be satisfied."""
        return self.__minimumNumberOfValuesOrNone
    def __repr__(self):
        if self.__minimumNumberOfValuesOrNone is None:
            return 'LatestValuesPeriod(%d)' % self.__numberOfValues
        else:
            return 'LatestValuesPeriod(%d, %d)' % \
                (self.__numberOfValues, self.__minimumNumberOfValuesOrNone)
    def _toXml(self):
        e = XmlElement("LatestValuesPeriod").addChild(
            XmlElement("NumberOfValues").setValue(self.__numberOfValues))
        if self.__minimumNumberOfValuesOrNone is not None:
            e.addChild(XmlElement("MinimumNumberOfValues").setValue(
                self.__minimumNumberOfValuesOrNone))
        return e

class DayRangePeriod(data.Period):
    #1 inheritance-diagram:: DayRangePeriod
    """A type of :py:class:`Period <degreedays.api.data.Period>` that is defined
    explicitly in terms of the range of days that it covers.

    :param degreedays.time.DayRange dayRange: the range of days that the period
        should cover.
    :param degreedays.time.DayRange | None minimiumDayRangeOrNone: you can
        specify this if you would rather have a failure than a partial set of
        data covering less than your specified minimum range.  Otherwise you may
        get back less data than you asked for if there aren't enough
        weather-data records to generate a full set for your specified location.
        See :py:attr:`minimumDayRangeOrNone` for more on this.
    :raises TypeError: if `dayRange` is not a
        :py:class:`degreedays.time.DayRange`, or if `minimumDayRangeOrNone` is
        not a :py:class:`degreedays.time.DayRange` or `None`.
    :raises ValueError: if `minimumDayRangeOrNone` is a
        :py:class:`degreedays.time.DayRange` that extends earlier or later than
        `dayRange`.

    .. _widening:

    Widening: interpretation of a ``DayRangePeriod`` in the context of a ``Breakdown``
    ----------------------------------------------------------------------------------
    If the boundaries of a `DayRangePeriod` line up neatly with the date
    splitting of a :py:class:`Breakdown <degreedays.api.data.Breakdown>` that
    contains it, then the calculated data will cover the specified range exactly
    (or a subset of that range if there isn't enough data to satisfy the request
    fully). This will always be the case if the period is contained within a
    :py:class:`DailyBreakdown`.

    If you put a `DayRangePeriod` inside a :py:class:`WeeklyBreakdown`,
    :py:class:`MonthlyBreakdown`, :py:class:`YearlyBreakdown`, or
    :py:class:`FullYearsAverageBreakdown`, then it is up to you whether you
    ensure that the boundaries of your period line up neatly with the
    weekly/monthly/yearly splitting of the breakdown. If your period specifies
    dates that *do* line up with the breakdown, then those dates will be treated
    as an exact specification. If your period specifies dates that *don't* line
    up with the breakdown, the API will effectively widen the range (at the
    beginning, or the end, or both boundaries if necessary) to ensure that the
    returned data covers all the dates that your range specifies (assuming
    enough data exists to do this).

    The following examples should help to make this clearer:

    Widening example 1
    ^^^^^^^^^^^^^^^^^^
    .. code-block:: python

        period = Period.dayRange(degreedays.time.DayRange(
                datetime.date(2025, 2, 19), datetime.date(2025, 3, 5)))
        breakdown = DatedBreakdown.monthly(period)

    In this example you can see that the dates of the period (2025-02-19 to
    2025-03-05) do not match up with the calendar months that the
    ``MonthlyBreakdown`` specifies. In this instance the API would widen the
    range at both the beginning and the end, attempting to return one monthly
    value for February 2025 and one for March 2025.

    If the first day of the specified period was the first day of a breakdown
    month (e.g. 2025-02-01), the range would not have been widened at the start.
    Similarly, if the last day of the specified period was the last day of a
    breakdown month (e.g. 2025-03-31), the range would not have been widened at
    the end. Widening only occurs when the dates don't line up with the
    splitting of the breakdown.

    Widening example 2
    ^^^^^^^^^^^^^^^^^^
    .. code-block:: python

        singleDay = datetime.date(2024, 10, 21)
        period = Period.dayRange(degreedays.time.DayRange(singleDay, singleDay))
        breakdown = DatedBreakdown.yearly(period)

    In this example the period is specified to cover just one day: 2024-10-21.
    Of course, that period, if interpreted explicitly, is not long enough to
    allow a yearly breakdown.

    In this instance the API would widen the range at the beginning and the end,
    giving 2024-01-01 to 2024-12-31, so that it could return a yearly value for
    2024 (the year containing the specified range).

    Additional notes on widening
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    * When you create a ``DayRangePeriod`` object, that object will always
      contain the exact dates that you specified. Widening can only happen when
      those dates are being interpreted as part of the data-assembly process.
    * You can use widening to your advantage - passing approximate ranges and
      relying on the automatic widening can save you some date arithmetic and
      keep your code simpler.
    * Though be careful if you are fetching larger quantities of data and are
      concerned about rate limits... If, for example, you use an imprecise
      ``DayRangePeriod`` as part of a request for 12 months of monthly data
      (e.g. calendar months from 2024-01-14 to 2025-01-13), widening could push
      that to 13 months (e.g. 2024-01-01 to 2025-01-31), pushing you closer
      towards your rate limit than you would have wanted. This can't happen if
      you specify your dates precisely or use :py:class:`LatestValuesPeriod`
      instead of ``DayRangePeriod``."""
    __slots__ = ('__dayRange', '__minimumDayRangeOrNone')
    def __init__(self, dayRange, minimumDayRangeOrNone = None):
        # type: (degreedays.time.DayRange, degreedays.time.DayRange | None) -> None
        self.__dayRange = degreedays.time.DayRange._check(dayRange)
        if minimumDayRangeOrNone is not None:
            degreedays.time.DayRange._check(minimumDayRangeOrNone)
        self.__minimumDayRangeOrNone = minimumDayRangeOrNone
    def _equalityFields(self):
        return (self.__dayRange, self.__minimumDayRangeOrNone)
    @property
    def dayRange(self): # type: () -> degreedays.time.DayRange
        """The :py:class:`degreedays.time.DayRange` object that specifies the
        day(s) that this period covers."""
        return self.__dayRange
    @property
    def minimumDayRangeOrNone(self): # type: () -> degreedays.time.DayRange | None
        """The minimium day range the API must cover if it is able to generate
        data within this ``DayRangePeriod``, or `None` if no such minimum is
        specified.

        If this is `None`, the API can decide what to do if there is not enough
        data available to satisfy the :py:attr:`dayRange`, and it will typically
        return what it can from within :py:attr:`dayRange`. If a minimum day
        range is set, then a request for data will fail unless that minimum
        range can be satisfied.

        **Warning**: be careful with minimum ranges, particularly when defining
        the last day of a minimum range. The degree days for any given day will
        never become available until the day has finished *in the location's
        local time-zone*, and will always take at least a little longer (and
        sometimes quite a lot longer) for the `reasons explained here
        <https://www.degreedays.net/api/faq#update-schedules>`__. If your system
        specifies a minimum range that is too restrictive, it can easily end up
        with no data at all when in fact there's plenty of usable data
        available.

        That said, there are times when a minimum range with highly-restrictive
        dates is exactly what you want (and you'd rather get nothing than
        slightly less data), so don't be afraid to specify restrictive minimum
        ranges if you need them."""
        return self.__minimumDayRangeOrNone
    def __repr__(self):
        if self.__minimumDayRangeOrNone is None:
            return 'DayRangePeriod(%r)' % self.__dayRange
        else:
            return 'DayRangePeriod(%r, %r)' % \
                (self.__dayRange, self.__minimumDayRangeOrNone)
    def _toXml(self):
        e = XmlElement("DayRangePeriod").addChild(self.__dayRange._toXml())
        if self.__minimumDayRangeOrNone is not None:
            e.addChild(self.__minimumDayRangeOrNone._toXml('MinimumDayRange'))
        return e

class DailyBreakdown(data.DatedBreakdown):
    #1 inheritance-diagram:: DailyBreakdown
    """A type of :py:class:`DatedBreakdown <degreedays.api.data.DatedBreakdown>`
    used to specify that degree days should be broken down on a daily basis and
    cover a specific :py:class:`Period <degreedays.api.data.Period>` in time.

    :param Period period: the period in time that the daily breakdown should
        cover.
    :param bool allowPartialLatest: `True` to specify that the latest day of
        data can be partially filled (i.e. incomplete), or `False` if the latest
        day must be complete (the default behaviour).  Setting this to `True` is
        mainly useful if you are fetching time-series data (via
        :py:class:`TimeSeriesDataSpec <degreedays.api.data.TimeSeriesDataSpec>`)
        and you want it to include values for the current (incomplete) day. See
        :py:attr:`allowPartialLatest` for more on this.
    :raises TypeError: if `period` is not a :py:class:`Period
        <degreedays.api.data.Period>` object, or `allowPartialLatest` is not a
        `bool`."""
    __slots__ = ('__period', '__allowPartialLatest')
    def __init__(self, period, allowPartialLatest=False):
        # type: (data.Period, bool) -> None
        self.__period = data.Period._check(period)
        self.__allowPartialLatest = self._checkAllowPartialLatest(
            allowPartialLatest)
    def _equalityFields(self):
        return (self.__period, self.__allowPartialLatest)
    @property
    def period(self): # type: () -> data.Period
        """The period in time that the daily breakdown should cover."""
        return self.__period
    @property
    def allowPartialLatest(self): # type: () -> bool
        return self.__allowPartialLatest
    def _reprStart(self):
        return 'DailyBreakdown(%r' % self.__period
    def _toXml(self):
        e = XmlElement("DailyBreakdown").addChild(self.__period._toXml())
        return self._addAllowPartialLatestXml(e)

class WeeklyBreakdown(data.DatedBreakdown):
    #1 inheritance-diagram:: WeeklyBreakdown
    """A type of :py:class:`DatedBreakdown <degreedays.api.data.DatedBreakdown>`
    used to specify that degree days should be broken down on a weekly basis and
    cover a specific :py:class:`Period <degreedays.api.data.Period>` in time,
    with weeks starting on a specific day of the week.

    :param Period period: the period in time that the weekly breakdown should
        cover.
    :param DayOfWeek firstDayOfWeek: indicates which day should be taken as the
        first of each week.
    :param bool allowPartialLatest: `True` to specify that the latest week of
        data can be partially filled (i.e. incomplete), or `False` if the latest
        week must be complete (the default behaviour).  Setting this to `True`
        is mainly useful if you are fetching time-series data (via
        :py:class:`TimeSeriesDataSpec <degreedays.api.data.TimeSeriesDataSpec>`)
        and you want it to include the current (incomplete) week, including
        values for the current (incomplete) day. See
        :py:attr:`allowPartialLatest` for more on this.
    :raises TypeError: if `period` is not a :py:class:`Period
        <degreedays.api.data.Period>` object, or if `firstDayOfWeek` is not a
        :py:class:`degreedays.time.DayOfWeek` object, or if `allowPartialLatest`
        is not a `bool`."""
    __slots__ = ('__period', '__firstDayOfWeek', '__allowPartialLatest')
    def __init__(self, period, firstDayOfWeek, allowPartialLatest=False):
        # type: (data.Period, degreedays.time.DayOfWeek, bool) -> None
        self.__period = data.Period._check(period)
        self.__firstDayOfWeek = degreedays.time.DayOfWeek._check(
            firstDayOfWeek, 'firstDayOfWeek')
        self.__allowPartialLatest = self._checkAllowPartialLatest(
            allowPartialLatest)
    def _equalityFields(self):
        return (self.__period, self.__firstDayOfWeek,
            self.__allowPartialLatest)
    @property
    def period(self): # type: () -> data.Period
        """The period in time that the weekly breakdown should cover."""
        return self.__period
    @property
    def firstDayOfWeek(self): # type: () -> degreedays.time.DayOfWeek
        """The day of the week that should be the first of each weekly period."""
        return self.__firstDayOfWeek
    @property
    def allowPartialLatest(self): # type: () -> bool
        return self.__allowPartialLatest
    def _reprStart(self):
        return ('WeeklyBreakdown(%r, %r' %
            (self.__period, self.__firstDayOfWeek))
    def _toXml(self):
        e = XmlElement('WeeklyBreakdown') \
            .addChild(self.__period._toXml())
        e.addAttribute('firstDayOfWeek', str(self.__firstDayOfWeek))
        return self._addAllowPartialLatestXml(e)

class MonthlyBreakdown(data.DatedBreakdown):
    #1 inheritance-diagram:: MonthlyBreakdown
    """A type of :py:class:`DatedBreakdown <degreedays.api.data.DatedBreakdown>`
    used to specify that degree days should be broken down on a monthly basis
    and cover a specific :py:class:`Period <degreedays.api.data.Period>` in
    time.

    :param Period period: the period in time that the monthly breakdown should
        cover.
    :param StartOfMonth startOfMonth: specifying which day (between 1 and 28
        inclusive) should be taken as the first of each "month".
        ``StartOfMonth(1)`` is the default value and specifies regular calendar
        months.
    :param bool allowPartialLatest: `True` to specify that the latest month of
        data can be partially filled (i.e. incomplete), or `False` if the latest
        month must be complete (the default behaviour).  Setting this to `True`
        is mainly useful if you are fetching time-series data (via
        :py:class:`TimeSeriesDataSpec <degreedays.api.data.TimeSeriesDataSpec>`)
        and you want it to include the current (incomplete) month, including
        values for the current (incomplete) day. See
        :py:attr:`allowPartialLatest` for more on this.
    :raises TypeError: if `period` is not a :py:class:`Period
        <degreedays.api.data.Period>` object, or if `startOfMonth` is not a
        :py:class:`degreedays.time.StartOfMonth` object, or if
        `allowPartialLatest` is not a `bool`."""
    __slots__ = ('__period', '__startOfMonth', '__allowPartialLatest')
    def __init__(self, period, startOfMonth=degreedays.time.StartOfMonth(1),
            allowPartialLatest=False):
        # type: (data.Period, degreedays.time.StartOfMonth, bool) -> None
        self.__period = data.Period._check(period)
        self.__startOfMonth = degreedays.time.StartOfMonth._check(startOfMonth)
        self.__allowPartialLatest = self._checkAllowPartialLatest(
            allowPartialLatest)
    def _equalityFields(self):
        return (self.__period, self.__startOfMonth, self.__allowPartialLatest)
    @property
    def period(self): # type: () -> data.Period
        """The period in time that the monthly breakdown should cover."""
        return self.__period
    @property
    def startOfMonth(self): # type: () -> degreedays.time.StartOfMonth
        """The :py:class:`degreedays.time.StartOfMonth` object indicating which
        day should be taken as the first of each month (inclusive)."""
        return self.__startOfMonth
    @property
    def allowPartialLatest(self): # type: () -> bool
        return self.__allowPartialLatest
    def _reprStart(self):
        if self.__startOfMonth.dayOfMonth == 1:
            return 'MonthlyBreakdown(%r' % self.__period
        else:
            return ('MonthlyBreakdown(%r, %r' %
                (self.__period, self.__startOfMonth))
    def _toXml(self):
        e = XmlElement('MonthlyBreakdown') \
            .addChild(self.__period._toXml())
        if self.__startOfMonth.dayOfMonth != 1:
            e.addAttribute('startOfMonth', str(self.__startOfMonth))
        return self._addAllowPartialLatestXml(e)

class YearlyBreakdown(data.DatedBreakdown):
    #1 inheritance-diagram:: YearlyBreakdown
    """A type of :py:class:`DatedBreakdown <degreedays.api.data.DatedBreakdown>`
    used to specify that degree days should be broken down on a yearly (annual)
    basis and cover a specific :py:class:`Period <degreedays.api.data.Period>`
    in time.

    :param Period period: the period in time that the yearly breakdown should
        cover.
    :param StartOfYear startOfYear: specifying which day of the year (month and
        day of the month) should be taken as the first of each "year".
        ``StartOfYear(1, 1)`` is the default value and specifies regular
        calendar years.
    :param bool allowPartialLatest: `True` to specify that the latest year of
        data can be partially filled (i.e. incomplete), or `False` if the latest
        year must be complete (the default behaviour).  Setting this to `True`
        is mainly useful if you are fetching time-series data (via
        :py:class:`TimeSeriesDataSpec <degreedays.api.data.TimeSeriesDataSpec>`)
        and you want it to include the current (incomplete) year, including
        values for the current (incomplete) day. See
        :py:attr:`allowPartialLatest` for more on this.
    :raises TypeError: if `period` is not a :py:class:`Period
        <degreedays.api.data.Period>` object, or if `startOfYear` is not a
        :py:class:`degreedays.time.StartOfYear` object, or if
        `allowPartialLatest` is not a `bool`."""
    __slots__ = ('__period', '__startOfYear', '__allowPartialLatest')
    def __init__(self, period, startOfYear=degreedays.time.StartOfYear(1, 1),
            allowPartialLatest=False):
        # type: (data.Period, degreedays.time.StartOfYear, bool) -> None
        self.__period = data.Period._check(period)
        self.__startOfYear = degreedays.time.StartOfYear._check(startOfYear)
        self.__allowPartialLatest = self._checkAllowPartialLatest(
            allowPartialLatest)
    def _equalityFields(self):
        return (self.__period, self.__startOfYear, self.__allowPartialLatest)
    @property
    def period(self): # type: () -> data.Period
        """The period in time that the yearly breakdown should cover."""
        return self.__period
    @property
    def startOfYear(self): # type: () -> degreedays.time.StartOfYear
        """The :py:class:`degreedays.time.StartOfYear` object indicating which
        day should be taken as the first of each year (inclusive)."""
        return self.__startOfYear
    @property
    def allowPartialLatest(self): # type: () -> bool
        return self.__allowPartialLatest
    def _reprStart(self):
        if self.__startOfYear == degreedays.time.StartOfYear(1, 1):
            return 'YearlyBreakdown(%r' % self.__period
        else:
            return ('YearlyBreakdown(%r, %r' %
                (self.__period, self.__startOfYear))
    def _toXml(self):
        e = XmlElement('YearlyBreakdown').addChild(self.period._toXml())
        if self.startOfYear != degreedays.time.StartOfYear(1, 1):
            e.addAttribute('startOfYear', str(self.startOfYear))
        return self._addAllowPartialLatestXml(e)

class CustomBreakdown(data.DatedBreakdown):
    #1 inheritance-diagram:: CustomBreakdown
    """A type of :py:class:`DatedBreakdown <degreedays.api.data.DatedBreakdown>`
    used to specify that degree days should be broken down into the custom date
    ranges specified e.g. to match the dates of your energy-usage records.

    :param DayRanges dayRanges: specifying the dates that each degree-day figure
        should cover (typically matching the dates of your energy-usage
        records).
    :param bool allowPartialLatest: `True` to specify that the latest specified
        day range can be partially filled (i.e. incomplete), or `False` if it
        must be complete (the default behaviour).  Setting this to `True` is
        mainly useful if you are fetching time-series data (via
        :py:class:`TimeSeriesDataSpec <degreedays.api.data.TimeSeriesDataSpec>`)
        and you want it to include values for the current (incomplete) day. See
        :py:attr:`allowPartialLatest` for more on this.
    :raises TypeError: if `dayRanges` is not a
        :py:class:`degreedays.time.DayRanges` object, or if `allowPartialLatest`
        is not a `bool`."""
    __slots__ = ('__dayRanges', '__allowPartialLatest')
    def __init__(self, dayRanges, allowPartialLatest=False):
        # type: (degreedays.time.DayRanges, bool) -> None
        self.__dayRanges = degreedays.time.DayRanges._check(dayRanges)
        self.__allowPartialLatest = self._checkAllowPartialLatest(
            allowPartialLatest)
    def _equalityFields(self):
        return (self.__dayRanges, self.__allowPartialLatest)
    @property
    def dayRanges(self): # type: () -> degreedays.time.DayRanges
        """The :py:class:`degreedays.time.DayRanges` that specifies the dates
        that each degree-day figure should cover."""
        return self.__dayRanges
    @property
    def allowPartialLatest(self): # type: () -> bool
        return self.__allowPartialLatest
    def _reprStart(self):
        return 'CustomBreakdown(%r' % self.__dayRanges
    def _toXml(self):
        e = XmlElement('CustomBreakdown').addChild(self.__dayRanges._toXml())
        return self._addAllowPartialLatestXml(e)

class FullYearsAverageBreakdown(data.AverageBreakdown):
    #1 inheritance-diagram:: FullYearsAverageBreakdown
    """A type of :py:class:`AverageBreakdown
    <degreedays.api.data.AverageBreakdown>` used to specify that
    average-degree-day figures should be derived from data covering a specified
    number of full calendar years.

    :param Period period: specifies the full calendar years of data that the
        average figures should be derived from. Typically you'd want to use
        :py:meth:`Period.latestValues <degreedays.api.data.Period.latestValues>`
        for this, specifying at least 2 values (since an average of 1 year of
        data is not very meaningful). But you can also use
        :py:meth:`Period.dayRange <degreedays.api.data.Period.dayRange>` - in
        this case the period may be :ref:`widened <widening>` for calculation
        purposes to make it cover full calendar years.
    :raises TypeError: if `period` is not a :py:class:`Period
        <degreedays.api.data.Period>` object.

    The years used will always be consecutive
    (i.e. no gaps), and are specified using the :py:class:`Period
    <degreedays.api.data.Period>` passed into the constructor.

    Typically you'd want to use :py:meth:`Period.latestValues
    <degreedays.api.data.Period.latestValues>` to create the :py:class:`Period
    <degreedays.api.data.Period>`, to specify that the last year of the average
    should be the most recent full calendar year.

    If you want average data calculated using a different method, remember that
    you can always fetch dated data and calculate averages directly from that.
    """
    __slots__ = ('__period',)
    def __init__(self, period): # type: (data.Period) -> None
        self.__period = data.Period._check(period)
    def _equalityFields(self):
        return self.__period
    @property
    def period(self): # type: () -> data.Period
        """The period in time that the breakdown should average data from."""
        return self.__period
    def __repr__(self):
        return 'FullYearsAverageBreakdown(%r)' % self.__period
    def _toXml(self):
        return (XmlElement('FullYearsAverageBreakdown')
            .addChild(self.period._toXml()))

class HeatingDegreeDaysCalculation(data.Calculation):
    #1 inheritance-diagram:: HeatingDegreeDaysCalculation
    """A type of :py:class:`Calculation <degreedays.api.data.Calculation>` that
    specifies that heating degree days should be calculated and that holds the
    base temperature that they should be calculated to.

    :param Temperature baseTemperature: the base temperature that the heating
        degree days should be calculated to.
    :raises TypeError: if `baseTemperature` is not a :py:class:`Temperature
        <degreedays.api.data.Temperature>` object."""
    __slots__ = ('__baseTemperature',)
    def __init__(self, baseTemperature): # type: (data.Temperature) -> None
        self.__baseTemperature = data.Temperature._check(
            baseTemperature, 'baseTemperature')
    def _equalityFields(self):
        return self.__baseTemperature
    @property
    def baseTemperature(self): # type: () -> data.Temperature
        """The base temperature of the heating-degree-days calculation."""
        return self.__baseTemperature
    def __repr__(self):
        return 'HeatingDegreeDaysCalculation(%r)' % self.__baseTemperature
    def _toXml(self):
        return XmlElement('HeatingDegreeDaysCalculation').addChild(
                self.__baseTemperature._toXml('BaseTemperature'))

class CoolingDegreeDaysCalculation(data.Calculation):
    #1 inheritance-diagram:: CoolingDegreeDaysCalculation
    """A type of :py:class:`Calculation <degreedays.api.data.Calculation>` that
    specifies that cooling degree days should be calculated and that holds the
    base temperature that they should be calculated to.

    :param Temperature baseTemperature: the base temperature that the cooling
        degree days should be calculated to.
    :raises TypeError: if `baseTemperature` is not a :py:class:`Temperature
        <degreedays.api.data.Temperature>` object."""
    __slots__ = ('__baseTemperature',)
    def __init__(self, baseTemperature): # type: (data.Temperature) -> None
        self.__baseTemperature = data.Temperature._check(
            baseTemperature, 'baseTemperature')
    def _equalityFields(self):
        return self.__baseTemperature
    @property
    def baseTemperature(self): # type: () -> data.Temperature
        """The base temperature of the cooling-degree-days calculation."""
        return self.__baseTemperature
    def __repr__(self):
        return 'CoolingDegreeDaysCalculation(%r)' % self.__baseTemperature
    def _toXml(self):
        return XmlElement('CoolingDegreeDaysCalculation').addChild(
                self.__baseTemperature._toXml('BaseTemperature'))

class TemperatureTimeSeriesCalculation(data.TimeSeriesCalculation):
    #1 inheritance-diagram:: TemperatureTimeSeriesCalculation
    """A type of :py:class:`TimeSeriesCalculation
    <degreedays.api.data.TimeSeriesCalculation>` that specifies that temperature
    data should be calculated with the specified interval (e.g. hourly) and unit
    (e.g. Celsius).

    :param TemperatureUnit temperatureUnit: specifies whether the data should be
        calculated in Celsius or Fahrenheit.
    :raises TypeError: if `temperatureUnit` is not a :py:class:`TemperatureUnit
        <degreedays.api.data.TemperatureUnit>` object.

    :ref:`Find out why time-series data is "calculated"
    <why-is-time-series-data-calculated>`."""
    __slots__ = ('__interval', '__temperatureUnit')
    def __init__(self, interval, temperatureUnit):
        # type: (data.TimeSeriesInterval, data.TemperatureUnit) -> None
        self.__interval = data.TimeSeriesInterval._check(interval)
        self.__temperatureUnit = \
            data.TemperatureUnit._check(temperatureUnit)
    def _equalityFields(self):
        return (self.__interval, self.__temperatureUnit)
    @property
    def interval(self): # type: () -> data.TimeSeriesInterval
        return self.__interval
    @property
    def temperatureUnit(self): # type: () -> data.TemperatureUnit
        """The :py:class:`TemperatureUnit <degreedays.api.data.TemperatureUnit>`
        indicating whether the temperatures should be calculated in Celsius or
        Fahrenheit."""
        return self.__temperatureUnit
    def __repr__(self):
        return 'TemperatureTimeSeriesCalculation(%r, %r)' % \
            (self.__interval, self.__temperatureUnit)
    def _toXml(self):
        return XmlElement('TemperatureTimeSeriesCalculation') \
            .addChild(self.__interval._toXml()) \
            .addChild(self.__temperatureUnit._toXml())
