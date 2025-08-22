# -*- coding: utf-8 -*-

"""
For specifying and receiving degree-day data and temperature data from the API.

If you are new to this module, we suggest you start by looking at
:py:class:`DataApi`.
"""

import datetime
import re
import bisect
import degreedays._private as private
import degreedays.time
import degreedays.geo
from degreedays._private import _Immutable, XmlElement
import degreedays.api as api
_isTypingOverloadImported = False
try:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        import degreedays.api.data.impl as impl
        from degreedays.api.regression import RegressionResponse
        from typing import TypeVar, overload
        _isTypingOverloadImported = True
        _RES = TypeVar('_RES', bound=api.Response)
        import sys
        if sys.version_info >= (3, 9):
            from collections.abc import Iterator, Iterable, Sequence, Mapping, \
                Collection
        else:
            from typing import Iterator, Iterable, Sequence, Mapping, Collection
except ImportError:
    pass
def _importDummyOverload():
    # We put this overload in a function cos, if it is in an except block or
    # use a bool check, for some reason VSCode imports it for type hinting,
    # overriding the import of typing.overload.
    from degreedays._private import overload
    global overload # Need this to make it accessible outside function
if not _isTypingOverloadImported:
    _importDummyOverload()

__all__ = ['Location', 'GeographicLocation',
    'Period',
    'Breakdown', 'DatedBreakdown', 'AverageBreakdown',
    'Calculation', 'TimeSeriesCalculation',
    'DataSpec', 'DatedDataSpec', 'AverageDataSpec', 
    'TimeSeriesDataSpec', 'DataSpecs',
    'LocationDataRequest', 'LocationInfoRequest', 'DataApi',
    'TemperatureUnit', 'Temperature',
    'TimeSeriesInterval',
    'LocationError', 'SourceDataError',
    'DataValue', 'DatedDataValue', 'TimeSeriesDataValue',
    'DataSet', 'DatedDataSet', 'AverageDataSet', 'TimeSeriesDataSet',
    'DataSets',
    'Station', 'Source',
    'LocationDataResponse', 'LocationInfoResponse']

_ABSTRACT_INIT_FACTORY = ('This is an abstract superclass.  To create an '
    'instance use the static factory methods, for example: ')
_ABSTRACT_INIT_RESPONSE = ('This is an abstract superclass.  Only the '
    'subclasses %s can be instantiated directly, though usually the API would '
    'create them automatically.')

_LOCATION_EXAMPLE = ("Location.stationId('KNYC'), "
    "Location.longLat(degreedays.geo.LongLat(-122.45361, 37.80544)), "
    "Location.postalCode('10036', 'US'), "
    "Location.postalCode('WC2N 5DN', 'GB')")
class Location(_Immutable):
    #1 inheritance-diagram:: Location
    #   degreedays.api.data.impl.StationIdLocation
    #   degreedays.api.data.impl.LongLatLocation
    #   degreedays.api.data.impl.PostalCodeLocation
    """Defines a location for which degree days should be calculated.

    **To create a** ``Location`` **object** you can use the static factory
    methods of this class. For example::

        losAngelesAirportWeatherStation = Location.stationId("KLAX")

        empireStateBuilding = Location.postalCode("10118", "US")

        trafalgarSquare = Location.longLat(LongLat(-0.12795, 51.50766))

    `empireStateBuilding` and `trafalgarSquare` are examples of geographic
    locations, which provide a powerful way to get data for locations around the
    world. See :py:class:`GeographicLocation` for more on how these geographic
    locations work."""
    __slots__ = ()
    def __init__(self):
        raise TypeError(_ABSTRACT_INIT_FACTORY + _LOCATION_EXAMPLE + '.')
    @staticmethod
    def stationId(stationId): # type: (str) -> impl.StationIdLocation
        """Returns a ``StationIdLocation`` object with the specified weather
        station ID.

        :param str stationId: the ID of the weather station that the
            ``StationIdLocation`` should represent (i.e. the station you want
            data for). Cannot be empty, cannot contain contain any characters
            other than ``[-_0-9a-zA-Z]``, and cannot contain more than 60
            characters (a limit that is significantly larger than the length of
            any station ID that we are currently aware of, but that is set high
            to allow for "virtual station IDs" to be introduced in the future,
            combining data from multiple stations).
        :raises TypeError: if `stationId` is not a ``str``.
        :raises ValueError: if tests indicate that `stationId` fails to match
            the specification detailed above."""
        # Having to import impl for static factory methods like this is ugly...
        # But we can't do it at the top because then that's a circular import
        # (as impl depends on this module).
        # This seems to be the only way to avoid cluttering this module up
        # conceptually for the user by forcing them to see way more classes
        # than they'll need.
        # Apparently at least this isn't a performance hit:
        # http://stackoverflow.com/questions/477096/python-import-coding-style
        # "Because of the way python caches modules, there isn't a performance
        # hit. In fact, since the module is in the local namespace, there is a
        # slight performance benefit to importing modules in a function."
        import degreedays.api.data.impl as impl
        return impl.StationIdLocation(stationId)
    @staticmethod
    def longLat(longLat):
        # type: (degreedays.geo.LongLat) -> impl.LongLatLocation
        """Returns a ``LongLatLocation`` object with the specified longitude and
        latitude position.

        :param LongLat longLat: the longitude/latitude position.
        :raises TypeError: if `longLat` is not a
            :py:class:`degreedays.geo.LongLat` object.

        See also: :py:class:`GeographicLocation`"""
        import degreedays.api.data.impl as impl
        return impl.LongLatLocation(longLat)
    @staticmethod
    def postalCode(postalCode, countryCode):
        # type: (str, str) -> impl.PostalCodeLocation
        """Returns a ``PostalCodeLocation`` object with a postal code (or zip
        code, post code, or postcode) and a two-letter country code representing
        the country that the postal code belongs to.

        :param str postalCode: the postal code (or zip code, post code, or
            postcode) of the location you want data for. Cannot be empty, cannot
            be longer than 16 characters (a length that we believe allows for
            all current postal codes worldwide), and cannot contain any
            characters other than ``[- 0-9a-zA-Z]``.
        :param str twoLetterIsoCountryCodeInUpperCase: the `ISO 3166-1-alpha-2
            country code <http://www.iso.org/iso/country_codes/
            iso_3166_code_lists/country_names_and_code_elements.htm>`__ of the
            country that `postalCode` belongs to. It must be a two-character
            string comprised of only characters A-Z (i.e. upper case only). For
            example, pass "US" if `postalCode` is a US zip code, pass "GB" (for
            "Great Britain") if `postalCode` is a UK post code, and pass "CA" if
            `postalCode` is a Canadian zip code.
        :raises TypeError: if `postalCode` or
            `twoLetterIsoCountryCodeInUpperCase` is not a ``str``.
        :raises ValueError: if tests indicate that `postalCode` or
            `twoLetterIsoCountryCodeInUpperCase` fails to match the
            specifications detailed above.

        See also: :py:class:`GeographicLocation`"""
        import degreedays.api.data.impl as impl
        return impl.PostalCodeLocation(postalCode, countryCode)
    def _toXml(self): # type: () -> XmlElement
        raise NotImplementedError
    @staticmethod
    def _check(param, paramName='location'):
        # type: (Location, str) -> Location
        if not isinstance(param, Location):
            raise TypeError(private.wrongSupertypeString(param, paramName,
                Location, _LOCATION_EXAMPLE))
        return param

_GEOGRAPHIC_LOCATION_EXAMPLE = (
    "Location.longLat(degreedays.geo.LongLat(-122.45361, 37.80544)), "
    "Location.postalCode('10036', 'US'), "
    "Location.postalCode('WC2N 5DN', 'GB').")   
class GeographicLocation(Location):
    #1 inheritance-diagram:: GeographicLocation
    #   degreedays.api.data.impl.LongLatLocation
    #   degreedays.api.data.impl.PostalCodeLocation
    """Defines a location in terms of a longitude/latitude or postal/zip code,
    leaving it to the API to find the nearest good weather station.

    **To create a** ``GeographicLocation`` **object** you can use the
    :py:meth:`Location.postalCode` and :py:meth:`Location.longLat` factory
    methods.  For example::

        empireStateBuilding = Location.postalCode("10118", "US")
        
        trafalgarSquare = Location.longLat(LongLat(-0.12795, 51.50766))

    Geographic locations provide a powerful way to request degree-day data.
    Manually selecting the best weather station to provide data for a specific
    building or region can be tricky, because different stations have different
    levels of data coverage and quality. With a geographic location, the API
    will automatically select the weather station that is best equipped to
    provide the data you want.

    At some point the API might average data from multiple weather stations
    around the specified location if it thinks that would significantly improve
    results. If we do add this feature, it will be optional, and disabled by
    default, so the behaviour of your system won't change unless you want it to.

    **Make sure to specify the full range of data that you want when using a
    geographic location**... Some weather stations have less data than others so
    it's important for the API to know the full range of interest when it's
    choosing which station(s) to use.

    Fetching more data for the same location (e.g. daily updates)
    --------------------------------------------------------------
    The :py:class:`LocationDataResponse` contains a station ID that will enable
    you to fetch more data for the weather station(s) that were selected for
    your geographic location. If just one station was used (the normal case),
    then the station ID will simply be the canonical ID of that one station. If
    data from multiple stations was combined to satisfy your request (an option
    that isn't available now but that we may cater for in future), then the
    station ID will be for a "virtual station" that represents the specific
    combination of weather stations used.

    Either way, you can use the station ID from the
    :py:class:`LocationDataResponse` to fetch more data for the same location in
    the future. For example, you might initially want to fetch the last 5 years
    of data for a geographic location, and then use the returned station ID to
    fetch updates each day, week, or month going forward. If you're storing the
    generated data, then doing it this way will ensure that your data updates
    are generated using the same weather station(s) as your initial request.

    However, if you're following this model, bear in mind that a weather station
    that works today won't necessarily be working next month or next year.  It's
    unusual for stations to go out of service, but it does happen.  It might not
    be worth worrying about the possibility of stations going down if you're
    only tracking data for a handful of locations, but it's definitely worth
    planning for if you're tracking data for hundreds or thousands of locations.
    To prepare for a station going down, it makes sense to store the details of
    the geographic location together with the station ID that you're using for
    updates. That way, if the station fails, you can use the geographic location
    to find a replacement.

    Note that a simple alternative is to use the geographic location to fetch a
    full set of data each time it is needed. You might not get data from the
    same station(s) each time (particularly if you vary the :py:class:`Period`
    that you request data for), but the station-selection algorithm will ensure
    that you're getting the best available data for each individual request that
    you make.

    .. _two-stage-fetching:

    Two-stage data fetching for geographic locations
    -------------------------------------------------
    If you are using geographic locations, but storing data by station ID (as
    described above), you may be able to save request units and improve the
    efficiency of your system with two-stage data fetching. When you want to add
    a new location into your system (e.g. if a new user signs up with a new
    address), you can do the following:

    **Stage 1**: Call :py:meth:`DataApi.getLocationInfo` with a
    :py:class:`LocationInfoRequest` containing the geographic location and the
    specification of the data that you want. You won't get any data back, but
    you should get the station ID that the system would use for an equivalent
    :py:class:`LocationDataRequest`. If you already have data stored for that
    station ID, use it; if not, progress to stage 2.

    **Stage 2**: Call :py:meth:`DataApi.getLocationData` with a
    :py:class:`LocationDataRequest` that specifies the station ID from stage 1.
    (You could use the geographic location again, but using the station ID will
    save a request unit, such that your two-stage fetch will take the same
    number of request units in total as it would if you had just submitted a
    :py:class:`LocationDataRequest` with the geographic location in the first
    place.)

    Two-stage fetching will only improve efficiency and save request units
    if/when you have enough geographic locations in your system that some of
    them end up sharing weather stations. But, if that is the case, two-stage
    fetching can really help your system to scale well as more and more
    geographic locations are added in."""
    __slots__ = ()
    def __init__(self):
        raise TypeError(_ABSTRACT_INIT_FACTORY +
            _GEOGRAPHIC_LOCATION_EXAMPLE + '.')

_PERIOD_EXAMPLE = ("Period.latestValues('5'), "
    "Period.dayRange(degreedays.time.DayRange("
        "datetime.date(2012, 1, 1), "
        "datetime.date(2012, 10, 31)))")  
class Period(_Immutable):
    #1 inheritance-diagram:: Period
    #   degreedays.api.data.impl.LatestValuesPeriod
    #   degreedays.api.data.impl.DayRangePeriod
    """Defines the period in time that a set of degree days should cover.

    **To create a** ``Period`` **object** you can use the static factory methods
    of this class.  For example::

        latest7Values = Period.latestValues(7)
        yearOf2024 = Period.dayRange(degreedays.time.DayRange(
                datetime.date(2024, 1, 1), datetime.date(2024, 12, 31)))
    """
    __slots__ = ()
    def __init__(self):
        raise TypeError(_ABSTRACT_INIT_FACTORY + _PERIOD_EXAMPLE + '.')
    @staticmethod
    def latestValues(numberOfValues, minimumNumberOfValuesOrNone=None):
        # type: (int, int | None) -> impl.LatestValuesPeriod
        """Returns a ``LatestValuesPeriod`` object that automatically resolves
        to a date range including the latest available data and the specified
        number of degree-day values.

        :param int numberOfValues: a number, greater than zero, that specifies
            how many degree-day values the period should cover (see
            :py:class:`degreedays.api.data.impl.LatestValuesPeriod` for an
            explanation of how the values in question can be daily, weekly,
            monthly, or yearly). This is effectively an upper bound: if there
            isn't enough good data to cover the `numberOfValues` specified, the
            API will assemble and return what it can.
        :param int | None minimumNumberOfValuesOrNone: you can specify this if
            you would rather have a failure than a partial set of data with less
            than your specified minimum number of values.  Otherwise you may get
            back less data than you asked for if there aren't enough
            weather-data records to generate a full set for your specified
            location.
        :raises TypeError: if `numberOfValues` is not an `int`, or if
            `minimumNumberOfValuesOrNone` is not an `int` or `None`.
        :raises ValueError: if `numberOfValues` is less than 1, or if
            `minimumNumberOfValuesOrNone` is an `int` that is less than 1 or
            greater than `numberOfValues`."""
        import degreedays.api.data.impl as impl
        return impl.LatestValuesPeriod(
            numberOfValues, minimumNumberOfValuesOrNone)
    @staticmethod
    def dayRange(dayRange, # type: degreedays.time.DayRange
            minimumDayRangeOrNone=None # type: degreedays.time.DayRange | None
            ): # type: (...) -> impl.DayRangePeriod
        """Returns a ``DayRangePeriod`` object that specifies the period covered
        by `dayRange`.

        :param degreedays.time.DayRange dayRange: the range of days that the
            period should cover.
        :param degreedays.time.DayRange | None minimiumDayRangeOrNone: you can
            specify this if you would rather have a failure than a partial set
            of data covering less than your specified minimum range.  Otherwise
            you may get back less data than you asked for if there aren't enough
            weather-data records to generate a full set for your specified
            location. See
            :py:attr:`degreedays.api.data.impl.DayRangePeriod.minimumDayRangeOrNone`
            for more on this.
        :raises TypeError: if `dayRange` is not a
            :py:class:`degreedays.time.DayRange`, or if `minimumDayRangeOrNone`
            is not a :py:class:`degreedays.time.DayRange` or `None`.
        :raises ValueError: if `minimumDayRangeOrNone` is a
            :py:class:`degreedays.time.DayRange` that extends earlier or later
            than `dayRange`."""
        import degreedays.api.data.impl as impl
        return impl.DayRangePeriod(dayRange, minimumDayRangeOrNone)
    def _toXml(self): # type: () -> XmlElement
        raise NotImplementedError
    @staticmethod
    def _check(param, paramName='period'): # type: (Period, str) -> Period
        if not isinstance(param, Period):
            raise TypeError(private.wrongSupertypeString(param, paramName,
                Period, _PERIOD_EXAMPLE))
        return param

_BREAKDOWN_EXAMPLE = ('DatedBreakdown.daily(Period.latestValues(30)), '
    'DatedBreakdown.monthly(Period.latestValues(12)), '
    'AverageBreakdown.fullYears(Period.latestValues(5))')   
class Breakdown(_Immutable):
    #1 inheritance-diagram:: Breakdown DatedBreakdown AverageBreakdown
    #   degreedays.api.data.impl.DailyBreakdown
    #   degreedays.api.data.impl.WeeklyBreakdown
    #   degreedays.api.data.impl.MonthlyBreakdown
    #   degreedays.api.data.impl.YearlyBreakdown
    #   degreedays.api.data.impl.CustomBreakdown
    #   degreedays.api.data.impl.FullYearsAverageBreakdown
    """Defines how a set of degree days should be broken down (e.g. daily,
    weekly, or monthly), and the period in time they should cover.

    **To create a** ``Breakdown`` **object**, use the static factory methods on
    the :py:class:`DatedBreakdown` and :py:class:`AverageBreakdown` subclasses.
    """
    __slots__ = ()
    def __init__(self):
        raise TypeError(_ABSTRACT_INIT_FACTORY + _BREAKDOWN_EXAMPLE + '.')
    def _toXml(self): # type: () -> XmlElement
        raise NotImplementedError

_DATED_BREAKDOWN_EXAMPLE = ('DatedBreakdown.daily(Period.latestValues(30)), '
    'DatedBreakdown.monthly(Period.latestValues(12)), '
    'DatedBreakdown.yearly(Period.latestValues(5))')
class DatedBreakdown(Breakdown):
    #1 inheritance-diagram:: DatedBreakdown
    #   degreedays.api.data.impl.DailyBreakdown
    #   degreedays.api.data.impl.WeeklyBreakdown
    #   degreedays.api.data.impl.MonthlyBreakdown
    #   degreedays.api.data.impl.YearlyBreakdown
    #   degreedays.api.data.impl.CustomBreakdown
    """Defines how a set of dated degree days (in a :py:class:`DatedDataSet`)
    should be broken down, including the period in time they should cover.

    This is the abstract superclass of the types of :py:class:`Breakdown` that
    can be taken by a :py:class:`DatedDataSpec`.

    **To create a** ``DatedBreakdown`` **object** you can use the static factory
    methods of this class. For example::

        dailyBreakdownOverLast30Days = DatedBreakdown.daily(
                Period.latestValues(30))

        weeklyBreakdownFor2024WithWeeksStartingOnMonday = DatedBreakdown.weekly(
                Period.dayRange(degreedays.time.DayRange(
                    datetime.date(2024, 1, 1),
                    datetime.date(2024, 12, 31))),
                DayOfWeek.MONDAY)

        monthlyBreakdownOverLast12Months = DatedBreakdown.monthly(
                Period.latestValues(12))

        yearlyBreakdownOverLast5Years = DatedBreakdown.yearly(
                Period.latestValues(5))

    As you can see from the above examples, defining the :py:class:`Period` is
    an important part of defining a ``DatedBreakdown``. See that class for more
    information on the relevant options."""
    __slots__ = ()
    def __init__(self):
        raise TypeError(_ABSTRACT_INIT_FACTORY + _DATED_BREAKDOWN_EXAMPLE + '.')
    @property
    def allowPartialLatest(self): # type: () -> bool
        """`True` if the latest day range can be partially filled (i.e.
        incomplete); `False` otherwise (the default case).

        When specifying time-series data (like hourly temperature data) via a
        :py:class:`TimeSeriesDataSpec <degreedays.api.data.TimeSeriesDataSpec>`,
        you can specify a breakdown with this `allowPartialLatest` property set
        to `True`, to tell the API to include values for the current day so far.
        For example::

            hourlyTempsIncludingToday = DataSpec.timeSeries(
                TimeSeriesCalculation.hourlyTemperature(TemperatureUnit.CELSIUS),
                DatedBreakdown.daily(Period.latestValues(31), allowPartialLatest=True))

        If you requested the above-specified hourly temperature data at, say,
        11:42 on any given day, you could expect it to include values for 00:00,
        01:00, 02:00 through to 11:00 on that day (bearing in mind that some
        stations are slower to report than others so you won't always get the
        absolute latest figures).

        Please note that the most recent time-series data can be a little
        volatile, as weather stations sometimes send multiple reports for the
        same time, some delayed, and some marked as corrections for reports they
        sent earlier. Our system generates time-series data using all the
        relevant reports that each weather station has sent, but the generated
        figures may change if delayed or corrected reports come through later.
        If you are storing partial-latest time-series data we suggest you
        overwrite it later with figures generated after the day has completed
        and any delayed/corrected reports have had time to filter through.

        This `allowPartialLatest` property exists mainly for time-series data,
        but you can also set it to `True` on a breakdown for degree days, to
        specify that the data can include a value for the latest partial
        week/month/year. For example::

            monthlyHddIncludingPartialLatest = DataSpec.dated(
                Calculation.heatingDegreeDays(Temperature.fahrenheit(65)),
                DatedBreakdown.monthly(Period.latestValues(12), allowPartialLatest=True))

        If you requested the above-specified monthly degree-day data on, say,
        June 22nd, you could expect the last of the 12 values returned to cover
        from the start of June 1st through to the end of June 21st (assuming a
        good weather station with frequent reporting and minimal delays). If you
        left `allowPartialLatest` with its default value of `False`, the last of
        the 12 values returned would be for the full month of May (i.e. from the
        start of May 1st to the end of May 31st), as the monthly figure for June
        wouldn't become available until June ended.

        Unlike for time-series data (specified with
        :py:class:`TimeSeriesDataSpec
        <degreedays.api.data.TimeSeriesDataSpec>`), this property will never
        cause degree days to be calculated for partial days. So for degree days
        this property will only make a difference on
        :py:meth:`weekly <degreedays.api.data.DatedBreakdown.weekly>`,
        :py:meth:`monthly <degreedays.api.data.DatedBreakdown.monthly>`,
        :py:meth:`yearly <degreedays.api.data.DatedBreakdown.yearly>`, and
        :py:meth:`custom <degreedays.api.data.DatedBreakdown.custom>` breakdowns
        with day ranges covering multiple days.

        Any partial-latest day range will always start on the usual day (i.e. it
        will never be cut short at the start), it's only the end that can be cut
        short. This is true for both degree days and time-series data."""
        raise NotImplementedError()
    def _checkAllowPartialLatest(self, allowPartialLatest):
        # type: (bool) -> bool
        return private.checkBoolean(allowPartialLatest, 'allowPartialLatest')
    def _reprStart(self): # type: () -> str
        raise TypeError('Subclass must override this')
    def __repr__(self):
        if self.allowPartialLatest:
            return self._reprStart() + ', allowPartialLatest=True)'
        else:
            return self._reprStart() + ')'
    def _addAllowPartialLatestXml(self, xmlElement):
        # type: (XmlElement) -> XmlElement
        if self.allowPartialLatest:
            xmlElement.addAttribute('allowPartialLatest', 'true')
        return xmlElement
    @staticmethod
    def daily(period, allowPartialLatest=False):
        # type: (Period, bool) -> impl.DailyBreakdown
        """Returns a ``DailyBreakdown`` object that specifies daily degree days
        covering the specified period in time.

        :param Period period: the period in time that the daily breakdown should
            cover.
        :param bool allowPartialLatest: `True` to specify that the latest day
            of data can be partially filled (i.e. incomplete), or `False` if the
            latest day must be complete (the default behaviour).  Setting this
            to `True` is mainly useful if you are fetching time-series data (via
            :py:class:`TimeSeriesDataSpec`) and you want it to include values
            for the current (incomplete) day.  See :py:attr:`allowPartialLatest`
            for more on this.
        :raises TypeError: if `period` is not a :py:class:`Period` object, or
            `allowPartialLatest` is not a `bool`."""
        import degreedays.api.data.impl as impl
        return impl.DailyBreakdown(period, allowPartialLatest)
    @staticmethod
    def weekly(period, firstDayOfWeek, allowPartialLatest=False):
        # type: (Period, degreedays.time.DayOfWeek, bool) -> impl.WeeklyBreakdown
        """Returns a ``WeeklyBreakdown`` object that specifies weekly degree
        days covering the specified period in time.

        To avoid the potential for confusion, you must explicitly specify the
        day of the week that you want each "week" to start on. For example, if a
        "week" should run from Monday to Sunday (inclusive), specify the
        `firstDayOfWeek` parameter as ``degreedays.time.DayOfWeek.MONDAY``.

        :param Period period: the period in time that the weekly breakdown should
            cover.
        :param DayOfWeek firstDayOfWeek: indicates which day should be taken as
            the first of each week.
        :param bool allowPartialLatest: `True` to specify that the latest week
            of data can be partially filled (i.e. incomplete), or `False` if the
            latest week must be complete (the default behaviour).  Setting this
            to `True` is mainly useful if you are fetching time-series data (via
            :py:class:`TimeSeriesDataSpec`) and you want it to include the
            current (incomplete) week, including values for the current
            (incomplete) day.  See :py:attr:`allowPartialLatest` for more on
            this.
        :raises TypeError: if `period` is not a :py:class:`Period` object, or if
            `firstDayOfWeek` is not a :py:class:`degreedays.time.DayOfWeek`
            object, or if `allowPartialLatest` is not a `bool`."""
        import degreedays.api.data.impl as impl
        return impl.WeeklyBreakdown(period, firstDayOfWeek, allowPartialLatest)
    @staticmethod
    def monthly(period, startOfMonth=degreedays.time.StartOfMonth(1),
            allowPartialLatest=False):
        # type: (Period, degreedays.time.StartOfMonth, bool) -> impl.MonthlyBreakdown
        """Returns a ``MonthlyBreakdown`` object that specifies monthly degree
        days covering the specified `period` in time, with each "month" starting
        on the specified day of the month.

        :param Period period: the period in time that the monthly breakdown
            should cover.
        :param StartOfMonth startOfMonth: specifying which day (between 1 and 28
            inclusive) should be taken as the first of each "month".
            ``StartOfMonth(1)`` is the default value and specifies regular
            calendar months.
        :param bool allowPartialLatest: `True` to specify that the latest month
            of data can be partially filled (i.e. incomplete), or `False` if the
            latest month must be complete (the default behaviour).  Setting this
            to `True` is mainly useful if you are fetching time-series data (via
            :py:class:`TimeSeriesDataSpec`) and you want it to include the
            current (incomplete) month, including values for the current
            (incomplete) day.  See :py:attr:`allowPartialLatest` for more on
            this.
        :raises TypeError: if `period` is not a :py:class:`Period` object, or if
            `startOfMonth` is not a :py:class:`degreedays.time.StartOfMonth`
            object, or if `allowPartialLatest` is not a `bool`."""
        import degreedays.api.data.impl as impl
        return impl.MonthlyBreakdown(period, startOfMonth, allowPartialLatest)
    @staticmethod
    def yearly(period, startOfYear=degreedays.time.StartOfYear(1, 1),
            allowPartialLatest=False):
        # type: (Period, degreedays.time.StartOfYear, bool) -> impl.YearlyBreakdown
        """Returns a ``YearlyBreakdown`` object that specifies yearly degree
        days covering the specified `period` in time, with each "year" starting
        on the specified day of the year.

        :param Period period: the period in time that the yearly breakdown
            should cover.
        :param StartOfYear startOfYear: specifying which day of the year (month
            and day of the month) should be taken as the first of each "year".
            ``StartOfYear(1, 1)`` is the default value and specifies regular
            calendar years.
        :param bool allowPartialLatest: `True` to specify that the latest year
            of data can be partially filled (i.e. incomplete), or `False` if the
            latest year must be complete (the default behaviour).  Setting this
            to `True` is mainly useful if you are fetching time-series data (via
            :py:class:`TimeSeriesDataSpec`) and you want it to include the
            current (incomplete) year, including values for the current
            (incomplete) day.  See :py:attr:`allowPartialLatest` for more on
            this.
        :raises TypeError: if `period` is not a :py:class:`Period` object, or if
            `startOfYear` is not a :py:class:`degreedays.time.StartOfYear`
            object, or if `allowPartialLatest` is not a `bool`."""
        import degreedays.api.data.impl as impl
        return impl.YearlyBreakdown(period, startOfYear, allowPartialLatest)
    @staticmethod
    def custom(dayRanges, allowPartialLatest=False):
        # type: (degreedays.time.DayRanges, bool) -> impl.CustomBreakdown
        """Returns a ``CustomBreakdown`` object that specifies degree days
        broken down to match the :py:class:`degreedays.time.DayRanges` passed
        in.

        :param DayRanges dayRanges: specifying the dates that each degree-day
            figure should cover (typically matching the dates of your
            energy-usage records).
        :param bool allowPartialLatest: `True` to specify that the latest
            specified day range can be partially filled (i.e. incomplete), or
            `False` if it must be complete (the default behaviour).  Setting
            this to `True` is mainly useful if you are fetching time-series data
            (via :py:class:`TimeSeriesDataSpec`) and you want it to include
            values for the current (incomplete) day.  See
            :py:attr:`allowPartialLatest` for more on this.
        :raises TypeError: if `dayRanges` is not a
            :py:class:`degreedays.time.DayRanges` object, or if
            `allowPartialLatest` is not a `bool`."""
        import degreedays.api.data.impl as impl
        return impl.CustomBreakdown(dayRanges, allowPartialLatest)
    @staticmethod
    def _check(param, paramName='datedBreakdown'):
        # type: (DatedBreakdown, str) -> DatedBreakdown
        if not isinstance(param, DatedBreakdown):
            raise TypeError(private.wrongSupertypeString(param, paramName,
                DatedBreakdown, _DATED_BREAKDOWN_EXAMPLE))
        return param

_AVERAGE_BREAKDOWN_EXAMPLE = (
    'AverageBreakdown.fullYears(Period.latestValues(5)) for a ' +
    '5-year average covering the 5 most recent full calendar years') 
class AverageBreakdown(Breakdown):
    #1 inheritance-diagram:: AverageBreakdown
    #   degreedays.api.data.impl.FullYearsAverageBreakdown
    """Defines how a set of average degree days should be broken down, including
    the period in time they should cover.

    This is the abstract superclass of the types of :py:class:`Breakdown` that
    can be taken by an :py:class:`AverageDataSpec`.

    **To create an** ``AverageBreakdown`` **object** use the
    :py:meth:`fullYears` static factory method.  For example:: 

        fiveYearAverage = AverageBreakdown.fullYears(Period.latestValues(5))

    :py:class:`AverageDataSpec` has more on how to actually fetch average
    degree-day data with your specified ``AverageBreakdown``."""
    __slots__ = ()
    def __init__(self):
        raise TypeError(_ABSTRACT_INIT_FACTORY +
            _AVERAGE_BREAKDOWN_EXAMPLE, '.')
    @staticmethod
    def fullYears(period):
        # type: (Period) -> impl.FullYearsAverageBreakdown
        """Returns a ``FullYearsAverageBreakdown`` object that specifies average
        degree days derived from data covering full calendar years determined by
        the specified `period`.

        :param Period period: specifies the full calendar years of data that the
            average figures should be derived from. Typically you'd want to use
            :py:meth:`Period.latestValues` for this, specifying at least 2
            values (since an average of 1 year of data is not very meaningful).
            But you can also use :py:meth:`Period.dayRange` - in this case the
            period may be :ref:`widened <widening>` for calculation purposes to
            make it cover full calendar years.
        :raises TypeError: if `period` is not a :py:class:`Period` object."""
        import degreedays.api.data.impl as impl
        return impl.FullYearsAverageBreakdown(period)
    @staticmethod
    def _check(param, paramName='averageBreakdown'):
        # type: (AverageBreakdown, str) -> AverageBreakdown
        if not isinstance(param, AverageBreakdown):
            raise TypeError(private.wrongSupertypeString(param, paramName,
                AverageBreakdown, _AVERAGE_BREAKDOWN_EXAMPLE))
        return param

# TemperatureUnit follows the pattern shown by one of the answers at:
# http://stackoverflow.com/questions/36932/
# Though we define CELSIUS and FAHRENHEIT inside the class (initially as None,
# then set after the definition), so as to make them appear in PyDev
# intellisense.
# The metaclass stuff is to enable people to iterate over the units like:
# "for u in TemperatureUnit".  It's complicated to make it compatible with
# Python 2 and 3.  Our approach is based on that described at:
# http://mikewatkins.ca/2008/11/29/python-2-and-3-metaclasses/
# We have to pass a dict into TemperatureUnitMetaclass, which would imply
# mutability, but following the guidance at
# http://stackoverflow.com/questions/9654133/
# we pass a dictionary containing empty __slots__ in, which works great at
# ensuring immutability.
class _TemperatureUnitMetaclass(type):
    _SHORT_CHARS = ('C', 'F')
    def __iter__(cls): # type: () -> Iterator[TemperatureUnit]
        for shortChar in cls._SHORT_CHARS:
            yield TemperatureUnit._get(shortChar)
    # Following are effectively class properties - these are what get used by
    # references to e.g. TemperatureUnit.CELSIUS.  Idea came from here
    # https://stackoverflow.com/a/38810649  This is supposedly "the preferred
    # approach" https://github.com/pylint-dev/pylint/issues/378
    # We move these properties to get them showing in Sphinx documentation - see
    # preprocess.py for notes.
    #EnumCopyStart(TemperatureUnit)
    @property
    def CELSIUS(cls): # type: () -> TemperatureUnit
        """For the Celsius temperature scale.

        Access via: ``TemperatureUnit.CELSIUS``"""
        return TemperatureUnit._get('C')
    @property
    def FAHRENHEIT(cls): # type: () -> TemperatureUnit
        """For the Fahrenheit temperature scale.

        Access via: ``TemperatureUnit.FAHRENHEIT``"""
        return TemperatureUnit._get('F')
    #EnumCopyEnd
_TemperatureUnitSuper = _TemperatureUnitMetaclass('_TemperatureUnitSuper',
    (_Immutable,), {'__slots__': ()})
class TemperatureUnit(_TemperatureUnitSuper):
    """Defines the units of temperature measurement with class constants
    :py:attr:`TemperatureUnit.CELSIUS` and
    :py:attr:`TemperatureUnit.FAHRENHEIT`."""
    __slots__ = ('_shortChar', '_name', '__nameUpper',
        '_minTimesTen', '_maxTimesTen')
    # cache of values to avoid recreation.
    __map = {} # type: dict[str, TemperatureUnit]
    #EnumPaste(TemperatureUnit)
    def __new__(cls):
        raise TypeError('This is not built for direct '
                'instantiation.  Please use either TemperatureUnit.CELSIUS or '
                'TemperatureUnit.FAHRENHEIT.')
    def __initImpl(self, shortChar, name, minTimesTen, maxTimesTen):
        # type: (TemperatureUnit, str, str, int, int) -> None
        self._shortChar = shortChar
        self._name = name
        self._minTimesTen = minTimesTen
        self._maxTimesTen = maxTimesTen
        self.__nameUpper = name.upper()
    @classmethod
    def _create(cls, shortChar): # type: (str) -> TemperatureUnit
        newItem = super(TemperatureUnit, cls).__new__(cls)
        if shortChar == 'C':
            newItem.__initImpl('C', 'Celsius', -2730, 30000)
        elif shortChar == 'F':
            newItem.__initImpl('F', 'Fahrenheit', -4594, 54320)
        else:
            raise ValueError
        cls.__map[newItem._shortChar] = newItem
        return newItem
    @classmethod
    def _get(cls, shortCode): # type: (str) -> TemperatureUnit
        return cls.__map[shortCode]
    # We need this for pylint to find the class properties on the metaclass.
    # https://stackoverflow.com/a/60731663
    def __getattr__(self, name): # type: (str) -> str
        return getattr(_TemperatureUnitMetaclass, name)
    def _equalityFields(self): # type: () -> str
        return self._shortChar
    def range(self, firstValue, lastValue, step):
        # type: (float, float, float) -> Sequence[Temperature]
        """Returns a low-to-high sorted :py:class:`Sequence` of
        :py:class:`Temperature` objects, with values running from `firstValue`
        to `lastValue` (inclusive), and the specified `step` between each
        consecutive temperature.

        For example, to get Celsius temperatures between 10°C and 30°C
        (inclusive), with each temperature being 5°C greater than the last
        (giving temperatures 10°C, 15°C, 20°C, 25°C, and 30°C)::

            temps = TemperatureUnit.CELSIUS.range(10, 30, 5)

        :param float firstValue: the value of the first :py:class:`Temperature`
            to be included in the returned :py:class:`Sequence`. If this
            ``range`` method is called on :py:attr:`TemperatureUnit.CELSIUS`,
            `firstValue` must be greater than or equal to -273°C and less than
            or equal to 3000°C; if it is called on
            :py:attr:`TemperatureUnit.FAHRENHEIT` then `firstValue` must be
            greater than or equal to -459.4°F and less than or equal to 5432°F.
        :param float lastValue: the value of the last :py:class:`Temperature`
            to be included in the returned :py:class:`Sequence`. This must be
            greater than or equal to `firstValue`. Also, like for `firstValue`,
            if this ``range`` method is called on
            :py:attr:`TemperatureUnit.CELSIUS`, `lastValue` must be greater than
            or equal to -273°C and less than or equal to 3000°C; if it is called
            on :py:class:`TemperatureUnit.FAHRENHEIT` then `lastValue` must be
            greater than or equal to -459.4°F and less than or equal to 5432°F.
        :param float step: the temperature difference between each temperature
            value to be included in the returned :py:class:`Sequence`. Cannot be
            `NaN`, and must be greater than zero. It must also be a multiple of
            0.1 (the smallest temperature difference allowed), though allowances
            are made for floating-point imprecision (so for example a `step` of
            0.4999999 will be treated as 0.5).
        :raises TypeError: if `firstValue`, `lastValue`, or `step` is not a
            `float`.
        :raises ValueError: if any of the parameters are `NaN`; if `firstValue`
            or `lastValue` are outside of their allowed range (that's -273°C
            to 3000°C inclusive if this ``range`` method is called on
            :py:attr:`TemperatureUnit.CELSIUS`, and -459.4°F to 5432°F inclusive
            if it is called on :py:attr:`TemperatureUnit.FAHRENHEIT`); if
            `lastValue` is less than `firstValue`; if `step` is not positive; or
            if `step` is not a multiple of 0.1 (allowing for slight deviations
            caused by floating-point imprecision).

        See also: :py:meth:`Temperature.celsiusRange`,
        :py:meth:`Temperature.fahrenheitRange`"""
        return Temperature._range(self, firstValue, lastValue, step)
    def _checkRange(self, value, valueTimesTen, paramName):
        # type: (float, int, str) -> None
        if (valueTimesTen < self._minTimesTen or
                valueTimesTen > self._maxTimesTen):
            raise ValueError('%s is an invalid %s temperature %s - cannot be '
                'less than %s or greater than %s' %
                (paramName, self._name, _formatTemperature(value),
                    _formatTemperatureTimesTen(self._minTimesTen),
                    _formatTemperatureTimesTen(self._maxTimesTen)))
    def _getTimesTenValue(self, value, paramName):
        # type: (float, str) -> int
        private.checkNumeric(value, paramName)
        # This should always work, even with huge numbers.
        timesTen = int(round(value * 10))
        self._checkRange(value, timesTen, paramName)
        return timesTen
    def __str__(self): # type: () -> str
        return self._name
    def __repr__(self):
        return 'TemperatureUnit.' + self.__nameUpper
    def _toXml(self):
        return XmlElement('TemperatureUnit').setValue(self._name)
    @staticmethod
    def _check(param, paramName='temperatureUnit'):
        # type: (TemperatureUnit, str) -> TemperatureUnit
        if type(param) is not TemperatureUnit:
            raise TypeError(private.wrongTypeString(param, paramName,
                TemperatureUnit,
                'TemperatureUnit.CELSIUS or TemperatureUnit.FAHRENHEIT'))
        return param
for _shortChar in TemperatureUnit._SHORT_CHARS: # create the instances
    TemperatureUnit._create(_shortChar)

# Sphinx fails with errors if we use TemperatureUnit.FAHRENHEIT here (cos of how
# we rewrite enum-like classes for Sphinx), so we use _get instead.
_MAX_TIMES_TEN_RANGE = (TemperatureUnit._get('F')._maxTimesTen -
    TemperatureUnit._get('F')._minTimesTen) # type: int
_OUT_OF_RANGE_POSITIVE_STEP_TIMES_TEN = _MAX_TIMES_TEN_RANGE + 1 # type: int
_JUST_OVER_MAX_RANGE = _OUT_OF_RANGE_POSITIVE_STEP_TIMES_TEN / 10.0 # type: float

def _formatTemperature(value): # type: (float) -> str
    s = '%.1f' % value
    # We did use rstrip('.0') but that didn't work with 0.0.
    if s.endswith('.0'):
        return s[:-2]
    return s

def _formatTemperatureTimesTen(timesTenValue): # type: (int) -> str
    # Must divide by 10.0 to avoid it doing whole integer division (in python
    # 2 anyway; 3 is different: http://www.python.org/dev/peps/pep-0238/)
    return _formatTemperature(timesTenValue / 10.0)

_TEMPERATURE_EXAMPLE = ('Temperature.celsius(15.5), '
    'Temperature.fahrenheit(65)')  
class Temperature(_Immutable):
    """Defines a temperature value, typically the base temperature of a
    degree-day calculation.

    **To create a** ``Temperature`` **object** you can use the static factory
    methods :py:meth:`celsius` and :py:meth:`fahrenheit`. For example::

        celsiusTemp = Temperature.celsius(15.5)
        fahrenheitTemp = Temperature.fahrenheit(65)

    You can pass a temperature into a :py:class:`Calculation` to define the base
    temperature that that ``Calculation`` should use to calculate degree days.
    Use a Celsius temperature for Celsius degree days, and a Fahrenheit
    temperature for Fahrenheit degree days.

    .. _rounding:

    Rounding
    --------
    This class enables temperatures to be defined to the nearest 0.1 degrees
    (either 0.1°C or 0.1°F). Given the limitations of temperature-recording
    equipment and methods, it is meaningless to consider temperature differences
    smaller than this.

    When creating a ``Temperature`` object, you can pass in any `float` value
    within the maximum and minimum limits set by the temperature unit. But **the
    value you pass in will always be rounded to the nearest 0.1 degrees**.

    For example, a Celsius ``Temperature`` created with a value of 15.5 will be
    equal to one created with 15.456 or 15.543. And a Fahrenheit ``Temperature``
    created with 65 will be equal to one created with 64.96 or 65.04.

    One benefit of this is that you can easily define a range of base
    temperatures in a loop without worrying too much about the inaccuracies of
    floating-point arithmetic. The automatic rounding should correct any such
    issues (e.g. rounding 69.9998 up to 70)."""
    __slots__ = ('__valueTimesTen', '__unit')
    def __init__(self, value, unit): # type: (float, TemperatureUnit) -> None
        value = private.checkNumeric(value, 'value')
        # round returns a float, but int(...) of that should work fine,
        # according to:
        # http://stackoverflow.com/questions/3387655/
        self.__valueTimesTen = int(round(value * 10))
        self.__unit = TemperatureUnit._check(unit, 'unit')
        self.__unit._checkRange(value, self.__valueTimesTen, 'value')
    def _equalityFields(self):
        return (self.__valueTimesTen, self.__unit)
    @staticmethod
    def celsius(value): # type: (float) -> Temperature
        """Returns a ``Temperature`` object with the specified Celsius
        temperature rounded to the nearest 0.1°C.

        :param float value: a Celsius temperature that's greater than or equal
            to -273°C (absolute zero) and less than or equal to 3000°C (hotter
            than the hottest blast furnaces). Note that the base-temperature
            range over which it would typically make sense to calculate degree
            days is *much* smaller than the range allowed by these limits.
        :param TypeError: if `value` is not a `float`.
        :param ValueError: if `value` is `NaN`, less than -273°C, or greater
            than 3000°C.

        See also: :ref:`Rounding <rounding>`, :py:meth:`fahrenheit`"""
        return Temperature(value, TemperatureUnit.CELSIUS)
    @staticmethod
    def fahrenheit(value): # type: (float) -> Temperature
        """Returns a ``Temperature`` object with the specified Fahrenheit
        temperature rounded to the nearest 0.1°F.

        :param float value: a Fahrenheit temperature that's greater than or
            equal to -459.4°F (absolute zero) and less than or equal to 5432°F
            (hotter than the hottest blast furnaces). Note that the
            base-temperature range over which it would typically make sense to
            calculate degree days is *much* smaller than the range allowed by
            these limits.
        :param TypeError: if `value` is not a `float`.
        :param ValueError: if `value` is `NaN`, less than -459.4°F, or greater
            than 5432°F.

        See also: :ref:`Rounding <rounding>`, :py:meth:`celsius`"""
        return Temperature(value, TemperatureUnit.FAHRENHEIT)
    @classmethod
    def _range(cls, unit, firstValue, lastValue, step):
        # type: (TemperatureUnit, float, float, float) -> tuple[Temperature, ...]
        firstTimesTen = unit._getTimesTenValue(firstValue, 'firstValue')
        lastTimesTen = unit._getTimesTenValue(lastValue, 'lastValue')
        if firstTimesTen > lastTimesTen:
            raise ValueError('firstValue (%g) cannot be greater than lastValue '
                '(%g) when rounded to the nearest 0.1.' %
                    (firstValue, lastValue))
        private.checkNumericAllowingInf(step, 'step')
        if not (step > 0):
            # This will cover -inf
            raise ValueError('Invalid step (%g) - it must be positive.' % step)
        elif step >_JUST_OVER_MAX_RANGE:
            # This will cover inf
            stepTimesTen = _OUT_OF_RANGE_POSITIVE_STEP_TIMES_TEN
        else:
            stepTimesTenFloat = step * 10
            stepTimesTen = int(round(stepTimesTenFloat))
            if (stepTimesTen == 0 or
                    abs(stepTimesTenFloat - stepTimesTen) > 0.01):
                raise ValueError("Invalid step (%g) - it must be a multiple of "
                    "0.1 (like 0.1, 0.2, 0.5, 1, 2, 5 etc.), or at least very "
                    "close to such a multiple (as we do a little rounding to "
                    "allow for inaccuracies in floating-point arithmetic).  "
                    "This is because Temperature objects allow only one figure "
                    "after the decimal point, as real-world weather-station "
                    "thermometers just aren't accurate enough to justify more."
                    % step)
        temps = [] # type: list[Temperature]
        def create(timesTen): # type: (int) -> Temperature
            t = Temperature.__new__(cls)
            t.__unit = unit
            t.__valueTimesTen = timesTen
            return t
        # For Python's range method: "For a positive step, the contents of a
        # range r are determined by the formula r[i] = start + step*i where
        # i >= 0 and r[i] < stop."  So it won't include lastTimesTen, unless
        # it's the same as firstTimesTen.
        for valueTimesTen in range(firstTimesTen, lastTimesTen, stepTimesTen):
            temps.append(create(valueTimesTen))
        temps.append(create(lastTimesTen))
        return tuple(temps)
    @staticmethod
    def celsiusRange(firstValue, lastValue, step):
        # type: (float, float, float) -> Sequence[Temperature]
        """Returns a low-to-high sorted :py:class:`Sequence` of ``Temperature``
        objects, with Celsius values running from `firstValue` to `lastValue`
        (inclusive), and the specified `step` between each consecutive
        temperature.

        For example, to get Celsius temperatures between 10°C and 30°C
        (inclusive), with each temperature being 5°C greater than the last
        (giving temperatures 10°C, 15°C, 20°C, 25°C, and 30°C)::

            temps = Temperature.celsiusRange(10, 30, 5)

        :param float firstValue: the Celsius value of the first
            ``Temperature`` to be included in the returned :py:class:`Sequence`.
            This must be greater than or equal to -273°C and less than
            or equal to 3000°C.
        :param float lastValue: the Celsius value of the last
            :py:class:`Temperature` to be included in the returned
            :py:class:`Sequence`. This must be greater than or equal to
            `firstValue`. Also, like for `firstValue`, this must be greater than
            or equal to -273°C and less than or equal to 3000°C.
        :param float step: the Celsius temperature difference between each
            temperature value to be included in the returned
            :py:class:`Sequence`. Cannot be `NaN`, and must be greater than
            zero. It must also be a multiple of 0.1 (the smallest temperature
            difference allowed), though allowances are made for floating-point
            imprecision (so for example a `step` of 0.4999999 will be treated as
            0.5).
        :raises TypeError: if `firstValue`, `lastValue`, or `step` is not a
            `float`.
        :raises ValueError: if any of the parameters are `NaN`; if `firstValue`
            or `lastValue` are outside of their allowed range (-273°C to 3000°C
            inclusive); if `lastValue` is less than `firstValue`; if `step` is
            not positive; or if `step` is not a multiple of 0.1 (allowing for
            slight deviations caused by floating-point imprecision).

        See also: :py:meth:`fahrenheitRange`, :py:meth:`TemperatureUnit.range`
        """
        return Temperature._range(
            TemperatureUnit.CELSIUS, firstValue, lastValue, step)
    @staticmethod
    def fahrenheitRange(firstValue, lastValue, step):
        # type: (float, float, float) -> Sequence[Temperature]
        """Returns a low-to-high sorted :py:class:`Sequence` of ``Temperature``
        objects, with Fahrenheit values running from `firstValue` to `lastValue`
        (inclusive), and the specified `step` between each consecutive
        temperature.

        For example, to get Fahrenheit temperatures between 50°F and 70°F
        (inclusive), with each temperature being 5°F greater than the last
        (giving temperatures 50°F, 55°F, 60°F, 65°F, and 70°F)::

            temps = Temperature.fahrenheitRange(50, 70, 5)

        :param float firstValue: the Fahrenheit value of the first
            ``Temperature`` to be included in the returned :py:class:`Sequence`.
            This must be greater than or equal to -459.4°F and less than
            or equal to 5432°F.
        :param float lastValue: the Fahrenheit value of the last
            :py:class:`Temperature` to be included in the returned
            :py:class:`Sequence`. This must be greater than or equal to
            `firstValue`. Also, like for `firstValue`, this must be greater than
            or equal to -459.4°F and less than or equal to 5432°F.
        :param float step: the Fahrenheit temperature difference between each
            temperature value to be included in the returned
            :py:class:`Sequence`. Cannot be `NaN`, and must be greater than
            zero. It must also be a multiple of 0.1 (the smallest temperature
            difference allowed), though allowances are made for floating-point
            imprecision (so for example a `step` of 0.4999999 will be treated as
            0.5).
        :raises TypeError: if `firstValue`, `lastValue`, or `step` is not a
            `float`.
        :raises ValueError: if any of the parameters are `NaN`; if `firstValue`
            or `lastValue` are outside of their allowed range (-459.4°F to
            5432°F inclusive); if `lastValue` is less than `firstValue`; if
            `step` is not positive; or if `step` is not a multiple of 0.1
            (allowing for slight deviations caused by floating-point
            imprecision).

        See also: :py:meth:`celsiusRange`, :py:meth:`TemperatureUnit.range`"""
        return Temperature._range(
            TemperatureUnit.FAHRENHEIT, firstValue, lastValue, step)
    @property
    def value(self): # type: () -> float
        # Must divide by 10.0 for same reason as in _formatTemperatureTimesTen
        """A `float` representation of the 0.1-precision number stored
        internally. Because of :ref:`rounding <rounding>`, this might not be
        exactly the same as the `float` that this instance was created with."""
        return self.__valueTimesTen / 10.0
    @property
    def unit(self): # type: () -> TemperatureUnit
        """The unit of this temperature."""
        return self.__unit
    @property
    def __intermediateValue(self): # type: () -> int
        if self.__unit == TemperatureUnit.CELSIUS:
            return self.__valueTimesTen * 9
        else:
            return (self.__valueTimesTen - 320) * 5
    def __compareTo(self, other): # type: (Temperature) -> int
        if self.__unit == other.__unit:
            return self.__valueTimesTen - other.__valueTimesTen
        intermediateDiff = self.__intermediateValue - other.__intermediateValue
        if intermediateDiff != 0:
            return intermediateDiff
        elif self.__unit == TemperatureUnit.CELSIUS:
            return -1 # put Celsius first
        else:
            return 1 # put Fahrenheit afterwards
    def __lt__(self, other): # type: (Temperature) -> bool
        return self.__compareTo(other) < 0
    def __gt__(self, other): # type: (Temperature) -> bool
        return self.__compareTo(other) > 0
    def __le__(self, other): # type: (Temperature) -> bool
        return self.__compareTo(other) <= 0
    def __ge__(self, other): # type: (Temperature) -> bool
        return self.__compareTo(other) >= 0
    def __repr__(self):
        if self.__unit == TemperatureUnit.CELSIUS:
            return 'Temperature.celsius(' + _formatTemperatureTimesTen(
                self.__valueTimesTen) + ')'
        else:
            return 'Temperature.fahrenheit(' + _formatTemperatureTimesTen(
                self.__valueTimesTen) + ')'
    def _toNumericString(self): # type: () -> str
        return _formatTemperatureTimesTen(self.__valueTimesTen)
    def __str__(self):
        return (self._toNumericString() + ' ' + self.__unit._shortChar)
    def _toXml(self, elementNameExtra=''): # type: (str) -> XmlElement
        return XmlElement(self.__unit._name + elementNameExtra).setValue(
            _formatTemperatureTimesTen(self.__valueTimesTen))
    @staticmethod
    def _check(param, paramName='temperature'):
        # type: (Temperature, str) -> Temperature
        if type(param) is not Temperature:
            raise TypeError(private.wrongTypeString(param, paramName,
                Temperature, _TEMPERATURE_EXAMPLE))
        return param

class _TimeSeriesIntervalMetaclass(type):
    _CODES = (0,)
    def __iter__(cls): # type: () -> Iterator[TimeSeriesInterval]
        for code in cls._CODES:
            yield TimeSeriesInterval._get(code)
    #EnumCopyStart(TimeSeriesInterval)
    @property
    def HOURLY(cls): # type: () -> TimeSeriesInterval
        """For regular hourly time-series data i.e. readings on the hour every
        hour.

        Access via: ``TimeSeriesInterval.HOURLY``"""
        return TimeSeriesInterval._get(0)
    #EnumCopyEnd
_TimeSeriesIntervalSuper = _TimeSeriesIntervalMetaclass(
    '_TimeSeriesIntervalSuper', (_Immutable,), {'__slots__': ()})
class TimeSeriesInterval(_TimeSeriesIntervalSuper):
    """Defines the interval (e.g. hourly) that time-series data should be
    calculated with."""
    __slots__ = ('__code', '__name', '__nameUpper')
    __map = {} # type: dict[int, TimeSeriesInterval]
    #EnumPaste(TimeSeriesInterval)
    def __new__(cls):
        raise TypeError('This is not built for direct '
                'instantiation.  Please use TimeSeriesInterval.HOURLY.')
    def __initImpl(self, code, name): # type: (int, str) -> None
        self.__code = code
        self.__name = name
        self.__nameUpper = name.upper()
    @classmethod
    def _create(cls, code): # type: (int) -> TimeSeriesInterval
        newItem = super(TimeSeriesInterval, cls).__new__(cls)
        if code == 0:
            newItem.__initImpl(0, 'Hourly')
        else:
            raise ValueError
        cls.__map[newItem.__code] = newItem
        return newItem
    @classmethod
    def _get(cls, code): # type: (int) -> TimeSeriesInterval
        return cls.__map[code]
    def __getattr__(self, name): # type: (str) -> str
        return getattr(_TimeSeriesIntervalMetaclass, name)
    def _equalityFields(self): # type: () -> int
        return self.__code
    def __str__(self): # type: () -> str
        return self.__name
    def __repr__(self):
        return 'TimeSeriesInterval.' + self.__nameUpper
    def _toXml(self):
        return XmlElement('Interval').setValue(self.__name)
    @staticmethod
    def _check(param, paramName='interval'):
        # type: (TimeSeriesInterval, str) -> TimeSeriesInterval
        if type(param) is not TimeSeriesInterval:
            raise TypeError(private.wrongTypeString(param, paramName,
                TimeSeriesInterval, 'TimeSeriesInterval.HOURLY'))
        return param
for _code in TimeSeriesInterval._CODES:
    TimeSeriesInterval._create(_code)

_CALCULATION_EXAMPLE = (
    'Calculation.heatingDegreeDays(Temperature.celsius(15.5)), '
    'Calculation.coolingDegreeDays(Temperature.fahrenheit(65))')            
class Calculation(_Immutable):
    #1 inheritance-diagram:: Calculation
    #   degreedays.api.data.impl.HeatingDegreeDaysCalculation
    #   degreedays.api.data.impl.CoolingDegreeDaysCalculation
    """Defines how degree days should be calculated e.g. HDD or CDD to a
    specific base temperature.

    **To create a** ``Calculation`` **object** you can use the static factory
    methods of this class.  For example::

        hdd = Calculation.heatingDegreeDays(Temperature.celsius(12.5))
        cdd = Calculation.coolingDegreeDays(Temperature.celsius(21))"""
    __slots__ = ()
    def __init__(self):
        raise TypeError(_ABSTRACT_INIT_FACTORY + _CALCULATION_EXAMPLE + '.')
    @staticmethod
    def heatingDegreeDays(baseTemperature):
        # type: (Temperature) -> impl.HeatingDegreeDaysCalculation
        """Returns a ``HeatingDegreeDaysCalculation`` object with the specified
        base temperature.

        :param Temperature baseTemperature: the base temperature that the
            heating degree days should be calculated to.
        :raises TypeError: if `baseTemperature` is not a :py:class:`Temperature`
            object."""
        import degreedays.api.data.impl as impl
        return impl.HeatingDegreeDaysCalculation(baseTemperature)
    @staticmethod
    def coolingDegreeDays(baseTemperature):
        # type: (Temperature) -> impl.CoolingDegreeDaysCalculation
        """Returns a ``CoolingDegreeDaysCalculation`` object with the specified
        base temperature.

        :param Temperature baseTemperature: the base temperature that the
            cooling degree days should be calculated to.
        :raises TypeError: if `baseTemperature` is not a :py:class:`Temperature`
            object."""
        import degreedays.api.data.impl as impl
        return impl.CoolingDegreeDaysCalculation(baseTemperature)
    def _toXml(self): # type: () -> XmlElement
        raise NotImplementedError
    @staticmethod
    def _check(param, paramName='calculation'):
        # type: (Calculation, str) -> Calculation
        if not isinstance(param, Calculation):
            raise TypeError(private.wrongSupertypeString(param, paramName,
                Calculation, _CALCULATION_EXAMPLE))
        return param

_TIME_SERIES_CALCULATION_EXAMPLE = (
    'TimeSeriesCalculation.hourlyTemperature(TemperatureUnit.CELSIUS)')            
class TimeSeriesCalculation(_Immutable):
    #1 inheritance-diagram:: TimeSeriesCalculation
    #   degreedays.api.data.impl.TemperatureTimeSeriesCalculation
    """Defines how time-series data should be calculated e.g. temperature data,
    with hourly figures, in Celsius.

    **To create a** ``TimeSeriesCalculation`` **object** you can use the static
    factory methods of this class. For example::

        hourlyTempsCalculation = TimeSeriesCalculation.hourlyTemperature(
                TemperatureUnit.CELSIUS)

    The docs for :py:class:`TimeSeriesDataSpec` have more on how to actually
    fetch time-series data with your specified ``TimeSeriesCalculation``.

    .. _why-is-time-series-data-calculated:

    Why is time-series data "calculated"?
    -------------------------------------
    You might wonder why time-series data such as hourly temperature data is
    "calculated" as opposed to just being returned...

    The thing is that real-world weather stations hardly ever report exactly on
    the hour, every hour. Different stations have different reporting
    frequencies and schedules, they can change over time (e.g. if a station has
    its equipment upgraded), and gaps in routine reporting are fairly common
    too. Higher-quality stations do tend to report at least hourly, but it's
    rarely exactly on the hour, and it's rarely perfectly regular either. We
    take whatever data the weather stations do report, and use it to calculate
    (or interpolate) neat, perfectly-regular time-series data (such as hourly
    temperature data) with all gaps filled with estimated data (which is marked
    as such so you can easily identify it).

    The end result is neat, regular data that is easy to store and easy to work
    with, but it actually takes a lot of processing to get it into that format.
    And this is why time-series data from our system is "calculated" as opposed
    to just being returned."""
    __slots__ = ()
    def __init__(self):
        raise TypeError(_ABSTRACT_INIT_FACTORY +
            _TIME_SERIES_CALCULATION_EXAMPLE + '.')
    @staticmethod
    def hourlyTemperature(temperatureUnit):
        # type: (TemperatureUnit) -> impl.TemperatureTimeSeriesCalculation
        """Returns a :py:class:`TemperatureTimeSeriesCalculation` object with
        :py:attr:`TimeSeriesInterval.HOURLY` and the specified
        :py:class:`TemperatureUnit`.

        :param TemperatureUnit temperatureUnit: specifies whether the data
            should be calculated in Celsius or Fahrenheit.
        :raises TypeError: if `temperatureUnit` is not a
            :py:class:`TemperatureUnit` object."""
        import degreedays.api.data.impl as impl
        return impl.TemperatureTimeSeriesCalculation(
            TimeSeriesInterval.HOURLY, temperatureUnit)
    @property
    def interval(self): # type: () -> TimeSeriesInterval
        """The :py:class:`TimeSeriesInterval
        <degreedays.api.data.TimeSeriesInterval>` indicating the interval (e.g.
        hourly) that the time-series data should be calculated with."""
        raise NotImplementedError
    def _toXml(self): # type: () -> XmlElement
        raise NotImplementedError
    @staticmethod
    def _check(param, paramName='timeSeriesCalculation'):
        # type: (TimeSeriesCalculation, str) -> TimeSeriesCalculation
        if not isinstance(param, TimeSeriesCalculation):
            raise TypeError(private.wrongSupertypeString(param, paramName,
                TimeSeriesCalculation, _TIME_SERIES_CALCULATION_EXAMPLE))
        return param

_DATA_SPEC_EXAMPLE = (
    'DataSpec.dated(calculation, datedBreakdown), '
    'DataSpec.average(calculation, averageBreakdown), '
    'DataSpec.timeSeries(timeSeriesCalculation, datedBreakdown)')
class DataSpec(_Immutable):
    #1 inheritance-diagram:: DataSpec DatedDataSpec AverageDataSpec
    #   TimeSeriesDataSpec 
    """Defines a specification of a single set of degree-day data (or
    temperature data) in all aspects other than the location that the data
    should be generated for.

    A ``DataSpec`` defines a single set of data only (e.g. degree days in just
    one base temperature), but the :py:class:`DataSpecs` class will enable you
    to include multiple ``DataSpec`` objects in a single
    :py:class:`LocationDataRequest`.

    **To create a** ``DataSpec`` **object** you can use the static factory
    methods of this class. For example::

        thirtyMostRecentHddValues = DataSpec.dated(
                Calculation.heatingDegreeDays(Temperature.fahrenheit(55)),
                DatedBreakdown.daily(Period.latestValues(30)))

        fiveYearAverageCdd = DataSpec.average(
                Calculation.coolingDegreeDays(Temperature.fahrenheit(65)),
                AverageBreakdown.fullYears(Period.latestValues(5)))

        hourlyTempsForLastCalendarYear = DataSpec.timeSeries(
                TimeSeriesCalculation.hourlyTemperature(TemperatureUnit.CELSIUS),
                DatedBreakdown.yearly(Period.latestValues(1)))

    See :py:class:`DatedDataSpec`, :py:class:`AverageDataSpec`, and
    :py:class:`TimeSeriesDataSpec` for example code showing how to use each one
    individually to fetch data from the API. Though do remember that, as
    mentioned above, you can also fetch multiple sets of data in a single
    request."""
    __slots__ = ()
    def __init__(self):
        raise TypeError(_ABSTRACT_INIT_FACTORY + _DATA_SPEC_EXAMPLE + '.')
    @staticmethod
    def dated(calculation, datedBreakdown):
        # type: (Calculation, DatedBreakdown) -> DatedDataSpec
        """Returns a ``DatedDataSpec`` object with the specified
        :py:class:`Calculation` and :py:class:`DatedBreakdown`.

        :param Calculation calculation: defines the way in which the degree days
            should be calculated in terms of their base temperature and whether
            they should be heating degree days or cooling degree days.
        :param DatedBreakdown datedBreakdown: defines the way in which the data
            should be broken down and the period that it should cover.
        :raises TypeError: if `calculation` is not a :py:class:`Calculation`
            object, or if `datedBreakdown` is not a :py:class:`DatedBreakdown`
            object.

        See :py:class:`DatedDataSpec` for more info and a code sample."""
        return DatedDataSpec(calculation, datedBreakdown)
    @staticmethod
    def average(calculation, averageBreakdown):
        # type: (Calculation, AverageBreakdown) -> AverageDataSpec
        """Returns an ``AverageDataSpec`` object with the specified
        :py:class:`Calculation` and :py:class:`AverageBreakdown`.

        :param Calculation calculation: defines the way in which the degree days
            should be calculated in terms of their base temperature and whether
            they should be heating degree days or cooling degree days.
        :param AverageBreakdown averageBreakdown: defines the way in which the
            data should be broken down and the period that it should cover.
        :raises TypeError: if `calculation` is not a :py:class:`Calculation`
            object, or if `averageBreakdown` is not an
            :py:class:`AverageBreakdown` object.

        See :py:class:`AverageDataSpec` for more info and a code sample."""
        return AverageDataSpec(calculation, averageBreakdown)
    @staticmethod
    def timeSeries(timeSeriesCalculation, datedBreakdown):
        # type: (TimeSeriesCalculation, DatedBreakdown) -> TimeSeriesDataSpec
        """Returns a ``TimeSeriesDataSpec`` object with the specified
        :py:class:`TimeSeriesCalculation` and :py:class:`DatedBreakdown`.

        :param TimeSeriesCalculation timeSeriesCalculation: defines how the
            time-series data should be :ref:`calculated
            <why-is-time-series-data-calculated>` (e.g. specifying hourly
            temperature data, in Celsius).
        :param DatedBreakdown datedBreakdown: defines the period of time that
            the time-series data should cover (:ref:`read more on how this works
            <why-time-series-data-breakdown>`).
        :raises TypeError: if `timeSeriesCalculation` is not a
            :py:class:`TimeSeriesCalculation` object or `datedBreakdown` is not
            a :py:class:`DatedBreakdown` object.

        See :py:class:`TimeSeriesDataSpec` for more info and a code sample."""
        return TimeSeriesDataSpec(timeSeriesCalculation, datedBreakdown)
    def _toXml(self): # type: () -> XmlElement
        raise NotImplementedError
    @staticmethod
    def _check(param, paramName='dataSpec'):
        # type: (DataSpec, str) -> DataSpec
        if not isinstance(param, DataSpec):
            raise TypeError(private.wrongSupertypeString(param, paramName,
                DataSpec, _DATA_SPEC_EXAMPLE))
        return param

class DatedDataSpec(DataSpec):
    #1 inheritance-diagram:: DatedDataSpec
    """Defines a specification for a set of dated data such as daily, weekly, or
    monthly degree days covering a specific period in time.

    **To create a** ``DatedDataSpec`` **object** use :py:meth:`DataSpec.dated`.

    A ``DatedDataSpec`` specifies a set of degree days in terms of:

    * its calculation process (heating or cooling, and the base temperature);
      and
    * its breakdown (e.g. daily, weekly, or monthly, and the period covered).

    Example ``DatedDataSpec`` code:
    -------------------------------
    Here's how you could specify monthly heating degree days with a base
    temperature of 15.5°C covering the whole of 2019::

        datedDataSpec = DataSpec.dated(
                Calculation.heatingDegreeDays(Temperature.celsius(15.5)),
                DatedBreakdown.monthly(Period.dayRange(degreedays.time.DayRange(
                    datetime.date(2019, 1, 1), datetime.date(2019, 12, 31)))))

    You could then send that ``DatedDataSpec`` to the API as part of a
    :py:class:`LocationDataRequest`, and get a response containing an 
    :py:class:`DatedDataSet` back::

        api = DegreeDaysApi.fromKeys(AccountKey(yourStringAccountKey),
                SecurityKey(yourStringSecurityKey))
        request = LocationDataRequest(
                Location.stationId("KHYA"),
                DataSpecs(datedDataSpec))
        response = api.dataApi.getLocationData(request)
        datedData = response.dataSets[datedDataSpec]
        for v in datedData.values:
            print('%s: %g' % (v.dayRange, v.value))

    To request multiple sets of dated data with different calculation processes
    (e.g. multiple different base temperatures) and/or different breakdowns,
    simply put multiple ``DatedDataSpec`` objects into the :py:class:`DataSpecs`
    object that you pass into your :py:class:`LocationDataRequest`.

    See also: :py:class:`AverageDataSpec`, :py:class:`TimeSeriesDataSpec`"""
    __slots__ = ('__calculation', '__breakdown')
    def __init__(self, calculation, datedBreakdown):
        # type: (Calculation, DatedBreakdown) -> None
        self.__calculation = Calculation._check(calculation)
        self.__breakdown = DatedBreakdown._check(datedBreakdown)
    def _equalityFields(self):
        return (self.__calculation, self.__breakdown)
    @property
    def calculation(self): # type: () -> Calculation
        """The :py:class:`Calculation` object that defines the way in which the
        degree days should be calculated in terms of their base temperature and
        whether they should be heating degree days or cooling degree days."""
        return self.__calculation
    @property
    def breakdown(self): # type: () -> DatedBreakdown
        """The :py:class:`DatedBreakdown` object that defines the way in which
        the degree days should be broken down and the period in time that they
        should cover."""
        return self.__breakdown
    def __repr__(self):
        return 'DatedDataSpec(%r, %r)' % (self.__calculation, self.__breakdown)
    def _toXml(self):
        return XmlElement('DatedDataSpec') \
            .addChild(self.__calculation._toXml()) \
            .addChild(self.__breakdown._toXml())

class AverageDataSpec(DataSpec):
    #1 inheritance-diagram:: AverageDataSpec
    """Defines a specification for a set of average data such as 5-year-average
    degree days.

    **To create an** ``AverageDataSpec`` **object** use
    :py:meth:`DataSpec.average`.

    An ``AverageDataSpec`` specifies a set of average degree days in terms of:

    * the calculation process used to calculate the dated figures that the
      averages are derived from (heating or cooling, and the base temperature);
      and
    * its breakdown (which years of data to include in the averaged figures).

    Example ``AverageDataSpec`` code:
    ---------------------------------
    Here's how you could specify 10-year average heating degree days with a base
    temperature of 70°F::

        averageDataSpec = DataSpec.average(
                Calculation.heatingDegreeDays(Temperature.fahrenheit(70)),
                AverageBreakdown.fullYears(Period.latestValues(10)))

    You could then send that ``AverageDataSpec`` to the API as part of a
    :py:class:`LocationDataRequest`, and get a response containing an 
    :py:class:`AverageDataSet` back::

        api = DegreeDaysApi.fromKeys(AccountKey(yourStringAccountKey),
                SecurityKey(yourStringSecurityKey))
        request = new LocationDataRequest(
                Location.postalCode('02630', 'US'),
                new DataSpecs(averageDataSpec))
        response = api.dataApi.getLocationData(request)
        averageData = response.dataSets[averageDataSpec]
        for month in range(1, 12):
        print('Average HDD for month %i: %g' %
                (month, averageData.monthlyAverage(month).value))
        print('Annual average HDD: %g' % averageData.annualAverage.value)

    To request multiple sets of average data with different calculation
    processes (e.g. multiple different base temperatures) and/or different
    breakdowns, simply put multiple ``AverageDataSpec`` objects into the
    :py:class:`DataSpecs` object that you pass into your
    :py:class:`LocationDataRequest`.

    See also: :py:class:`DatedDataSpec`, :py:class:`TimeSeriesDataSpec`"""
    __slots__ = ('__calculation', '__breakdown')
    def __init__(self, calculation, averageBreakdown):
        # type: (Calculation, AverageBreakdown) -> None
        self.__calculation = Calculation._check(calculation)
        self.__breakdown = AverageBreakdown._check(averageBreakdown)
    def _equalityFields(self):
        return (self.__calculation, self.__breakdown)
    @property
    def calculation(self): return self.__calculation
    @property
    def breakdown(self): return self.__breakdown
    def __repr__(self):
        return ('AverageDataSpec(%r, %r)' %
            (self.__calculation, self.__breakdown))
    def _toXml(self):
        return XmlElement('AverageDataSpec') \
            .addChild(self.__calculation._toXml()) \
            .addChild(self.__breakdown._toXml())

class TimeSeriesDataSpec(DataSpec):
    #1 inheritance-diagram:: TimeSeriesDataSpec
    """Defines a specification for a set of time-series data such as hourly
    temperature data covering a specific period in time.

    **To create a** ``TimeSeriesDataSpec`` **object** use
    :py:meth:`DataSpec.timeSeries`.

    A ``TimeSeriesDataSpec`` specifies a set of time-series data in terms of:

    * the calculation process used to calculate the time-series figures
      (:ref:`find out why time-series data is "calculated"
      <why-is-time-series-data-calculated>`); and
    * a breakdown that determines the period in time that the time-series data
      should cover (more on this below).

    Example ``TimeSeriesDataSpec`` code:
    ------------------------------------
    Here's how you could specify hourly temperature data, in Fahrenheit,
    covering the last 30 days::

        timeSeriesDataSpec = DataSpec.timeSeries(
                TimeSeriesCalculation.hourlyTemperature(TemperatureUnit.FAHRENHEIT),
                DatedBreakdown.daily(Period.latestValues(30)))

    You could then send that ``TimeSeriesDataSpec`` to the API as part of a
    :py:class:`LocationDataRequest`, and get a response containing a
    :py:class:`TimeSeriesDataSet` back::

        api = DegreeDaysApi.fromKeys(AccountKey(yourStringAccountKey),
                SecurityKey(yourStringSecurityKey))
        request = LocationDataRequest(
                Location.postalCode("02630", "US"),
                DataSpecs(timeSeriesDataSpec))
        response = api.dataApi.getLocationData(request)
        hourlyData = response.dataSets[timeSeriesDataSpec]
        for v in hourlyData.values:
            print('%s: %g' % (v.datetime, v.value))

    **To include figures for the current day** (as opposed to the default
    behaviour of covering full days only), you can specify a
    :py:class:`DatedBreakdown` with its
    :py:class:`DatedBreakdown.allowPartialLatest` property set to `True`. For
    example::

        hourlyTempsIncludingToday = DataSpec.timeSeries(
            TimeSeriesCalculation.hourlyTemperature(TemperatureUnit.FAHRENHEIT),
            DatedBreakdown.daily(Period.latestValues(31), allowPartialLatest=True))

    The docs for :py:attr:`DatedBreakdown.allowPartialLatest` explain more,
    including an important caution that the latest figures can be volatile, and,
    if stored, should be overwritten later when the weather stations have had
    time to send any delayed or corrected weather reports (which many weather
    stations send quite often).

    .. _why-time-series-data-breakdown:

    Why does ``TimeSeriesDataSpec`` take a ``DatedBreakdown``?
    ---------------------------------------------------------- 
    It might seem strange that ``TimeSeriesDataSpec`` takes a
    :py:class:`DatedBreakdown` in the same way that :py:class:`DatedDataSpec`
    (for degree days) does, because hourly data is broken down hourly, not by
    days, weeks, or months. However, it works this way to give you flexibility
    in how you specify the time-period that the time-series data should cover,
    and to make it easier for you to get time-series data that lines up with
    your degree days.

    With a :py:class:`DatedBreakdown` you can easily specify that you want
    hourly data covering e.g. the last 30 days, or the last 12 full calendar
    months, or the last 5 full calendar years, just like you do when you are
    using a :py:class:`DatedBreakdown` to specify the degree days you want. You
    can take full advantage of :ref:`widening rules <widening>` if they make
    things more convenient for you. The data will always come back as hourly
    figures. Essentially a daily, weekly, monthly, or yearly breakdown in a
    ``TimeSeriesDataSpec`` is used only to determine the overall period of time
    that the time-series data should cover.

    Custom breakdowns (made with :py:meth:`DatedBreakdown.custom`) deserve a
    special note, however... If you create a ``TimeSeriesDataSpec`` with a
    custom breakdown (made up of your own custom-specified 
    :py:class:`degreedays.time.DayRanges`), then your time-series data will
    cover only the day ranges you specify. If you specify day ranges with gaps
    between them, then your time-series data will have gaps too (just as your
    degree days would if you used the same breakdown for them).  This is rather
    contrary to our general ethos of providing continuous data with no gaps, but
    it will only happen if you specifically request it (by specifying a custom
    breakdown with gaps between its day ranges).
    
    See also: :py:class:`DatedDataSpec`, :py:class:`AverageDataSpec`"""
    __slots__ = ('__calculation', '__breakdown')
    def __init__(self, timeSeriesCalculation, datedBreakdown):
        # type: (TimeSeriesCalculation, DatedBreakdown) -> None
        self.__calculation = TimeSeriesCalculation._check(timeSeriesCalculation)
        self.__breakdown = DatedBreakdown._check(datedBreakdown)
    def _equalityFields(self):
        return (self.__calculation, self.__breakdown)
    @property
    def calculation(self): # type: () -> TimeSeriesCalculation
        """The :py:class:`TimeSeriesCalculation` object that defines how the
        time-series data should be :ref:`calculated
        <why-is-time-series-data-calculated>`. For example it could specify
        hourly temperature data, in Celsius."""
        return self.__calculation
    @property
    def breakdown(self): # type: () -> DatedBreakdown
        """The :py:class:`DatedBreakdown` object that defines the period of time
        that the time-series data should cover (:ref:`read more on how this
        works <why-time-series-data-breakdown>`)."""
        return self.__breakdown
    def __repr__(self):
        return 'TimeSeriesDataSpec(%r, %r)' % (self.__calculation, self.__breakdown)
    def _toXml(self):
        return XmlElement('TimeSeriesDataSpec') \
            .addChild(self.__calculation._toXml()) \
            .addChild(self.__breakdown._toXml())

_DATA_SPEC_KEY_REGEXP_STRING = '[-_.0-9a-zA-Z]{1,60}$'
_DATA_SPEC_KEY_REGEXP = re.compile(_DATA_SPEC_KEY_REGEXP_STRING)
# This assumes that it's already been checked to see that it's a string.
def _checkDataSpecStringKey(key): # type: (str) -> str
    if not _DATA_SPEC_KEY_REGEXP.match(key):
        raise ValueError('Invalid DataSpec/DataSet key (%r) - it should match '
            'the regular expression %s.' % (key, _DATA_SPEC_KEY_REGEXP_STRING))
    return key

_DATA_SPECS_EXAMPLE = ('DataSpecs(hddSpec), '
    'DataSpecs(hddSpec, cddSpec), '
    'DataSpecs(listOfDataSpecObjects)')
class DataSpecs(_Immutable):
    """Defines up to 120 sets of data that should be generated to fulfil a
    :py:class:`LocationDataRequest`.

    :param \\*args: up to
        120 :py:class:`DataSpec` objects, or one or more sequences (e.g. lists
        or tuples) containing a total of up to 120 ``DataSpec`` objects.  In
        rare cases you may want to pass in a ``Mapping[str, DataSpec]`` of
        string :ref:`keys <keys>` to ``DataSpec`` objects.
    :raises TypeError: if you pass in anything that isn't a :py:class:`DataSpec`
        object, a sequence (e.g. list or tuple) of ``DataSpec`` objects, or a
        single ``Mapping[str, DataSpec]`` (in the unlikely event that you are
        defining your own :ref:`keys <keys>`).
    :raises ValueError: if you pass in zero :py:class:`DataSpec` objects or more
        than 120 of them.

    When requesting multiple sets of data for a particular location, it makes
    sense to use multiple :py:class:`DataSpec` objects to retrieve as much data
    as possible in a single request. This is cheaper and faster than fetching
    the same data across multiple requests. For example, for a particular
    location you might want to request heating and cooling degree days at 5
    different base temperatures each. This would require 10 different
    ``DataSpec`` objects in total. By putting all 10 ``DataSpec`` objects in a
    single ``DataSpecs`` object, you could fetch all 10 sets of data in a single
    request.

    For example, if ``ds1`` to ``ds10`` are :py:class:`DataSpec` objects you
    have created already::

        dataSpecs = DataSpecs(ds1, ds2, ds3, ds4, ds5, ds6, ds7, ds8, ds9, ds10)

    For most use cases, all you will ever need to do with this class is pass in
    the :py:class:`DataSpec` objects you want, then pass the ``DataSpecs`` into
    a :py:class:`LocationDataRequest` object. However, there is a small chance
    that you could find it useful to understand about keys and the uniqueness of
    ``DataSpec`` objects:

    .. _keys:

    Keys
    ----
    The XML request (which this Python library generates internally) requires
    that each :py:class:`DataSpec` be assigned a unique string key attribute so
    that its corresponding :py:class:`DataSet` can be found in the XML response
    (which this Python library parses internally). This ``DataSpecs`` class is
    central to the way that the keys are created and managed. It essentially
    gives you two options for key management:

    #. You can let this ``DataSpecs`` class generate and manage the keys
       entirely, such that you never have to see them or use them directly. You
       can fetch your :py:class:`DataSet` objects out of the
       :py:class:`LocationDataResponse` using the :py:class:`DataSpec` objects
       that you created for the request (and kept on hand for this purpose). We
       recommend this approach in virtually all cases.
    #. You can specify your own keys explicitly. If this is the case, create a
       ``DataSpecs`` object by passing in a :py:class:`Mapping` (e.g. a
       ``dict``) with your own custom key-to-:py:class:`DataSpec` mappings.

    .. _uniqueness:

    Uniqueness of ``DataSpec`` objects
    ----------------------------------
    There is no point in submitting a request containing multiple identical
    :py:class:`DataSpec` objects, as it would lead to unnecessary duplication in
    the results and unnecessary bandwidth usage for the communication between
    the client and API servers.

    Unless you are specifying your own keys (by passing in a
    ``Mapping[str, DataSpec]``), this class is set up to prevent duplicate
    :py:class:`DataSpec` objects from being submitted as part of a request. It
    does this by filtering and discarding all duplicate ``DataSpec`` objects
    passed in when an instance is created. So, if you pass in 10 ``DataSpec``
    objects, and only 5 of those are unique, then only the 5 unique ``DataSpec``
    objects will be stored internally and sent as part of the XML request.

    Because discarded duplicate :py:class:`DataSpec` objects are identical to
    their retained counterparts, you can still use the duplicates to retrieve
    fetched data out of the :py:class:`LocationDataResponse`. In other words,
    **the internal process of filtering and discarding duplicate**
    :py:class:`DataSpec` **objects should not affect the way in which you use
    this API**.

    If you create your own keys, then duplicate :py:class:`DataSpec` objects are
    *not* filtered. Filtering duplicate ``DataSpec`` objects would also involve
    filtering the keys associated with the duplicates, and this could cause
    problems for code of yours that was expecting those keys in the XML
    response. You can rely on the fact that, if you define your own ``DataSpec``
    keys, your XML response will contain entries for all of your keys,
    irrespective of whether some of the data associated with those keys is
    duplicated.

    See also: :py:meth:`DataApi.getLocationData(locationDataRequest)
    <DataApi.getLocationData>`"""
    __slots__ = ('__specToKeyMap', '__keyToSpecMap', '__orderedKeys',
            '__specSet')
    def __init__(self, *args):
        # type: (DataSpec | Iterable[DataSpec] | Mapping[str, DataSpec]) -> None
        # We only allow one Mapping, not the multiple implied by the type hint,
        # but it's an unusual use case to want to specify keys at all, and if
        # doing so it would be very strange to want multiple Mappings.
        self.__specToKeyMap = {} # type: dict[DataSpec, str]
        # Could use OrderedDict, but that is Python 2.7+ and I'm not sure we
        # want to restrict to that version just for that.
        self.__keyToSpecMap = {} # type: dict[str, DataSpec]
        orderedKeys = [] # type: list[str]
        if len(args) == 1 and private.isMapping(args[0]):
            asMapping = args[0] # type: Mapping[str, DataSpec]
            for key, item in private.getDictItemsIterable(asMapping):
                if not private.isString(key):
                    raise TypeError('If creating this with a Mapping (to '
                        'specify custom keys for the request XML), DataSpecs '
                        'expects string keys.  But the Mapping it was passed '
                        'contained %r as a key.' % key)
                elif not isinstance(item, DataSpec):
                    raise TypeError('If creating this with a Mapping (to '
                        'specify custom keys for the request XML), DataSpecs '
                        'expects the values associated with each key to be '
                        'DataSpec instances (e.g. DataSpec.dated(...) or '
                        'DataSpec.average(...)).  But for key %r it found %r' %
                        (key, item))
                key = _checkDataSpecStringKey(key)
                self.__specToKeyMap[item] = key
                self.__keyToSpecMap[key] = item
                orderedKeys.append(key)
        else:
            def add(item): # type: (DataSpec) -> None
                index = len(orderedKeys)
                if index >= 120:
                    raise ValueError(
                        'Cannot have more than 120 DataSpec items.')
                if isinstance(item, DataSpec):
                    if not item in self.__specToKeyMap:
                        key = str(index) # simple integer key for now
                        self.__specToKeyMap[item] = key
                        self.__keyToSpecMap[key] = item
                        orderedKeys.append(key)
                elif private.isString(item):
                    # Have to be careful with strings cos they look like a
                    # sequence but will cause a stack overflow, see:
                    # https://stackoverflow.com/questions/1835018/
                    DataSpec._check(item,
                        'An item passed into the DataSpecs constructor')
                else:
                    # Assume it's a sequence, just let it throw TypeError if
                    # it's not (as tested in python_tests.py).
                    for innerItem in item:
                        add(innerItem)
            for arg in args:
                add(arg)
        if len(orderedKeys) == 0:
            raise ValueError('Must have at least one DataSpec')
        # We create specSet purely for a quick equality comparison, as
        # described at:
        # http://stackoverflow.com/questions/3210832/
        # Note it has to be frozenset, not set, because only frozenset (which
        # is immutable) is hashable.
        self.__specSet = frozenset(self.__specToKeyMap)
        # Make tuple so immutable.
        self.__orderedKeys = tuple(orderedKeys)
    def _equalityFields(self):
        return self.__specSet
    @property
    def keys(self): # type: () -> Collection[str]
        """Gives access to the string keys that are assigned to the
        :py:class:`DataSpec` objects stored within this ``DataSpecs``.

        See also: :ref:`keys <keys>`"""
        # The keys are ordered to reduce the potential for confusion, but really
        # DataSpecs is meant to be like an unordered dict, hence we return
        # Collection rather than Sequence.
        return self.__orderedKeys
    def __getitem__(self, key): # type: (str) -> DataSpec
        return self.__keyToSpecMap[key]
    def getKey(self, dataSpec): # type: (DataSpec) -> str
        """Returns the non-empty string key associated with `dataSpec`.

        :param DataSpec dataSpec: a a data specification held by this
            ``DataSpecs``.
        :raises TypeError: if `dataSpec` is not a :py:class:`DataSpec` object.
        :raises KeyError: if `dataSpec` is not one of the :py:class:`DataSpec`
            objects held by this ``DataSpecs``.

        See also: :ref:`keys <keys>`"""
        DataSpec._check(dataSpec)
        return self.__specToKeyMap[dataSpec]
    def _containsKey(self, key): # type: (str) -> bool
        return key in self.__keyToSpecMap
    def _dataSetsEquals(self,
            thisResults, # type: dict[str, DataSet | api.Failure]
            thatDataSpecs, # type: DataSpecs
            thatResultsMap # type: dict[str, DataSet | api.Failure]
            ): # type: (...) -> bool
        for spec, thisKey in private.getDictItemsIterable(self.__specToKeyMap):
            thisResult = thisResults[thisKey]
            thatKey = thatDataSpecs.__specToKeyMap[spec]
            thatResult = thatResultsMap[thatKey]
            if thisResult != thatResult:
                return False
        return True
    def _dataSetsHashCode(self, thisResultsMap):
        # type: (dict[str, DataSet | api.Failure]) -> int
        hashCode = 17
        # hashCode of the DataSpecs stored inside the DataSets.
        hashCode = 31 * hashCode + hash(self)
        # We want to sum the hashCodes of the DataSet objects corresponding to
        # each unique DataSpec.
        #
        # We need to sum without a multiplier because, if we used a multiplier,
        # then the result would depend on the order.  And we don't want that.
        # This is like how it's done in Java's AbstractSet.
        for key in private.getDictValuesIterable(self.__specToKeyMap):
            result = thisResultsMap[key]
            hashCode += hash(result)
        # Before python 2.2 (earlier than this library covers), Python int
        # operations used to result in an error if they got big or small enough
        # to overflow.  They never overflowed automatically like Java ints.
        # Before 3 they automatically turn into longs, after 3 then there is no
        # difference between ints and longs anyway - they're both the int type:
        # http://www.python.org/dev/peps/pep-0237/
        # http://stackoverflow.com/questions/4581842/
        # http://stackoverflow.com/questions/2104884/
        # The docs for __hash__ say it should return an integer, but that, since
        # 2.5 it can return a long, and the system will use the 32-bit hash of
        # that object.  See:
        # http://docs.python.org/2/reference/datamodel.html#object.__hash__
        # To make this work for Python 2.2 to 2.5, we check for int and return
        # the hash if it isn't one (because presumably it's a long).
        # We don't worry about pre-2.2 at all - that may throw an overflow
        # error above.
        if not isinstance(hashCode, int):
            hashCode = hash(hashCode)
        return hashCode
    def __len__(self):
        return len(self.__orderedKeys)
    def __repr__(self):
        # We make this include the keys.  It's more useful for DataSets.__repr__
        # and for debugging, if necessary.  Also the keys are pretty short.
        s = [] # type: list[str]
        for key in self.__orderedKeys:
            s.append("'%s': %r" % (key, self.__keyToSpecMap[key]))
        s.sort()
        return 'DataSpecs({' + ', '.join(s) + '})'
    def _toXml(self): # type: () -> XmlElement
        parent = XmlElement('DataSpecs')
        for key in self.__orderedKeys:
            child = self.__keyToSpecMap[key]._toXml().addAttribute('key', key)
            parent.addChild(child)
        return parent
    @staticmethod
    def _check(param, paramName='dataSpecs'):
        # type: (DataSpecs, str) -> DataSpecs
        if type(param) is not DataSpecs:
            raise TypeError(private.wrongTypeString(param, paramName,
                DataSpecs, _DATA_SPECS_EXAMPLE))
        return param

_LOCATION_DATA_REQUEST_EXAMPLE = (
    "LocationDataRequest(Location.stationId('EGLL'), "
        "DataSpecs(DataSpec.dated("
            "Calculation.heatingDegreeDays(Temperature.fahrenheit(65)), "
                "DatedBreakdown.monthly(Period.latestValues(12)))))")
class LocationDataRequest(api.Request):
    #1 inheritance-diagram:: LocationDataRequest
    """Defines a request for one or more sets of data from a particular
    location. A successfully-processed ``LocationDataRequest`` will result in a
    :py:class:`LocationDataResponse` containing the specified data.

    :param Location location: the location for which the data should be
        generated.
    :param DataSpecs dataSpecs: the specification of how the set(s) of data
        should be calculated and broken down.
    :raises TypeError: if `location` is not a subclass of :py:class:`Location`,
        or if `dataSpecs` is not a :py:class:`DataSpecs` object.

    Here's an example showing how to create a request for one set of data from
    the EGLL weather station in London, UK. The request specifies heating degree
    days with a base temperature of 15.5°C, broken down on a daily basis and
    covering the whole of July 2024::

        period = Period.dayRange(degreedays.time.DayRange(
                datetime.date(2024, 7, 1), datetime.date(2024, 7, 31)))
        breakdown = DatedBreakdown.daily(period)
        baseTemp = Temperature.celsius(15.5)
        calculation = Calculation.heatingDegreeDays(baseTemp)
        dataSpec = DataSpec.dated(calculation, breakdown)
        location = Location.stationId('EGLL')
        request = LocationDataRequest(
                location, DataSpecs(dataSpec))

    Here's an example showing how to create a request for two sets of data from
    Times Square in New York. We specify the location as a zip code (a type of
    :py:class:`GeographicLocation`), leaving it to the API to choose the most
    appropriate weather station in the area. The request specifies heating
    degree days with a base temperature of 55°F, and cooling degree days with a
    base temperature of 65°F, both broken down on a monthly basis and covering
    the last 12 months::

        breakdown = DatedBreakdown.monthly(Period.latestValues(12))
        hddSpec = DataSpec.dated(
                Calculation.heatingDegreeDays(Temperature.fahrenheit(55)),
                breakdown)
        cddSpec = DataSpec.dated(
                Calculation.coolingDegreeDays(Temperature.fahrenheit(65)),
                breakdown)
        request = LocationDataRequest(
                Location.postalCode('10036', 'US'),
                DataSpecs(hddSpec, cddSpec))

    See :py:meth:`DataApi.getLocationData(locationDataRequest)
    <DataApi.getLocationData>` for an example of how to submit a
    ``LocationDataRequest`` to the API and get a
    :py:class:`LocationDataResponse` back containing the data you requested."""
    __slots__ = ('__location', '__dataSpecs')
    def __init__(self, location, dataSpecs):
        # type: (Location, DataSpecs) -> None
        self.__location = Location._check(location)
        self.__dataSpecs = DataSpecs._check(dataSpecs)
    def _equalityFields(self):
        return (self.__location, self.__dataSpecs)
    @property
    def location(self): # type: () -> Location
        """The :py:class:`Location` object that specifies the location for which
        the data should be generated."""
        return self.__location
    @property
    def dataSpecs(self): # type: () -> DataSpecs
        """The :py:class:`DataSpecs` object that specifies how the set(s) of
        data should be calculated and broken down."""
        return self.__dataSpecs
    def __repr__(self):
        return ('LocationDataRequest(%r, %r)' %
            (self.__location, self.__dataSpecs))
    def _toXml(self):
        return XmlElement('LocationDataRequest') \
            .addChild(self.__location._toXml()) \
            .addChild(self.__dataSpecs._toXml())
    @staticmethod
    def _check(param, paramName='locationDataRequest'):
        # type: (LocationDataRequest, str) -> LocationDataRequest
        if type(param) is not LocationDataRequest:
            raise TypeError(private.wrongTypeString(param, paramName,
                LocationDataRequest, _LOCATION_DATA_REQUEST_EXAMPLE))
        return param

_LOCATION_INFO_REQUEST_EXAMPLE = (
    "LocationInfoRequest(Location.stationId('EGLL'), "
        "DataSpecs(DataSpec.dated("
            "Calculation.heatingDegreeDays(Temperature.fahrenheit(65)), "
                "DatedBreakdown.monthly(Period.latestValues(12)))))")
class LocationInfoRequest(api.Request):
    #1 inheritance-diagram:: LocationInfoRequest
    """Defines a request for info about the station(s) that would be used to
    fulfil an equivalent :py:class:`LocationDataRequest`.

    :param Location location: the location for which data is desired.
    :param DataSpecs dataSpecs: the specification of the data that is desired
        from the specified location.
    :raises TypeError: if `location` is not a subclass of :py:class:`Location`,
        or if `dataSpecs` is not a :py:class:`DataSpecs` object.

    ``LocationInfoRequest`` is effectively a lightweight alternative to
    :py:class:`LocationDataRequest`, primarily for use when you want to know
    what station ID the API *would* use for a given
    :py:class:`GeographicLocation` and :py:class:`DataSpecs`, without the
    overhead of actually fetching the specified data.  A ``LocationInfoRequest``
    will only ever take one request unit, whilst a
    :py:class:`LocationDataRequest` can take many more (depending on how much
    data it fetches).

    A successfully-processed ``LocationInfoRequest`` will result in a
    :py:class:`LocationInfoResponse`.

    See :py:meth:`DataApi.getLocationInfo(locationInfoRequest)
    <DataApi.getLocationInfo>` for an example of how to create a
    ``LocationInfoRequest``, submit it to the API, and get a
    :py:class:`LocationInfoResponse` back."""
    __slots__ = ('__location', '__dataSpecs')
    def __init__(self, location, dataSpecs):
        # type: (Location, DataSpecs) -> None
        self.__location = Location._check(location)
        self.__dataSpecs = DataSpecs._check(dataSpecs)
    def _equalityFields(self):
        return (self.__location, self.__dataSpecs)
    @property
    def location(self): # type: () -> Location
        """The :py:class:`Location` object for which data is desired."""
        return self.__location
    @property
    def dataSpecs(self): # type: () -> DataSpecs
        """The :py:class:`DataSpecs` object that specifies the data that is
        desired from the specified location."""
        return self.__dataSpecs
    def __repr__(self):
        return ('LocationInfoRequest(%r, %r)' %
            (self.__location, self.__dataSpecs))
    def _toXml(self):
        return XmlElement('LocationInfoRequest') \
            .addChild(self.__location._toXml()) \
            .addChild(self.__dataSpecs._toXml())
    @staticmethod
    def _check(param, paramName='locationInfoRequest'):
        # type: (LocationInfoRequest, str) -> LocationInfoRequest
        if type(param) is not LocationInfoRequest:
            raise TypeError(private.wrongTypeString(param, paramName,
                LocationInfoRequest, _LOCATION_INFO_REQUEST_EXAMPLE))
        return param


class LocationError(api.RequestFailureError):
    #1 inheritance-diagram:: LocationError
    """Indicates a :py:class:`Failure <degreedays.api.Failure>` in the API's
    processing of a request, caused by problems with the :py:class:`Location`
    that the request specified.

    This exception corresponds to any :ref:`failure code <failure-codes>`
    code starting with "Location".

    You can interrogate the :ref:`isDueToXXX <is-due-to-properties>` properties
    of this exception to find out more about the cause. But do note that it is
    possible for none of those properties to be `True` if a relevant new
    :ref:`failure code <failure-codes>` is added into the API. Be prepared for
    this in your handling.

    You might not need to pay any attention to the specific code behind the
    ``LocationError``. For many use-cases, the best way to handle a
    ``LocationError`` is just to try again with an alternative location. For
    example, if a request for data from a specific
    :py:meth:`Location.stationId` fails, you might want to try a request for the
    :py:class:`GeographicLocation` of the real-world building you ultimately
    want data for, so that the API can find a replacement station for you
    automatically."""
    def __init__(self, failureResponse): # type: (api.FailureResponse) -> None
        api.RequestFailureError.__init__(self, failureResponse)
    @property
    def isDueToLocationNotRecognized(self): # type: () -> bool
        """`True` if this failure came in response to a request for data from a
        location that the API did not recognize as a weather station or
        real-world geographic location; `False` otherwise.

        This type of failure will occur if you specify a
        :py:meth:`Location.stationId` with an unrecognized ID, or a
        :py:meth:`Location.postalCode` with an unrecognized postal code."""
        return self._testCode('LocationNotRecognized')
    @property
    def isDueToLocationNotSupported(self): # type: () -> bool
        """`True` if this failure came in response to a request for data from a
        location that is recognized but not currently supported by the API;
        `False` otherwise.

        This can happen if you request data from a
        :py:class:`GeographicLocation` for which the API is unable to find a
        good weather station. In this instance it is possible that a weather
        station with usable data does exist in the area - you could try visiting
        `www.degreedays.net <https://www.degreedays.net/>`__ and searching
        manually to see if you can find a good weather station to use for future
        API requests (referencing it by station ID). But you will probably have
        to look some distance from the location of interest to find a usable
        station.

        This can also happen if you request data from a weather station that has
        not sent any usable weather reports for roughly 10 days or more (10
        being an approximate number that is subject to change). We call such
        stations "inactive".

        Some stations have *never* reported valid temperatures, and so have
        always been inactive/not supported.

        It's fairly rare for active stations to go inactive, but it does happen,
        and it's best to be prepared for the possibility, particularly if you're
        handling data from hundreds or thousands of locations. Stations can be
        taken down, they can break (and not be fixed in a timely manner), or
        they can be moved to another location and assigned a new ID.
        Unfortunately not even the best "airport" stations managed by
        organizations such as the NWS or UK Met Office are exempt from these
        sorts of problems.

        Short periods of station inactivity should not result in this failure.
        Up to a point, the API will fill in missing data with estimates. It's
        only when a station fails to send any usable data for roughly 10 days or
        more that the API will consider it inactive. (10 being an approximate
        number that is subject to change.)

        It's possible for an inactive station to become active (again) at some
        point in the future. However, if you get this failure for a station,
        you're probably best off finding another nearby station to use as an
        alternative/replacement (e.g. by requesting data using the
        :py:class:`GeographicLocation` of the real-world building of interest).
        If an active station goes inactive, and then later makes a revival,
        there will probably be a gap in its data coverage that will make it
        impractical for use in most forms of degree-day-based analysis until it
        has accumulated more uninterrupted data."""
        return self._testCode('LocationNotSupported')

class SourceDataError(api.FailureError):
    #1 inheritance-diagram:: SourceDataError
    """Indicates a :py:class:`Failure <degreedays.api.Failure>` to generate a
    :py:class:`DataSet` caused by problems with the source temperature data for
    the :py:class:`Location` and :py:class:`Period` requested.

    For a :py:class:`LocationDataRequest` containing specifications for multiple
    sets of data, it is possible for some to succeed and others to fail if they
    are sufficiently different (e.g. covering different periods in time).

    This exception corresponds to any :ref:`failure code <failure-codes>`
    starting with "SourceData".

    You can interrogate the :ref:`isDueToXXX <is-due-to-properties>` properties
    of this exception to find out more about the cause. But do note that it is
    possible for none of those properties to be `True` if a relevant new
    :ref:`failure code <failure-codes>` is added into the API.  Be prepared for
    this in your handling."""
    def __init__(self, failure): # type: (api.Failure) -> None
        api.FailureError.__init__(self, failure)
    @property
    def isDueToSourceDataErrors(self): # type: () -> bool
        """`True` if the requested data could not be generated because of errors
        in the recorded temperature data of the source weather station;
        `False` otherwise.

        Generally speaking, if a request for data from a weather station results
        in this error, it is probably best to find an alternative weather
        station nearby. But a weather station with data errors is not
        necessarily totally useless - it may make a revival at some point in the
        future, and it's possible that data requests covering a different period
        in time will work OK."""
        return self._testCode('SourceDataErrors')
    @property
    def isDueToSourceDataCoverage(self): # type: () -> bool
        """`True` if the requested data could not be generated because the
        source weather station's recorded temperature data did not cover the
        requested period in time; `False` otherwise.

        This will arise if you request data too early (because the weather
        station hasn't yet recorded the necessary temperature readings or they
        haven't yet filtered into our system), or if the weather station didn't
        exist or wasn't recording for the requested period in time."""
        return self._testCode('SourceDataCoverage')
    @property
    def isDueToSourceDataGranularity(self): # type: () -> bool
        """`True` if the requested data could not be generated because the
        source weather station's recorded temperature data was not
        fine-grained/detailed enough; `False` otherwise.

        This will arise if you request detailed time-series data (e.g. hourly
        temperature data) for a station without sufficiently fine-grained
        weather reports."""
        return self._testCode('SourceDataGranularity')

def _checkPercentageEstimated(percentageEstimated): # type: (float) -> float
    if percentageEstimated == 0:
        # returns 0.0 for negative zero and fast-tracks common 0 case
        return 0.0
    private.checkNumeric(percentageEstimated, 'percentageEstimated')
    if percentageEstimated > 100:
        raise ValueError('Invalid percentageEstimated %r: cannot be > 100.'
            % percentageEstimated)
    elif percentageEstimated < 0:
        raise ValueError('Invalid percentageEstimated %r: cannot be < 0')
    return percentageEstimated

class DataValue(_Immutable):
    #1 inheritance-diagram:: DataValue DatedDataValue TimeSeriesDataValue
    """Contains a value (e.g. an HDD or CDD value) and an approximate indication
    of its accuracy."""
    __slots__ = ()
    def __new__(cls, value, percentageEstimated):
        # type: (float, float) -> DataValue
        # Kind of based on example at:
        # http://stackoverflow.com/questions/5953759/
        if cls is DataValue:
            private.checkNumeric(value, 'value')
            if _checkPercentageEstimated(percentageEstimated) > 0:
                return _EstimatedDataValue(value, percentageEstimated)
            else:
                return _SimpleDataValue(value, 0.0)
        else:
            return _Immutable.__new__(cls)
    @property
    def value(self): # type: () -> float
        """The value, which will never be `NaN` or infinity, and, for degree
        days, will always be zero or greater."""
        raise NotImplementedError()
    @property
    def percentageEstimated(self): # type: () -> float
        """A number between 0 and 100 (both inclusive), indicating the extent to
        which the calculated :py:attr:`value` is based on estimated data.

        Generally speaking, a value with a lower percentage-estimated figure is
        likely to be more reliable than one with a higher percentage-estimated
        figure."""
        raise NotImplementedError()
    @staticmethod
    def _check(param, paramName='dataValue'):
        # type: (DataValue, str) -> DataValue
        if not isinstance(param, DataValue):
            raise TypeError(
                private.wrongSupertypeString(param, paramName, DataValue))
        return param

class _SimpleDataValue(DataValue):
    __slots__ = ('__value',)
    # Pass percentageEstimated to make the auto-call of __init__ that occurs
    # after the superclass __new__ method have the right number of arguments.
    # Essentially we need to accept the args that DataValue(...) was called
    # with and the easiest way to do this is to match the signature here (even
    # though we don't need percentageEstimated for this one as it wouldn't be
    # called unless it was zero).
    def __init__(self, value, percentageEstimated):
        # type: (float, float) -> None
        self.__value = value
    @property
    def value(self):
        return self.__value
    @property
    def percentageEstimated(self):
        return 0.0
    def _equalityFields(self):
        return self.__value
    def __str__(self):
        # %g works well for floats. %f adds unnecessary trailing zeroes.
        return '%g' % self.__value
    def __repr__(self):
        return 'DataValue(%g, 0.0)' % self.__value

class _EstimatedDataValue(DataValue):
    __slots__ = ('__value', '__percentageEstimated')
    # As for SimpleDataValue, it's best to match the signature of DataValue.
    def __init__(self, value, percentageEstimated):
        # type: (float, float) -> None
        self.__value = value
        self.__percentageEstimated = percentageEstimated
    @property
    def value(self):
        return self.__value
    @property
    def percentageEstimated(self):
        return self.__percentageEstimated
    def _equalityFields(self):
        return (self.__value, self.__percentageEstimated)
    def __str__(self):
        return ('%g (%g%% estimated)' %
            (self.__value, self.__percentageEstimated))
    def __repr__(self):
        return ('DataValue(%g, %g)' %
                (self.__value, self.__percentageEstimated))

class DatedDataValue(DataValue):
    #1 inheritance-diagram:: DatedDataValue
    """Contains a degree-day value for a specific dated period (a single day or
    a range of days like a specific week, month, or year)."""
    __slots__ = ()
    def __new__(cls, value, percentageEstimated, dayRange):
        # type: (float, float, degreedays.time.DayRange) -> DatedDataValue
        if cls is DatedDataValue:
            private.checkNumeric(value, 'value')
            degreedays.time.DayRange._check(dayRange)
            if dayRange.first == dayRange.last:
                if _checkPercentageEstimated(percentageEstimated) > 0:
                    return _EstimatedSingleDayDatedDataValue(
                        value, percentageEstimated, dayRange)
                else:
                    return _SingleDayDatedDataValue(value, 0.0, dayRange)
            else:
                if _checkPercentageEstimated(percentageEstimated) > 0:
                    return _EstimatedMultiDayDatedDataValue(
                        value, percentageEstimated, dayRange)
                else:
                    return _MultiDayDatedDataValue(value, 0.0, dayRange)
        else:
            # Need to go right up to the class above DataValue, as we don't want
            # to have to match DataValue's args.
            return _Immutable.__new__(cls)
    @property
    def dayRange(self): # type: () -> degreedays.time.DayRange
        """The :py:class:`DayRange` object indicating the period in time that
        this ``DatedDataValue`` covers."""
        raise NotImplementedError()
    @property
    def firstDay(self): # type: () -> datetime.date
        """Returns the first :py:class:`datetime.date` of the period covered by
        this ``DatedDataValue``.

        This is a convenience/performance property that should run faster (or at
        least not slower) than accessing ``.dayRange.first``, since accessing
        the :py:attr:`dayRange` property *may* result in a temporary
        :py:class:`degreedays.time.DayRange` object being created. We say "may"
        because, although at the time of writing it *does* create a temporary
        object, this is an implementation detail that might change in the
        future.

        A large request for data (daily data in particular) can easily result in
        hundreds of thousands of these ``DatedDataValue`` objects, each of which
        occupies memory and typically needs to be used by code that is repeating
        its operations on every single value in a set. So we've tried to design
        ``DatedDataValue`` to minimize memory footprint and enable fast access
        to its properties.

        If all you want is the first day of the range, then this is the optimal
        property to access. If you want the last day of the range, then 
        :py:attr:`lastDay` is the optimal property to access. But if you need
        more information then don't hesitate to access the :py:attr:`dayRange`
        property as the :py:class:`degreedays.time.DayRange` object is
        lightweight and creating it is a very fast operation. Choosing the
        optimal access pattern is very unlikely to make a practical difference
        unless performance is critically important to you and you're iterating
        over large quantities of daily data for which the :py:attr:`dayRange`
        property is largely irrelevant anyway (since for daily data the
        ``DayRange`` would only cover a single day)."""
        return self.dayRange.first
    @property
    def lastDay(self): # type: () -> datetime.date
        """The last :py:class:`datetime.date` of the period covered by this
        ``DatedDataValue``.

        See also: :py:attr:`firstDay`"""
        return self.dayRange.last
    def __repr__(self):
        return ('DatedDataValue(%g, %g, %r)' %
            (self.value, self.percentageEstimated, self.dayRange))
    @staticmethod
    def _check(param, paramName='datedDataValue'):
        # type: (DatedDataValue, str) -> DatedDataValue
        if not isinstance(param, DatedDataValue):
            raise TypeError(private.wrongSupertypeString(
                param, paramName, DatedDataValue))
        return param

class _SingleDayDatedDataValue(DatedDataValue):
    __slots__ = ('__value', '__day')
    def __init__(self, value, percentageEstimated, dayRange):
        # type: (float, float, degreedays.time.DayRange) -> None
        self.__value = value
        self.__day = dayRange.first
    def _equalityFields(self):
        return (self.__value, self.__day)
    @property
    def value(self):
        return self.__value
    @property
    def percentageEstimated(self):
        return 0.0
    @property
    def dayRange(self):
        return degreedays.time.DayRange(self.__day, self.__day)
    @property
    def firstDay(self):
        return self.__day
    @property
    def lastDay(self):
        return self.__day
    def __str__(self):
        return '%s: %g' % (self.__day, self.__value)

class _EstimatedSingleDayDatedDataValue(DatedDataValue):
    __slots__ = ('__value', '__percentageEstimated', '__day')
    def __init__(self, value, percentageEstimated, dayRange):
        # type: (float, float, degreedays.time.DayRange) -> None
        self.__value = value
        self.__percentageEstimated = percentageEstimated
        self.__day = dayRange.first
    def _equalityFields(self):
        return (self.__value, self.__percentageEstimated, self.__day)
    @property
    def value(self):
        return self.__value
    @property
    def percentageEstimated(self):
        return self.__percentageEstimated
    @property
    def dayRange(self):
        return degreedays.time.DayRange(self.__day, self.__day)
    @property
    def firstDay(self):
        return self.__day
    @property
    def lastDay(self):
        return self.__day
    def __str__(self):
        return ('%s: %g (%g%% estimated)' %
            (self.__day, self.__value, self.__percentageEstimated))

class _MultiDayDatedDataValue(DatedDataValue):
    __slots__ = ('__value', '__dayRange')
    def __init__(self, value, percentageEstimated, dayRange):
        # type: (float, float, degreedays.time.DayRange) -> None
        self.__value = value
        self.__dayRange = dayRange
    def _equalityFields(self):
        return (self.__value, self.__dayRange)
    @property
    def value(self):
        return self.__value
    @property
    def percentageEstimated(self):
        return 0.0
    @property
    def dayRange(self):
        return self.__dayRange
    def __str__(self):
        return '%s: %g' % (self.__dayRange, self.__value)

class _EstimatedMultiDayDatedDataValue(DatedDataValue):
    __slots__ = ('__value', '__percentageEstimated', '__dayRange')
    def __init__(self, value, percentageEstimated, dayRange):
        # type: (float, float, degreedays.time.DayRange) -> None
        self.__value = value
        self.__percentageEstimated = percentageEstimated
        self.__dayRange = dayRange
    def _equalityFields(self):
        return (self.__value, self.__percentageEstimated, self.__dayRange)
    @property
    def value(self):
        return self.__value
    @property
    def percentageEstimated(self):
        return self.__percentageEstimated
    @property
    def dayRange(self):
        return self.__dayRange
    def __str__(self):
        return ('%s: %g (%g%% estimated)' %
            (self.__dayRange, self.__value, self.__percentageEstimated))

class TimeSeriesDataValue(DataValue):
    #1 inheritance-diagram:: TimeSeriesDataValue
    """Contains a value (e.g. a temperature value) for a specific point in time,
    and an approximate indication of its accuracy."""
    __slots__ = ()
    def __new__(cls, value, percentageEstimated, datetime):
        # type: (float, float, datetime.datetime) -> TimeSeriesDataValue
        if cls is TimeSeriesDataValue:
            private.checkNumeric(value, 'value')
            private.checkDatetime(datetime, 'datetime')
            if datetime.second > 0 or datetime.microsecond > 0:
                raise ValueError(('We expect the datetime of a TimeSeriesDataValue '
                    'to be specified to the level of minutes only (i.e. no seconds '
                    'or microseconds), but this datetime is %r.') % datetime)
            elif datetime.tzinfo is None:
                raise ValueError(('We expect the datetime of a TimeSeriesDataValue '
                    'to have its tzinfo property set, but this datetime (%r) does '
                    'not.') % datetime)
            if _checkPercentageEstimated(percentageEstimated) > 0:
                return _EstimatedTimeSeriesDataValue(
                    value, percentageEstimated, datetime)
            else:
                return _SimpleTimeSeriesDataValue(value, 0.0, datetime)
        else:
            # Need to go right up to the class above DataValue, as we don't want
            # to have to match DataValue's args.
            return _Immutable.__new__(cls)
    @property
    def datetime(self): # type: () -> datetime.datetime
        """A :py:class:`datetime.datetime` object indicating the
        YYYY-MM-DDThh:mm (i.e. minute precision) date-time of this
        ``TimeSeriesDataValue``, in the local time-zone of the weather station.

        This holds the full detail of the date-time associated with this
        ``TimeSeriesDataValue``, including its time-zone info (accessible via
        the ``tzinfo`` property of the :py:class:`datetime.datetime` object)."""
        raise NotImplementedError()
    def __repr__(self):
        return ('TimeSeriesDataValue(%g, %g, %r)' %
            (self.value, self.percentageEstimated, self.datetime))
    @staticmethod
    def _check(param, paramName='timeSeriesDataValue'):
        # type: (TimeSeriesDataValue, str) -> TimeSeriesDataValue
        if not isinstance(param, TimeSeriesDataValue):
            raise TypeError(private.wrongSupertypeString(
                param, paramName, TimeSeriesDataValue))
        return param

class _SimpleTimeSeriesDataValue(TimeSeriesDataValue):
    __slots__ = ('__value', '__datetime')
    def __init__(self, value, percentageEstimated, datetime):
        # type: (float, float, datetime.datetime) -> None
        self.__value = value
        self.__datetime = datetime
    def _equalityFields(self):
        return (self.__value, self.__datetime)
    @property
    def value(self):
        return self.__value
    @property
    def percentageEstimated(self):
        return 0.0
    @property
    def datetime(self):
        return self.__datetime
    def __str__(self):
        return '%s: %g' % (private.formatDateTime(self.__datetime),
            self.__value)

class _EstimatedTimeSeriesDataValue(TimeSeriesDataValue):
    __slots__ = ('__value', '__percentageEstimated', '__datetime')
    def __init__(self, value, percentageEstimated, datetime):
        # type: (float, float, datetime.datetime) -> None
        self.__value = value
        self.__percentageEstimated = percentageEstimated
        self.__datetime = datetime
    def _equalityFields(self):
        return (self.__value, self.__percentageEstimated, self.__datetime)
    @property
    def value(self):
        return self.__value
    @property
    def percentageEstimated(self):
        return self.__percentageEstimated
    @property
    def datetime(self):
        return self.__datetime
    def __str__(self):
        return ('%s: %g (%g%% estimated)' %
            (private.formatDateTime(self.__datetime), self.__value,
                self.__percentageEstimated))

class DataSet(_Immutable):
    #1 inheritance-diagram:: DataSet DatedDataSet AverageDataSet
    #   TimeSeriesDataSet
    """Contains a set of degree-day data generated to fulfil a
    :py:class:`DataSpec` for a specific :py:class:`Location`."""
    __slots__ = ()
    def __init__(self):
        raise TypeError(
            _ABSTRACT_INIT_RESPONSE % 'DatedDataSet and AverageDataSet')
    @property
    def percentageEstimated(self): # type: () -> float
        """A number between 0 and 100 (both inclusive), indicating the overall
        extent to which this ``DataSet`` is based on estimated data.

        Generally speaking, data with a lower percentage-estimated figure is
        likely to be more reliable than data with a higher percentage-estimated
        figure."""
        raise NotImplementedError()
    @property
    def fullRange(self): # type: () -> degreedays.time.DayRange
        """The :py:class:`degreedays.time.DayRange` object indicating the period
        of time that is covered by this ``DataSet``."""
        raise NotImplementedError()

class DatedDataSet(DataSet):
    #1 inheritance-diagram:: DatedDataSet
    """Contains a set of dated data (e.g. daily/weekly/monthly degree days)
    generated to fulfil a :py:class:`DatedDataSpec` for a specific
    :py:class:`Location`.

    See :py:class:`DatedDataSpec` for example code showing how to fetch a
    ``DatedDataSet`` of degree days from the API.

    See also: :py:class:`AverageDataSet`, :py:class:`TimeSeriesDataSet`"""
    __slots__ = ('__percentageEstimated', '__values', '__isContiguous')
    def __init__(self, percentageEstimated, values):
        # type: (float, Sequence[DatedDataValue]) -> None
        self.__percentageEstimated = _checkPercentageEstimated(
            percentageEstimated)
        # convert values to immutable tuple and check each item within it
        values = private.checkTupleItems(
            tuple(values), DatedDataValue._check, 'values')
        length = len(values)
        if length == 0:
            raise ValueError('Expecting at least one DatedDataValue')
        isContiguous = True
        for i in range(1, length):
            lastDayOfPrevious = values[i - 1].lastDay
            firstDayOfTest = values[i].firstDay
            daysAfter = (firstDayOfTest - lastDayOfPrevious).days
            if daysAfter != 1:
                if daysAfter > 1:
                    isContiguous = False
                else:
                    raise ValueError(('Problem DatedDataValue items at indexes '
                        '%d (%s) and %d (%s): values must be chronological, '
                        'with each one starting after the end of the '
                        'previous.') % ((i - 1), values[i - 1], i, values[i])) 
        self.__values = values
        self.__isContiguous = isContiguous
    def _equalityFields(self):
        return (self.__percentageEstimated, self.__values)
    @property
    def percentageEstimated(self): # type: () -> float
        return self.__percentageEstimated
    @property
    def values(self): # type: () -> Sequence[DatedDataValue]
        """A non-empty chronologically-ordered :py:class:`Sequence` of the
        :py:class:`DatedDataValue` objects that make up this ``DatedDataSet``.
        """
        return self.__values
    @property
    def fullRange(self): # type: () -> degreedays.time.DayRange
        return degreedays.time.DayRange(self.__values[0].firstDay,
            self.__values[-1].lastDay)
    @property
    def isContiguous(self): # type: () -> bool
        """`True` if each contained :py:class:`DatedDataValue` starts the day
        after the previous ``DatedDataValue`` ended (i.e. no gaps); `False`
        otherwise.

        This will always be `True` for daily, weekly, monthly, or yearly data
        returned by the API."""
        return self.__isContiguous
    def __str__(self):
        s = [] # type: list[str]
        s.append('DatedDataSet(')
        s.append(str(len(self.__values)))
        s.append(' value')
        if len(self.__values) != 1:
            s.append('s')
        else:
            # include the value itself.  No need for % estimated as it will be
            # the same as for the whole set.
            s.append(' (%g)' % self.__values[0].value)
        s.append(' covering ')
        s.append(str(self.fullRange))
        if self.__percentageEstimated > 0:
            s.append(', %g%% estimated' % self.__percentageEstimated)
        s.append(')')
        return ''.join(s)
    def __repr__(self):
        return ('DatedDataSet(percentageEstimated=%g, values=%r)' %
            (self.__percentageEstimated, self.__values))
    @staticmethod
    def _check(param, paramName):
        # type: (DatedDataSet, str) -> DatedDataSet
        if type(param) is not DatedDataSet:
            raise TypeError(private.wrongTypeString(
                param, paramName, DatedDataSet))
        return param

class AverageDataSet(DataSet):
    #1 inheritance-diagram:: AverageDataSet
    """Contains a set of average degree-day data generated to fulfil an
    :py:class:`AverageDataSpec` for a specific :py:class:`Location`.

    See :py:class:`AverageDataSpec` for example code showing how to fetch an
    ``AverageDataSet`` of average degree days from the API."""
    __slots__ = ('__firstYear', '__lastYear', '__annualAverage',
            '__monthlyAverages')
    def __init__(self, firstYear, lastYear, annualAverage, monthlyAverages):
        # type: (int, int, DataValue, Sequence[DataValue]) -> None
        self.__firstYear = private.checkInt(firstYear, 'firstYear')
        self.__lastYear = private.checkInt(lastYear, 'lastYear')
        if firstYear > lastYear:
            raise ValueError('firstYear (%s) cannot be greater than lastYear '
                '(%s).' % (firstYear, lastYear))
        self.__annualAverage = DataValue._check(annualAverage, 'annualAverage')
        self.__monthlyAverages = private.checkTupleItems(tuple(monthlyAverages),
            DataValue._check, 'monthlyAverages')
        noMonths = len(self.__monthlyAverages)
        if noMonths != 12:
            raise ValueError('monthlyAverages should contain 12 DataValue '
                'objects, not %i.' %noMonths)
    def _equalityFields(self):
        return (self.__firstYear, self.__lastYear, self.__annualAverage,
            self.__monthlyAverages)
    @property
    def percentageEstimated(self): # type: () -> float
        return self.__annualAverage.percentageEstimated
    @property
    def firstYear(self): # type: () -> int
        """The first year of the continuous set of data that was used to
        calculate the average figures."""
        return self.__firstYear
    @property
    def lastYear(self): # type: () -> int
        """The last year of the continuous set of data that was used to
        calculate the average figures."""
        return self.__lastYear
    @property
    def numberOfYears(self): # type: () -> int
        """The number of years of data that the average figures were calculated
        from (e.g. for 5-year-average data this would return 5)."""
        return self.__lastYear - self.__firstYear + 1
    @property
    def annualAverage(self): # type: () -> DataValue
        """The average annual value."""
        return self.__annualAverage
    def monthlyAverage(self, monthIndexWithJanAs1): # type: (int) -> DataValue
        """The average value for the specified month (e.g. pass 1 for the
        average value for the month of January).

        :param int monthIndexWithJanAs1: a number between 1 (for January) and 12
            (for December).
        :raises TypeError: if `monthIndexWithJanAs1` is not an `int`.
        :raises IndexError: if `monthIndexWithJanAs1` is less than 1 or greater
            than 12."""
        private.checkInt(monthIndexWithJanAs1, 'monthIndexWithJanAs1')
        if monthIndexWithJanAs1 < 1 or monthIndexWithJanAs1 > 12:
            raise IndexError('Invalid month index (%i) - it must be between 1 '\
                    'and 12 (inclusive).' % monthIndexWithJanAs1)
        return self.__monthlyAverages[monthIndexWithJanAs1 - 1]
    @property
    def fullRange(self): # type: () -> degreedays.time.DayRange
        return degreedays.time.DayRange(
            datetime.date(self.__firstYear, 1, 1),
            datetime.date(self.__lastYear, 12, 31))
    def __str__(self):
        return ('AverageDataSet(%d to %d, annualAverage = %s)' %
            (self.__firstYear, self.__lastYear, self.__annualAverage))
    def __repr__(self):
        return ('AverageDataSet(firstYear=%d, lastYear=%d, annualAverage=%r, '
            'monthlyAverages=%r)' %
            (self.__firstYear, self.__lastYear, self.__annualAverage,
                self.__monthlyAverages))

class TimeSeriesDataSet(DataSet):
    #1 inheritance-diagram:: TimeSeriesDataSet
    """Contains a set of time-series data (e.g. hourly temperature data)
    generated to fulfil a :py:class:`TimeSeriesDataSpec` for a specific
    :py:class:`Location`.

    See :py:class:`TimeSeriesDataSpec` for example code showing how to get a
    ``TimeSeriesDataSet`` of hourly temperature data from the API."""
    __slots__ = ('__percentageEstimated', '__values', '__dates',
        '__firstOfDayIndexes')
    def __getIllegalTimeMessage(self, values, laterIndex, afterStart):
        # type: (tuple[TimeSeriesDataValue, ...], int, str) -> str
        return ('Problem TimeSeriesDataValue items at index %d (with a '
            'datetime of %s) and index %d (with a datetime of %s).  %s') % \
            (laterIndex - 1,
            private.formatDateTime(values[laterIndex - 1].datetime),
            laterIndex, private.formatDateTime(values[laterIndex].datetime),
            afterStart)
    def __init__(self, percentageEstimated, values):
        # type: (float, Sequence[TimeSeriesDataValue]) -> None
        self.__percentageEstimated = _checkPercentageEstimated(percentageEstimated)
        # convert values to immutable tuple and check each item within it
        values = private.checkTupleItems(
            tuple(values), TimeSeriesDataValue._check, 'values')
        length = len(values)
        if length == 0:
            raise ValueError('Expecting at least one TimeSeriesDataValue')
        lastDateTime = values[0].datetime
        lastDate = lastDateTime.date()
        dates = [lastDate]
        firstOfDayIndexes = [0]
        for i in range(1, len(values)):
            dt = values[i].datetime
            if dt <= lastDateTime:
                raise ValueError(self.__getIllegalTimeMessage(values, i,
                    ('It is expected that values are chronological, with each '
                    'one coming after the last (when their timezones are taken '
                    'into account).')))
            # Ugly comparing all 3 fields but we don't really want to call
            # dt.date() and create a new object on every iteration.
            if dt.day != lastDate.day or dt.month != lastDate.month or \
                    dt.year != lastDate.year:
                dtDate = dt.date()
                if dtDate < lastDate:
                    raise ValueError(self.__getIllegalTimeMessage(values, i,
                        ('The YYYY-MM-DD date part of the datetimes must '
                        'never go backwards.')))
                lastDate = dtDate
                dates.append(lastDate)
                firstOfDayIndexes.append(i)
            lastDateTime = dt
        self.__values = values
        self.__dates = tuple(dates)
        self.__firstOfDayIndexes = tuple(firstOfDayIndexes)
    def _equalityFields(self):
        return (self.__percentageEstimated, self.__values)
    @property
    def percentageEstimated(self): # type: () -> float
        return self.__percentageEstimated
    @property
    def values(self): # type: () -> Sequence[TimeSeriesDataValue]
        """A non-empty chronologically-ordered :py:class:`Sequence` of the
        :py:class:`TimeSeriesDataValue` objects that make up this
        ``TimeSeriesDataSet``."""
        return self.__values
    @property
    def fullRange(self): # type: () -> degreedays.time.DayRange
        return degreedays.time.DayRange(self.__values[0].datetime.date(),
            self.__values[-1].datetime.date())
    def getValuesWithin(self,
            dateOrDayRange # type: (datetime.date | degreedays.time.DayRange)
            ): # type: (...) -> Sequence[TimeSeriesDataValue]
        """Returns a possibly-empty chronologically-ordered :py:class:`Sequence`
        of the :py:class:`TimeSeriesDataValue` objects from this
        ``TimeSeriesDataSet`` that fall within the specified `dateOrDayRange`.

        :param datetime.date | degreedays.time.DayRange dayRange: the date or
            day range of interest.
        :raises TypeError: if `dateOrDayRange` is not a
            :py:class:`datetime.date` or :py:class:`degreedays.time.DayRange`.
        """
        if type(dateOrDayRange) is datetime.date:
            dayRange = degreedays.time.DayRange.singleDay(dateOrDayRange)
        elif type(dateOrDayRange) is degreedays.time.DayRange:
            dayRange = dateOrDayRange
        else:
            raise TypeError(('dateOrDayRange should be of type datetime.date '
                'or degreedays.time.DayRange, not %s.') %
                private.fullNameOfClass(dateOrDayRange.__class__))
        # Find earliest date that is later than or equal to startDate
        startDateIndex = bisect.bisect_left(self.__dates, dayRange.first)
        if startDateIndex == len(self.__dates) or not dayRange.contains(
                self.__dates[startDateIndex]):
            return ()
        startValueIndex = self.__firstOfDayIndexes[startDateIndex]
        # find earliest date later than endDate
        endDateIndex = bisect.bisect_right(
            self.__dates, dayRange.last, startDateIndex)
        if endDateIndex == len(self.__dates):
            endValueIndexExclusive = len(self.__values)
        else:
            endValueIndexExclusive = self.__firstOfDayIndexes[endDateIndex]
        return self.__values[startValueIndex:endValueIndexExclusive]
    def __str__(self):
        s = [] # type: list[str]
        s.append('TimeSeriesDataSet(')
        s.append(str(len(self.__values)))
        s.append(' values covering ')
        first = self.__values[0]
        last = self.__values[-1]
        s.append(private.formatDateTime(first.datetime))
        s.append(' (%g)' % first.value)
        s.append(' to ')
        s.append(private.formatDateTime(last.datetime))
        s.append(' (%g)' % last.value)
        if self.__percentageEstimated > 0:
            s.append(', %g%% estimated' % self.__percentageEstimated)
        s.append(')')
        return ''.join(s)
    def __repr__(self):
        return ('TimeSeriesDataSet(percentageEstimated=%g, values=%r)' %
            (self.__percentageEstimated, self.__values))

class DataSets(object):
    """Contains all sets of data generated to fulfil the :py:class:`DataSpecs`
    for a specific :py:class:`Location`.

    .. _get-data-set:

    How to get ``DataSet`` objects out of a ``DataSets``
    ----------------------------------------------------
    You need to keep hold of the :py:class:`DataSpec` objects that you specified
    in your request.  Then you can access the :py:class:`DataSet` object that
    corresponds to each ``DataSpec`` like so::

        datedDataSet = dataSets[yourDatedDataSpec]
        averageDataSet = dataSets[yourAverageDataSpec]
        timeSeriesDataSet = dataSets[yourTimeSeriesDataSpec]

    In rare cases you might also want to access the :py:class:`DataSet` objects
    using the :ref:`keys <keys>` that were set in the :py:class:`DataSpecs`
    sent with the :py:class:`LocationDataRequest`, like ``dataSets[stringKey]``.

    Watch out for ``SourceDataError``
    ---------------------------------
    If the API servers were unable to generate a particular :py:class:`DataSet`
    (e.g. because the weather station did not have the weather-data records
    necessary to generate data to match your ``DataSpec``), you'll get a
    :py:class:`SourceDataError` when you try to get the ``DataSet`` object out
    of the ``DataSets``.  For example::

        try:
            dataSet = dataSets[yourDataSpec]
        except SourceDataError as e:
            print('Failed to get data for', yourDataSpec, e)
    """
    __slots__ = ('__dataSpecsOrNone', '__results', '__cachedHashCode')
    def __init__(self, dataSpecsOrNone, stringKeyToResultDict):
        # type: (DataSpecs | None, Mapping[str, DataSet | api.Failure]) -> None
        dictCopy = private.checkMappingAndReturnDictCopy(stringKeyToResultDict,
            'stringKeyToResultDict')
        if dataSpecsOrNone is not None:
            DataSpecs._check(dataSpecsOrNone, 'dataSpecsOrNone')
            if len(dataSpecsOrNone) != len(dictCopy):
                raise ValueError('Different size of dataSpecsOrNone (%s) '
                    'and stringKeyToResultDict (%s)' %
                    (len(dataSpecsOrNone), len(dictCopy)))
        for key, value in private.getDictItemsIterable(dictCopy):
            if dataSpecsOrNone is not None:
                if not dataSpecsOrNone._containsKey(key):
                    raise ValueError('stringKeyToResultDict contains a key %r '
                        'that is not in the corresponding DataSpecs from the '
                        'request' % key)
            elif not private.isString(key):
                raise TypeError('stringKeyToResultDict contains non-string '
                    'key of type %s' % private.fullNameOfClass(key.__class__))
            else:
                _checkDataSpecStringKey(key)
            if not isinstance(value, (DataSet, api.Failure)):
                raise TypeError('stringKeyToResultDict contains a value that '
                    'is neither a subclass of DataSpec nor a Failure; it has '
                    'type %s' % private.fullNameOfClass(value.__class__))
        self.__dataSpecsOrNone = dataSpecsOrNone
        self.__results = dictCopy
        self.__cachedHashCode = 0
    @overload
    def __getitem__(self, dataSpecObjectOrStringKey):
        # type: (DatedDataSpec) -> DatedDataSet
        pass # use pass instead of ... cos older versions of Python choke on ...
    @overload
    def __getitem__(self, dataSpecObjectOrStringKey):
        # type: (AverageDataSpec) -> AverageDataSet
        pass
    @overload
    def __getitem__(self, dataSpecObjectOrStringKey):
        # type: (TimeSeriesDataSpec) -> TimeSeriesDataSet
        pass
    @overload
    def __getitem__(self, dataSpecObjectOrStringKey):
        # type: (DataSpec) -> DataSet
        pass
    @overload
    def __getitem__(self, dataSpecObjectOrStringKey):
        # type: (str) -> DataSet
        pass
    def __getitem__(self, dataSpecObjectOrStringKey):
        # type: (DataSpec | str) -> DataSet
        if private.isString(dataSpecObjectOrStringKey):
            # Unusual case, but useful for testing
            stringKey = private.castStr(dataSpecObjectOrStringKey) # type: str
        elif isinstance(dataSpecObjectOrStringKey, DataSpec):
            if self.__dataSpecsOrNone is None:
                # http://stackoverflow.com/questions/1701199/ says ValueError
                # is the equivalent to IllegalStateException.
                raise ValueError("You can only use DataSpec objects to access "
                    "the corresponding DataSet objects if the DataSets object "
                    "has internal access to the original DataSpecs from the "
                    "request (which maps the string keys in the XML response "
                    "to the DataSpec objects used to request them). This "
                    "framework would usually ensure that the DataSets object "
                    "was created with access to the relevant DataSpecs object, "
                    "but are you perhaps parsing the XML response yourself? "
                    "If so, please ensure that your implementation passes the "
                    "DataSpecs object from the request into the DataSets "
                    "object, or do all your interrogation of this object using "
                    "string keys.")
            stringKey = self.__dataSpecsOrNone.getKey(dataSpecObjectOrStringKey)
        else:
            raise TypeError('Expecting a DataSpec object from the request '
                '(the usual way to use this), or a string key (less common, '
                'but occasionally useful for testing or debugging).  Instead, '
                'got %r' % dataSpecObjectOrStringKey)
        # Following could throw KeyError
        result = self.__results[stringKey]
        if isinstance(result, api.Failure):
            raise SourceDataError(result)
        return result
    def __eq__(self, other): # type: (object) -> bool
        if type(other) is not DataSets:
            return False
        if self.__dataSpecsOrNone is None:
            if other.__dataSpecsOrNone is not None:
                return False
            # need to use keys in comparison...  Which makes it simple.
            return self.__results == other.__results
        elif other.__dataSpecsOrNone is None:
            return False
        elif self.__dataSpecsOrNone != other.__dataSpecsOrNone:
            return False
        return self.__dataSpecsOrNone._dataSetsEquals(self.__results,
            other.__dataSpecsOrNone, other.__results)
    def __ne__(self, other): # type: (object) -> bool
        return not (self == other)
    def __hash__(self):
        # We cache the hash code, like in Java.  This should be thread safe,
        # like in Java, as reading or writing a single instance attribute is
        # supposed to be thread safe:
        # http://effbot.org/zone/thread-synchronization.htm
        # Assuming that's right, the worst that could happen with below is that
        # the hash code is calculated multiple times. But we should be confident
        # that this method will always return the same value.
        hashCode = self.__cachedHashCode
        if hashCode == 0:
            if self.__dataSpecsOrNone is None:
                # started out making a frozenset of the values and getting the
                # hash of that.  But actually using our own method should be
                # faster as we only need to iterate over the values instead of
                # copying them and so on.  Also a frozenset would remove
                # duplicates which would make hash collisions more likely.
                hashCode = private.getDictValuesHash(self.__results)
            else:
                hashCode = self.__dataSpecsOrNone._dataSetsHashCode(
                    self.__results)
            self.__cachedHashCode = hashCode
        return hashCode
    def __str__(self):
        s = [] # type: list[str]
        s.append('DataSets(')
        noDated = 0
        noAverage = 0
        noTimeSeries = 0
        noFailures = 0
        lastDatedSet = None
        lastAverageSet = None
        lastTimeSeriesSet = None
        hasMultipleDifferentFailureCodes = False
        singleFailureCode = None
        for r in private.getDictValuesIterable(self.__results):
            if isinstance(r, api.Failure):
                noFailures += 1
                if not hasMultipleDifferentFailureCodes:
                    if singleFailureCode is None:
                        singleFailureCode = r.code
                    elif singleFailureCode != r.code:
                        hasMultipleDifferentFailureCodes = True
            else:
                if isinstance(r, DatedDataSet):
                    noDated += 1
                    lastDatedSet = r
                elif isinstance(r, AverageDataSet):
                    noAverage += 1
                    lastAverageSet = r
                else:
                    noTimeSeries += 1
                    lastTimeSeriesSet = r
        if noDated > 0:
            if noDated == 1:
                s.append(str(lastDatedSet))
            else:
                s.append('%d dated' % noDated)
            if noAverage > 0 or noTimeSeries > 0 or noFailures > 0:
                s.append(', ')
        if noAverage > 0:
            if noAverage == 1:
                s.append(str(lastAverageSet))
            else:
                s.append('%d average' % noAverage)
            if noTimeSeries > 0 or noFailures > 0:
                s.append(', ')
        if noTimeSeries > 0:
            if noTimeSeries == 1:
                s.append(str(lastTimeSeriesSet))
            else:
                s.append('%d time series' % noTimeSeries)
            if noFailures > 0:
                s.append(', ')
        if noFailures > 0:
            s.append(str(noFailures))
            if not hasMultipleDifferentFailureCodes:
                s.append(' ' + private.castNotNone(singleFailureCode))
            s.append(' failure')
            if noFailures > 1:
                s.append('s')
        s.append(')')
        return ''.join(s)
    def __repr__(self):
        s = [] # type: list[str]
        for key in self.__results.keys():
            s.append("'%s': %r" % (key, self.__results[key]))
        s.sort() # As we do for DataSpecs
        return 'DataSets(%r, {%s})' % (self.__dataSpecsOrNone, ', '.join(s))
    @staticmethod
    def _check(param, paramName='dataSets'):
        # type: (DataSets, str) -> DataSets
        if type(param) is not DataSets:
            raise TypeError(private.wrongTypeString(param, paramName, DataSets))
        return param

class Station(_Immutable):
    """Contains basic information about a weather station."""
    __slots__ = ('__id', '__longLat', '__elevation', '__displayName')
    # Python has an id function, but popular opinion seems to be that it's fine
    # for an object to have an id attribute:
    # http://stackoverflow.com/questions/3497883/
    def __init__(self, id, longLat, elevation, displayName):
        # type: (str, degreedays.geo.LongLat, degreedays.geo.Distance, str) -> None
        self.__id = private.checkStationId(id, False)
        self.__longLat = degreedays.geo.LongLat._check(longLat)
        self.__elevation = degreedays.geo.Distance._check(elevation, 'elevation')
        self.__displayName = private.checkString(displayName, 'displayName')
    def _equalityFields(self):
        return (self.__id, self.__longLat, self.__elevation, self.__displayName)
    def __repr__(self):
        return ("Station('%s', %r, %r, '%s')" %
            (self.__id, self.__longLat, self.__elevation, self.__displayName))
    @property
    def id(self): # type: () -> str
        """The canonical ID of the weather station. (See
        :py:attr:`LocationDataResponse.stationId` for an explanation of what
        "canonical" means in this context.)
        
        The ID can be used to request data from this station."""
        return self.__id
    @property
    def longLat(self): # type: () -> degreedays.geo.LongLat
        """The longitude/latitude location of the weather station.

        Note that a weather station's recorded location might not be a
        particularly accurate representation of its real-world location. Many
        stations do have recorded longitude/latitude locations that are accurate
        to within a few metres, but there are some that are out by as much as a
        kilometer or so.  This is worth bearing in mind when you're calculating
        the distances between locations.

        Note also that the recorded location of weather stations will often
        change over time as the underlying data sources are updated with more
        accurate measurements."""
        return self.__longLat
    @property
    def elevation(self): # type: () -> degreedays.geo.Distance
        """The elevation of the weather station. The
        :py:class:`degreedays.geo.Distance` object returned can easily be
        converted into units of your choice (typically metres or feet for an
        elevation).

        Note that the reliability of these measurements is variable. Note also
        that they may change over time as the underlying data sources are
        updated with more accurate measurements."""
        return self.__elevation
    @property
    def displayName(self): # type: () -> str
        """A string representing the name of the weather station.

        The display name should not include the :py:attr:`id`, the
        :py:attr:`longLat` or the :py:attr:`elevation`.  So, for displaying the
        name of a station in a UI, at a minimum you'll probably want to do
        something like::

            station.id + ': ' + station.displayName

        You might also want to display the longitude/latitude and elevation too.

        We'd love to be able to break the details within this name down further
        (e.g. offering separate fields for city, state, and country)... But the
        recorded details for weather-station names are generally too unreliable
        for this to make sense. Fields are often misspelled, mixed up (e.g. the
        state might have been entered into the city field), and required fields
        like country are often missing. And there's little consistency in the
        naming (e.g. United Kingdom, Great Britain, GB, UK etc.). This,
        unfortunately, is a limitation of the original data sources - it's
        typical for the IDs to be monitored and controlled closely, but it's
        rare for the names to receive the same level of attention.

        Please be aware that a weather station's display name may change over
        time, both in content and format. We strongly suggest that you don't try
        to parse these names. But please do let us know if there's something in
        particular that you need access to."""
        return self.__displayName
    @staticmethod
    def _check(param, paramName='station'):
        # type: (Station, str) -> Station
        if type(param) is not Station:
            raise TypeError(private.wrongTypeString(param, paramName, Station))
        return param

class Source(_Immutable):
    """Contains basic information about a source of data that was used to
    satisfy a request.

    On the surface this appears very similar to the :py:class:`Station` object
    that it contains, but there is a key difference: the information contained
    in a ``Source`` is specifically relevant to a *particular* request for data,
    whilst the :py:class:`Station` is independent of that. For example, the
    ``Source`` contains the :py:attr:`distanceFromTarget`, which is the distance
    of the :py:class:`Station` from the target location that was specified in
    the request."""
    __slots__ = ('__station', '__distanceFromTarget')
    def __init__(self, station, distanceFromTarget):
        # type: (Station, degreedays.geo.Distance) -> None
        self.__station = Station._check(station)
        self.__distanceFromTarget = degreedays.geo.Distance._check(
            distanceFromTarget, 'distanceFromTarget')
    def _equalityFields(self):
        return (self.__station, self.__distanceFromTarget)
    def __repr__(self):
        return 'Source(%r, %r)' % (self.__station, self.__distanceFromTarget)
    @property
    def station(self): # type: () -> Station
        """The :py:class:`Station` that this source represents."""
        return self.__station
    @property
    def distanceFromTarget(self): # type: () -> degreedays.geo.Distance
        """The distance of the :py:attr:`station` from the target location that
        was specified in the original request for data."""
        return self.__distanceFromTarget
    @staticmethod
    def _check(param, paramName='source'): # type: (Source, str) -> Source
        if type(param) is not Source:
            raise TypeError(private.wrongTypeString(param, paramName, Source))
        return param

def _getLocationResponseStringStart(response):
    # type: (LocationDataResponse | LocationInfoResponse | RegressionResponse) -> list[str]
    s = [] # type: list[str]
    s.append(type(response).__name__)
    s.append('(')
    s.append(response.stationId)
    if len(response.sources) > 1:
        s.append(', from %d sources' % len(response.sources))
    s.append(', target %s' % response.targetLongLat)
    return s

class LocationDataResponse(api.Response):
    #1 inheritance-diagram:: LocationDataResponse
    """Contains the data generated to fulfil a :py:class:`LocationDataRequest`.

    See :py:meth:`DataApi.getLocationData(locationDataRequest)
    <DataApi.getLocationData>` for more info and code samples."""
    __slots__ = ('__metadata', '__stationId', '__targetLongLat', '__sources',
        '__dataSets')
    def __init__(self,
            metadata, # type: api.ResponseMetadata
            stationId, # type: str
            targetLongLat, # type: degreedays.geo.LongLat
            sources, # type: Sequence[Source]
            dataSets # type: DataSets
            ): # type: (...) -> None
        self.__metadata = api.ResponseMetadata._check(metadata, 'metadata')
        self.__stationId = private.checkStationId(stationId, False)
        self.__targetLongLat = degreedays.geo.LongLat._check(
            targetLongLat, 'targetLongLat')
        self.__sources = private.checkTupleItems(
            tuple(sources), Source._check, 'sources')
        self.__dataSets = DataSets._check(dataSets)
    def _equalityFields(self):
        # metadata isn't included in equality check.
        return (self.__stationId, self.__targetLongLat, self.__sources,
            self.__dataSets)
    def __str__(self):
        s = _getLocationResponseStringStart(self)
        s.append(', %s)' % self.__dataSets)
        return ''.join(s)
    def __repr__(self):
        return ("LocationDataResponse(%r, '%s', %r, %r, %r)" %
            (self.__metadata, self.__stationId, self.__targetLongLat,
                self.__sources, self.__dataSets))
    @property
    def metadata(self):
        return self.__metadata
    @property
    def stationId(self): # type: () -> str
        """The non-empty canonical ID of the weather station or combination of
        weather stations that were used to calculate the returned data.

        If the :py:class:`Location` in the :py:class:`LocationDataRequest` was a
        :py:class:`StationIdLocation
        <degreedays.api.data.impl.StationIdLocation>` (created via
        :py:meth:`Location.stationId`), this method will simply return the
        canonical form of that weather station's ID. We say "canonical" because
        it's possible for a station ID to be expressed in more than one way,
        like upper case or lower case. The canonical form of the station ID is
        the form that you should display in a UI or store in a database if
        appropriate.

        If the :py:class:`Location` in the :py:class:`LocationDataRequest` was a
        :py:class:`GeographicLocation`, then:

        * If the data was calculated using a single station (the usual case),
          this method will return the canonical form of that station's ID.
        * If the data was calculated using multiple stations (something that the
          API might optionally start doing at some point in the future), this
          method will return the ID of a "virtual station" that represents the
          specific combination of weather stations used.

        Either way, the station ID returned by this method can be used to fetch
        more data from the same station(s) that were used to generate the data
        in this response. For example, you might want to request data using a
        :py:class:`GeographicLocation` initially, and then use the returned
        station ID to fetch updates each day, week, or month going forward."""
        return self.__stationId
    @property
    def targetLongLat(self): # type: () -> degreedays.geo.LongLat
        """The :py:class:`degreedays.geo.LongLat` object that specifies the
        geographic position of the :py:class:`Location` from the
        :py:class:`LocationDataRequest` that led to this response.

        If the :py:class:`Location` from the request was a
        :py:class:`PostalCodeLocation
        <degreedays.api.data.impl.PostalCodeLocation>` (created via
        :py:meth:`Location.postalCode`), this will be the ``LongLat`` that the
        API determined to be the central point of that postal code.

        If the :py:class:`Location` from the request was a
        :py:class:`StationIdLocation
        <degreedays.api.data.impl.StationIdLocation>` (created via
        :py:meth:`Location.stationId`), this will be the ``LongLat`` of that
        station (also accessible through :py:attr:`sources`).

        If the :py:class:`Location` from the request was a
        :py:class:`LongLatLocation
        <degreedays.api.data.impl.LongLatLocation>` (created via
        :py:meth:`Location.longLat`), this will simply be the ``LongLat`` that
        was originally specified. (Bear in mind that the longitude and latitude
        may have been rounded slightly between the request and the response.
        Such rounding would only introduce very small differences that would be
        insignificant as far as the real-world position is concerned, but it's
        worth bearing this in mind in case you are comparing for equality the
        returned ``LongLat`` with the ``LongLat`` from the request. The two
        positions will be close, but they might not be equal.)"""
        return self.__targetLongLat
    @property
    def sources(self): # type: () -> Sequence[Source]
        """The non-empty :py:class:`Sequence` of source(s) (essentially weather
        stations) that were used to generate the data in this response.

        At the time of writing there will only be one source for any given
        response (so ``sources[0]``) is the way to get it)... But at some point
        we might start combining data from multiple sources to satisfy requests
        for data from :py:class:`GeographicLocation` types. If we do add this
        feature, it will be optional, and disabled by default, so the behaviour
        of your system won't change unless you want it to."""
        return self.__sources
    @property
    def dataSets(self): # type: () -> DataSets
        """The :py:class:`DataSets` object containing the sets of data generated
        to fulfil the :py:class:`DataSpecs` from the
        :py:class:`LocationDataRequest` that led to this response."""
        return self.__dataSets

class LocationInfoResponse(api.Response):
    #1 inheritance-diagram:: LocationInfoResponse
    """Contains the location/station-related info returned in response to a
    :py:class:`LocationInfoRequest`.

    This mirrors :py:class:`LocationDataResponse`, except it doesn't actually
    contain any data (i.e. no :py:class:`DataSets`).

    See :py:meth:`DataApi.getLocationInfo(locationInfoRequest)
    <DataApi.getLocationInfo>` for more info and code samples."""
    __slots__ = ('__metadata', '__stationId', '__targetLongLat', '__sources')
    def __init__(self,
            metadata, # type: api.ResponseMetadata
            stationId, # type: str
            targetLongLat, # type: degreedays.geo.LongLat
            sources # type: Sequence[Source]
            ): # type: (...) -> None
        self.__metadata =  api.ResponseMetadata._check(metadata, 'metadata')
        self.__stationId = private.checkStationId(stationId, False)
        self.__targetLongLat = degreedays.geo.LongLat._check(
            targetLongLat, 'targetLongLat')
        self.__sources = private.checkTupleItems(
            tuple(sources), Source._check, 'sources')
    def _equalityFields(self):
        # metadata isn't included in equality check.
        return (self.__stationId, self.__targetLongLat, self.__sources)
    def __str__(self):
        s = _getLocationResponseStringStart(self)
        s.append(')')
        return ''.join(s)
    def __repr__(self):
        return ("LocationInfoResponse(%r, '%s', %r, %r)" %
            (self.__metadata, self.__stationId, self.__targetLongLat,
                self.__sources))
    @property
    def metadata(self):
        return self.__metadata
    @property
    def stationId(self): # type: () -> str
        """The non-empty canonical ID of the weather station or combination of
        weather stations that would be used to generate data for an equivalent
        :py:class:`LocationDataResponse`.

        If the :py:class:`Location` in the :py:class:`LocationInfoRequest` was a
        :py:class:`StationIdLocation
        <degreedays.api.data.impl.StationIdLocation>` (created via
        :py:meth:`Location.stationId`), this method will simply return the
        canonical form of that weather station's ID. We say "canonical" because
        it's possible for a station ID to be expressed in more than one way,
        like upper case or lower case. The canonical form of the station ID is
        the form that you should display in a UI or store in a database if
        appropriate.

        If the :py:class:`Location` in the :py:class:`LocationDataRequest` was a
        :py:class:`GeographicLocation`, then:

        * If the data for an equivalent :py:class:`LocationDataResponse` would
          be calculated using a single station (the usual case), this method
          will return the canonical form of that station's ID.
        * If the data for an equivalent :py:class:`LocationDataResponse` would
          be calculated using multiple stations (something that the
          API might optionally start doing at some point in the future), this
          method will return the ID of a "virtual station" that represents the
          specific combination of weather stations used.

        Either way, the station ID returned by this method can be used to fetch
        data from the same station(s) that would have been used to generate data
        in response to an equivalent :py:class:`LocationDataRequest`. Typically
        you would use this to get the station ID to best represent a
        :py:class:`GeographicLocation`, and then use that ID in each
        :py:class:`LocationDataRequest` for that location going forward."""
        return self.__stationId
    @property
    def targetLongLat(self): # type: () -> degreedays.geo.LongLat
        """The :py:class:`degreedays.geo.LongLat` object that specifies the
        geographic position of the :py:class:`Location` from the
        :py:class:`LocationInfoRequest` that led to this response.

        If the :py:class:`Location` from the request was a
        :py:class:`PostalCodeLocation
        <degreedays.api.data.impl.PostalCodeLocation>` (created via
        :py:meth:`Location.postalCode`), this will be the ``LongLat`` that the
        API determined to be the central point of that postal code.

        If the :py:class:`Location` from the request was a
        :py:class:`StationIdLocation
        <degreedays.api.data.impl.StationIdLocation>` (created via
        :py:meth:`Location.stationId`), this will be the ``LongLat`` of that
        station (also accessible through :py:attr:`sources`).

        If the :py:class:`Location` from the request was a
        :py:class:`LongLatLocation
        <degreedays.api.data.impl.LongLatLocation>` (created via
        :py:meth:`Location.longLat`), this will simply be the ``LongLat`` that
        was originally specified. (Bear in mind that the longitude and latitude
        may have been rounded slightly between the request and the response.
        Such rounding would only introduce very small differences that would be
        insignificant as far as the real-world position is concerned, but it's
        worth bearing this in mind in case you are comparing for equality the
        returned ``LongLat`` with the ``LongLat`` from the request. The two
        positions will be close, but they might not be equal.)"""
        return self.__targetLongLat
    @property
    def sources(self): # type: () -> Sequence[Source]
        """The non-empty :py:class:`Sequence` of source(s) (essentially weather
        stations) that would be used to generate data for an equivalent
        :py:class:`LocationDataResponse`.

        At the time of writing there will only be one source for any given
        response (so ``sources[0]``) is the way to get it)... But at some point
        we might start combining data from multiple sources to satisfy requests
        for data from :py:class:`GeographicLocation` types. If we do add this
        feature, it will be optional, and disabled by default, so the behaviour
        of your system won't change unless you want it to."""
        return self.__sources


class DataApi(object):
    """Provides easy, type-safe access to the API's data-related operations.

    **To get a** ``DataApi`` **object and use it**, create a
    :py:class:`degreedays.api.DegreeDaysApi` object, get the ``DataApi``
    object from that, then call the method you want.  For example, to send a
    :py:class:`LocationDataRequest` to the API and get a
    :py:class:`LocationDataResponse` back::

        api = DegreeDaysApi.fromKeys(
                AccountKey(yourStringAccountKey),
                SecurityKey(yourStringSecurityKey))
        response = api.dataApi.getLocationData(yourLocationDataRequest)

    See :py:meth:`getLocationData(locationDataRequest) <getLocationData>` and
    :py:meth:`getLocationInfo(locationInfoRequest) <getLocationInfo>` for much
    more info and sample code."""
    def __init__(self, requestProcessor):
        """:meta private:"""
        self.__requestProcessor = requestProcessor
    def __checkAndGet(self, request, expectedResponseType):
        # type: (api.Request, type[_RES]) -> _RES
        response = self.__requestProcessor.process(request)
        if isinstance(response, expectedResponseType):
            return response
        elif isinstance(response, api.FailureResponse):
            code = response.failure.code
            if code.startswith('Location'):
                raise LocationError(response)
            # for general exceptions
            raise api.RequestFailureError._create(response)
        else:
            raise ValueError('For a request of type %r, the RequestProcessor '
                'should return a response of type %r or a FailureResponse, not '
                '%r' % (type(request), expectedResponseType, type(response)))
    def getLocationData(self, locationDataRequest):
        # type: (LocationDataRequest) -> LocationDataResponse
        """Sends your request for data (for a specified location) to the API
        servers, returning a response containing data you requested, or throwing
        an appropriate subclass of :py:class:`degreedays.api.DegreeDaysApiError`
        if something goes wrong.

        :param LocationDataRequest locationDataRequest: specifies the data you
            want and the location you want it for.
        :return: :py:class:`LocationDataResponse` containing the data you
            requested or as much of it as was available for the location you
            specified (given the rules explained further below).
        :raises LocationError: if the request fails because of problems relating
            to the specified :py:class:`Location`.
        :raises ServiceError: if the request fails because of a problem with the
            API service (sorry!).
        :raises RateLimitError: if you hit the
            :py:class:`degreedays.api.RateLimit` for your account's plan, and
            need to wait a little while before it's reset.
        :raises InvalidRequestError: if the request that is sent to the API
            servers is invalid (e.g. if it is authenticated with invalid
            :ref:`API access keys <access-keys>`).
        :raises TransportError: if there's a problem sending the request to
            the API servers, or a problem getting the API's response back.
        :raises DegreeDaysApiError: **the superclass of all the exceptions
            listed above**.
        :raises TypeError: if `locationDataRequest` is not a
            :py:class:`LocationDataRequest` object.
        
        Sample ``LocationDataRequest``/``LocationDataResponse`` code
        ------------------------------------------------------------
        Here's a simple example showing how to fetch monthly
        65°F-base-temperature heating degree days, covering the 12 months of
        2024, for an automatically-selected weather station near US zip code
        02633 (which is on Cape Cod so you can use the `free test API account
        <https://www.degreedays.net/api/test>`__).  The HDD figures are output
        to the command line::

            api = DegreeDaysApi.fromKeys(
                    AccountKey('test-test-test'),
                    SecurityKey('test-test-test-test-test-test-test-test-test-test-test-test-test'))
            dayRange = degreedays.time.DayRange(
                    datetime.date(2024, 1, 1), datetime.date(2024, 12, 31))
            hddSpec = DataSpec.dated(
                    Calculation.heatingDegreeDays(Temperature.fahrenheit(65)),
                    DatedBreakdown.monthly(Period.dayRange(dayRange)))
            request = LocationDataRequest(
                    Location.postalCode('02532', 'US'),
                    DataSpecs(hddSpec))
            response = api.dataApi.getLocationData(request)
            hddData = response.dataSets[hddSpec]
            for v in hddData.values:
                print('%s: %g' % (v.firstDay, v.value))

        And here is a more complex example that fetches HDD, CDD, and
        hourly temperature data, covering just the latest available day, for a
        longitude/latitude position on Cape Cod, Massachusetts (again chosen so
        you can try out this code using the `free test API account
        <https://www.degreedays.net/api/test>`__)::

            api = DegreeDaysApi.fromKeys(
                    AccountKey('test-test-test'),
                    SecurityKey('test-test-test-test-test-test-test-test-test-test-test-test-test'))
            breakdown = DatedBreakdown.daily(Period.latestValues(1))
            hddSpec = DataSpec.dated(
                    Calculation.heatingDegreeDays(Temperature.celsius(15.5)),
                    breakdown)
            cddSpec = DataSpec.dated(
                    Calculation.coolingDegreeDays(Temperature.celsius(21)),
                    breakdown)
            hourlyTempsSpec = DataSpec.timeSeries(
                    TimeSeriesCalculation.hourlyTemperature(TemperatureUnit.CELSIUS),
                    breakdown)
            request = LocationDataRequest(
                    Location.longLat(degreedays.geo.LongLat(-70.305634, 41.695475)),
                    DataSpecs(hddSpec, cddSpec, hourlyTempsSpec))
            response = api.dataApi.getLocationData(request)
            hddData = response.dataSets[hddSpec]
            cddData = response.dataSets[cddSpec]
            hourlyTempsData = response.dataSets[hourlyTempsSpec]
            print('Station ID: %s' % response.stationId)
            for v in hddData.values:
                print('%s HDD: %g' % (v.firstDay, v.value))
            for v in cddData.values:
                print('%s CDD: %g' % (v.firstDay, v.value))
            for v in hourlyTempsData.values:
                print('%s: %g C' % (v.datetime, v.value))

        Both examples above specify a location on Cape Cod, Massachusetts, so
        you can try them out using the `free test API account
        <https://www.degreedays.net/api/test>`__.  To access data for locations
        worldwide (whether station IDs, postal/zip codes, or longitude/latitude
        positions), you can `sign up for a full API account on our website
        <https://www.degreedays.net/api/signup>`__, swap your own account key
        and security key into the code samples above, then change the location
        however you wish.

        Expanding on these examples
        ---------------------------
        The examples above are just a starting point...

        * The :py:class:`LocationDataRequest` is highly configurable:

          * You can specify the :py:class:`Location` you want data for as a
            weather-station ID or a geographic location (postal/zip code, or
            longitude/latitude position). For geographic locations the API will
            automatically select the best weather station to satisfy your
            request.
          * There are various components that enable you to specify exactly what
            each set of data should contain. Each :py:class:`DataSpec` can be
            either a :py:class:`DatedDataSpec` (for
            daily/weekly/monthly/yearly/custom degree days), an
            :py:class:`AverageDataSpec` (for average degree days), or a
            :py:class:`TimeSeriesDataSpec` (for hourly temperature data). Each
            of these is configured with objects that determine the data
            :py:class:`Calculation` (or :py:class:`TimeSeriesCalculation`), the
            :py:class:`Breakdown`, and the :py:class:`Period` of coverage that
            you want.
          * You can fetch *multiple* sets of data from a location in a single
            request. For example, you might want to fetch HDD and CDD with
            multiple base temperatures each. To do this just create the
            :py:class:`DataSpecs` in your request with multiple different
            :py:class:`DataSpec` items.
        * The :py:class:`LocationDataResponse` also contains information about
          the weather station(s) used to generate the returned data. If you
          request data from a geographic location initially, you might want to
          use the station ID to fetch updates later. If you are specifying
          geographic locations, but storing data by station ID, you can avoid
          re-fetching data unnecessarily by using
          :py:meth:`getLocationInfo(locationInfoRequest) <getLocationInfo>` to
          get the station ID that would be returned by an equivalent call to
          :py:meth:`getLocationData(locationDataRequest) <getLocationData>`. We
          call this :ref:`two-stage data fetching <two-stage-fetching>`.
        * **Error handling** would be important for production code. Catching
          :py:class:`DegreeDaysApiException` will cover everything that you
          should be prepared for, but it's often useful to get more detail.
          Check the list of exceptions for this method further above and the
          :ref:`notes on getting DataSet objects out of a DataSets object
          <get-data-set>` to see exactly what subclasses of
          ``DegreeDaysApiException`` can be thrown.

        Rules that govern what you can get in response
        ----------------------------------------------
        It's worth understanding the rules that govern what you can get in
        response to a request for one or more sets of data from a particular
        location:

        **Stations that data can come from:**

        * If your request specifies a :py:class:`StationIdLocation
          <degreedays.api.data.impl.StationIdLocation>` (created via
          :py:meth:`Location.stationId`) then the API will only ever return data
          from that station. It will never substitute in data from another
          station.
        * If your request specifies a :py:class:`GeographicLocation` the API
          will choose which station(s) to use automatically. The choice will
          depend on the data you requested as well as the location you requested
          it for. Some stations have more data than others, and the quality of a
          station's data can vary over time. The API will choose the station(s)
          that can best satisfy your specific request.
        * The API will never send a :py:class:`LocationDataResponse` for an
          inactive station. An inactive station is one that hasn't sent any
          usable weather reports for roughly 10 days or more (10 being an
          approximate number that is subject to change). See
          :py:attr:`LocationError.isDueToLocationNotSupported` for more
          information on inactive stations. If you request data from an inactive
          station, or for a :py:class:`GeographicLocation` for which no active
          station can be found, you will get a :py:class:`LocationError` to
          indicate that the location is not supported.

        **When you request more data than is available:**

        * If your request specifies data for a location for which an active
          station exists, you should, barring other failures, get a
          :py:class:`LocationDataResponse`. But, if any of the
          :py:class:`DataSpec` objects that you specified cannot be satisfied
          (either fully or partially), you will get a
          :py:class:`SourceDataError` each time you try to get the corresponding
          :py:class:`DataSet` from the :py:class:`DataSets` object held by the
          response.
        * If there's not enough data to fully satisfy your request, the API will
          return partial sets of data if it can. For example, you might request
          10 years of data, but only get 5. Because data is only returned for
          active stations, you can rely on recent times being covered if
          requested (usually including yesterday's data in the station's
          time-zone, but always to within around 10 days or so of that day).
          But data from further back could be missing.
        * If you'd rather the API gave you a :py:class:`SourceDataError` (see
          above) than any partially-complete :py:class:`DataSet`, make sure to
          specify the `minimumNumberOfValues` on :py:meth:`Period.latestValues`
          or the `minimumDayRange` on :py:meth:`Period.dayRange` for the
          :py:class:`Period` objects in your request. Unless you specify
          minimums, the API will return the best it can from within the
          specification you give.

        **Other data guarantees:**

        * Excepting the :ref:`widening rules <widening>` that apply when a
          :py:class:`DayRangePeriod <degreedays.api.data.impl.DayRangePeriod>`
          (created with :py:meth:`Period.dayRange`) is specified imprecisely,
          the API will never return more data than you asked for, or data from
          outside of the range that you asked for.
        * The API will never return data with gaps in it. No gaps, and no
          special error values like `NaN`, 0, -1, 9999 etc. If a station has
          *small* gaps in its source temperature data, the API will fill those
          gaps with estimates before calculating any degree days. But *larger*
          gaps are not tolerated, and the API will only ever use data from
          *after* such gaps. If a larger gap is ongoing (i.e. there is no good
          data after it), the station will be declared inactive (see above).
          This approach ensures that active stations will always have contiguous
          sets of data that run through to recent days."""
        LocationDataRequest._check(locationDataRequest)
        return self.__checkAndGet(
            locationDataRequest, LocationDataResponse)
    def getLocationInfo(self, locationInfoRequest):
        # type: (LocationInfoRequest) -> LocationInfoResponse
        """A lightweight alternative to
        :py:meth:`getLocationData(locationDataRequest) <getLocationData>` that
        returns info about the station(s) that would be used to satisfy an
        equivalent :py:class:`LocationDataRequest`, but not the data itself.
        Typically you would specify a :py:class:`GeographicLocation` in the
        :py:class:`LocationInfoRequest`, using this 
        ``getLocationInfo(locationInfoRequest)`` method to map postal/zip codes
        or longitude/latitude positions to station IDs.

        :param LocationInfoRequest locationInfoRequest: specifies the location
            you want data for and the data that you want (as this can affect the
            station-selection process for :py:class:`GeographicLocation` types).
        :return: :py:class:`LocationInfoResponse` containing info about the
            station(s) that would be used to satisfy an equivalent 
            :py:class:`LocationDataRequest`.
        :raises LocationError: if the request fails because of problems relating
            to the specified :py:class:`Location`.
        :raises ServiceError: if the request fails because of a problem with the
            API service (sorry!).
        :raises RateLimitError: if you hit the
            :py:class:`degreedays.api.RateLimit` for your account's plan, and
            need to wait a little while before it's reset.
        :raises InvalidRequestError: if the request that is sent to the API
            servers is invalid (e.g. if it is authenticated with invalid
            :ref:`API access keys <access-keys>`).
        :raises TransportError: if there's a problem sending the request to
            the API servers, or a problem getting the API's response back.
        :raises DegreeDaysApiError: **the superclass of all the exceptions
            listed above**.
        :raises TypeError: if `locationDataRequest` is not a
            :py:class:`LocationDataRequest` object.

        This ``getLocationInfo(locationInfoRequest)`` method can be useful if
        you have a database of data stored by station ID, but are using
        :py:class:`GeographicLocation` types (postal/zip codes or
        longitude/latitude positions) to determine which station ID to use for
        each of your real-world locations. A call to this
        ``getLocationInfo(locationInfoRequest)`` method will only ever take one
        request unit, whilst a call to
        :py:meth:`getLocationData(locationDataRequest) <getLocationData>` can
        take many more (depending on how much data it fetches), so it often
        makes sense to use this method to avoid the overhead of re-fetching data
        that you already have stored. We call this :ref:`two-stage data fetching
        <two-stage-fetching>`.

        Note, however, that this returns nothing that isn't also returned by a
        call to :py:meth:`getLocationData(locationDataRequest)
        <getLocationData>`. So, if you know you'll be fetching data anyway, you
        might as well use :py:meth:`getLocationData(locationDataRequest)
        <getLocationData>` from the start.

        Sample ``LocationInfoRequest``/``LocationInfoResponse`` code
        ------------------------------------------------------------
        Here's a simple example showing how to find out what station ID the API
        would use to provide 10 recent calendar years' worth of data for US zip code
        02633 (which is on Cape Cod so you can use the `free test API account
        <https://www.degreedays.net/api/test>`__).  The station ID is output to
        the command line::

            api = DegreeDaysApi.fromKeys(
                    AccountKey(yourStringAccountKey),
                    SecurityKey(yourStringSecurityKey))
            hddSpec = DataSpec.dated(
                    Calculation.heatingDegreeDays(Temperature.fahrenheit(65)),
                    DatedBreakdown.yearly(Period.latestValues(10)))
            request = LocationInfoRequest(
                    Location.postalCode('02532', 'US'),
                    DataSpecs(hddSpec))
            response = api.dataApi.getLocationInfo(request)
            print('Station ID: %s' % response.stationId)

        Exceptions and data availability
        --------------------------------
        The exceptions thrown by this ``getLocationInfo(locationInfoRequest)``
        method are the same as those thrown by
        :py:meth:`getLocationData(locationDataRequest) <getLocationData>`, and
        they are thrown under exactly the same circumstances.

        However, because the :py:class:`LocationInfoResponse` returned by this
        method does not contain any data (i.e. no :py:class:`DataSets`), there's
        no way to tell from this whether an equivalent
        :py:class:`LocationDataResponse` would actually contain any or all of
        the data you want. So, although you can call this method to determine
        what station ID the API would use for an equivalent call to
        :py:meth:`getLocationData(LocationDataRequest) <getLocationData>`, you
        would have to actually make that call to be sure that you could get all
        the data you wanted."""
        LocationInfoRequest._check(locationInfoRequest)
        return self.__checkAndGet(
            locationInfoRequest, LocationInfoResponse)
