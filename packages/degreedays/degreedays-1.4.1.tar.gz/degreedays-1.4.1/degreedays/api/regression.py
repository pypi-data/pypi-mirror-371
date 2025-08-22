# -*- coding: utf-8 -*-

"""
For using the API to run regressions against your energy-usage data.

If you are new to this module, we suggest you start by looking at
:py:class:`RegressionApi`.
"""

import sys
import re
from degreedays._private import _Immutable, XmlElement
import degreedays._private as private
import degreedays.time
import degreedays.geo
from degreedays.api.data import Temperature, TemperatureUnit, Location, \
    DatedDataSet, DataValue, SourceDataError, Source
import degreedays.api.data
import degreedays.api
try:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from typing import TypeVar
        _RES = TypeVar('_RES', bound=degreedays.api.Response)
        if sys.version_info >= (3, 9):
            from collections.abc import Iterable, Iterator, Sequence, \
                Collection, Mapping
        else:
            from typing import Iterable, Iterator, Sequence, Collection, Mapping
except ImportError:
    pass

__all__ = ['DayNormalization', 'ExpectedCorrelation', 'PredictorType',
    'RegressionTag', 'InputPeriod', 'InputData', 'ExtraPredictorSpec',
    'RegressionSpec', 'RegressionTestPlan', 'RegressionRequest',
    'RegressionComponent', 'BaseloadRegressionComponent',
    'ExtraRegressionComponent', 'DegreeDaysRegressionComponent',
    'RegressionComponents', 'Regression', 'RegressionResponse', 'RegressionApi']

# See TemperatureUnit for an explanation of this pattern.  We use it for all
# enums.
class _DayNormalizationMetaclass(type):
    _NAMES = ('Weighted', 'Unweighted', 'None')
    def __iter__(cls): # type: () -> Iterator[DayNormalization]
        for name in cls._NAMES:
            yield DayNormalization._get(name)
    #EnumCopyStart(DayNormalization)
    @property
    def WEIGHTED(cls): # type: () -> DayNormalization
        """The recommended option, this gives the best results for
        :py:class:`InputData` with periods of different length, and the
        weighting makes no difference if the periods are all the same length.
        With this option longer periods effectively have a greater influence on
        the regression coefficients than shorter periods.

        See `www.degreedays.net/regression#day-normalization
        <https://www.degreedays.net/regression#day-normalization>`__

        Access via: ``DayNormalization.WEIGHTED``"""
        return DayNormalization._get('Weighted')
    @property
    def UNWEIGHTED(cls): # type: () -> DayNormalization
        """For :py:class:`InputData` with periods of different length this is
        typically better than using no day normalization at all, but it's not as
        good as the :py:attr:`WEIGHTED` option.

        See `www.degreedays.net/regression#day-normalization
        <https://www.degreedays.net/regression#day-normalization>`__

        Access via: ``DayNormalization.UNWEIGHTED``"""
        return DayNormalization._get('Unweighted')
    @property
    def NONE(cls): # type: () -> DayNormalization
        """For no day normalization at all, this works fine for
        :py:class:`InputData` with periods that are all the same length, but not
        so well for data with periods of different length.

        See `www.degreedays.net/regression#day-normalization
        <https://www.degreedays.net/regression#day-normalization>`__

        Access via: ``DayNormalization.NONE``"""
        return DayNormalization._get('None')
    #EnumCopyEnd
_DayNormalizationSuper = _DayNormalizationMetaclass('_DayNormalizationSuper',
    (_Immutable,), {'__slots__': ()})
class DayNormalization(_DayNormalizationSuper):
    """Defines the day normalization used in the regression process – an
    important consideration when periods of energy usage cover different lengths
    of time.

    The best explanation of the day-normalization options is in the
    `docs for our online regression tool
    <https://www.degreedays.net/regression#day-normalization>`__ (which itself
    uses the API internally)."""
    __slots__ = ('__name', '__nameUpper')
    __map = {} # type: dict[str, DayNormalization]
    #EnumPaste(DayNormalization)
    def __new__(cls):
        raise TypeError('This is not built for direct instantiation.  Please '
            'use DayNormalization.WEIGHTED, DayNormalization.UNWEIGHTED, or '
            'DayNormalization.NONE.')
    @classmethod
    def _create(cls, name): # type: (str) -> DayNormalization
        newItem = super(DayNormalization, cls).__new__(cls)
        if name in _DayNormalizationMetaclass._NAMES:
            newItem.__name = name
        else:
            raise ValueError
        newItem.__nameUpper = name.upper()
        cls.__map[name] = newItem
        return newItem
    @classmethod
    def _get(cls, name): # type: (str) -> DayNormalization
        return cls.__map[name]
    def __getattr__(self, name): # type: (str) -> str
        return getattr(_DayNormalizationMetaclass, name)
    def _equalityFields(self): # type: () -> str
        return self.__name
    def __str__(self): # type: () -> str
        return self.__name
    def __repr__(self):
        return 'DayNormalization.' + self.__nameUpper
    def _toXml(self):
        return XmlElement('DayNormalization').setValue(self.__name)
    @staticmethod
    def _check(param, paramName='dayNormalization'):
        # type: (DayNormalization, str) -> DayNormalization
        if type(param) is not DayNormalization:
            raise TypeError(private.wrongTypeString(param, paramName,
                DayNormalization, 'DayNormalization.WEIGHTED, '
                'DayNormalization.UNWEIGHTED, or DayNormalization.NONE.'))
        return param
for _name in DayNormalization._NAMES:
    DayNormalization._create(_name)


class _ExpectedCorrelationMetaclass(type):
    _NAMES = ('Positive', 'Negative', 'PositiveOrNegative')
    def __iter__(cls): # type: () -> Iterator[ExpectedCorrelation]
        for name in cls._NAMES:
            yield ExpectedCorrelation._get(name)
    #EnumCopyStart(ExpectedCorrelation)
    @property
    def POSITIVE(cls): # type: () -> ExpectedCorrelation
        """For an extra predictor expected to have a positive correlation with
        energy usage i.e. larger extra-predictor figures lead to larger energy
        usage.

        Access via: ``ExpectedCorrelation.POSITIVE``"""
        return ExpectedCorrelation._get('Positive')
    @property
    def NEGATIVE(cls): # type: () -> ExpectedCorrelation
        """For an extra predictor expected to have a negative correlation with
        energy usage i.e. larger extra-predictor figures lead to smaller energy
        usage.

        Access via: ``ExpectedCorrelation.NEGATIVE``"""
        return ExpectedCorrelation._get('Negative')
    @property
    def POSITIVE_OR_NEGATIVE(cls): # type: () -> ExpectedCorrelation
        """For an extra predictor that could be expected to have either a
        positive or negative correlation with energy usage. You could look at
        this as an "I don't know what to expect" option. If possible, it's
        better to figure out what each extra predictor is and what you expect
        from it, but this option can be useful if your system is dealing with
        data it doesn't have much context on.

        Access via: ``ExpectedCorrelation.POSITIVE_OR_NEGATIVE``"""
        return ExpectedCorrelation._get('PositiveOrNegative')
    #EnumCopyEnd
_ExpectedCorrelationSuper = _ExpectedCorrelationMetaclass(
    '_ExpectedCorrelationSuper', (_Immutable,), {'__slots__': ()})
class ExpectedCorrelation(_ExpectedCorrelationSuper):
    """Defines how an extra predictor's figures are expected to correlate with
    energy usage (whether larger predictor numbers lead to larger or smaller
    energy usage).  This helps the API rank the various regressions it tests, as
    it will downrank the regressions with extra predictors that correlate with
    energy usage in an unexpected way."""
    __slots__ = ('__name', '__nameUpper')
    __map = {} # type: dict[str, ExpectedCorrelation]
    #EnumPaste(ExpectedCorrelation)
    def __new__(cls):
        raise TypeError('This is not built for direct instantiation.  Please '
            'use ExpectedCorrelation.POSITIVE, ExpectedCorrelation.NEGATIVE, '
            'or ExpectedCorrelation.POSITIVE_OR_NEGATIVE.')
    @classmethod
    def _create(cls, name): # type: (str) -> ExpectedCorrelation
        newItem = super(ExpectedCorrelation, cls).__new__(cls)
        if (name == 'Positive' or name == 'Negative'):
            newItem.__name = name
            newItem.__nameUpper = name.upper()
        elif (name == 'PositiveOrNegative'):
            newItem.__name = name
            newItem.__nameUpper = 'POSITIVE_OR_NEGATIVE'
        else:
            raise ValueError
        cls.__map[name] = newItem
        return newItem
    @classmethod
    def _get(cls, name): # type: (str) -> ExpectedCorrelation
        return cls.__map[name]
    def __getattr__(self, name): # type: (str) -> str
        return getattr(_ExpectedCorrelationMetaclass, name)
    def _equalityFields(self): # type: () -> str
        return self.__name
    def __str__(self): # type: () -> str
        return self.__name
    def __repr__(self):
        return 'ExpectedCorrelation.' + self.__nameUpper
    def _toXml(self):
        return XmlElement('ExpectedCorrelation').setValue(self.__name)
    @staticmethod
    def _check(param, paramName='expectedCorrelation'):
        # type: (ExpectedCorrelation, str) -> ExpectedCorrelation
        if type(param) is not ExpectedCorrelation:
            raise TypeError(private.wrongTypeString(param, paramName,
                ExpectedCorrelation, 'ExpectedCorrelation.POSITIVE, '
                'ExpectedCorrelation.NEGATIVE, or '
                'ExpectedCorrelation.POSITIVE_OR_NEGATIVE.'))
        return param
for _name in ExpectedCorrelation._NAMES:
    ExpectedCorrelation._create(_name)


class _PredictorTypeMetaclass(type):
    _NAMES = ('Cumulative', 'Average')
    def __iter__(cls): # type: () -> Iterator[PredictorType]
        for name in cls._NAMES:
            yield PredictorType._get(name)
    #EnumCopyStart(PredictorType)
    @property
    def CUMULATIVE(cls): # type: () -> PredictorType
        """For an extra predictor that increases with time and is naturally
        larger over longer periods e.g. a ``CUMULATIVE`` measure of occupancy
        could be the total person-hours worked. If a typical day saw 110 person
        hours, a typical 5-day week might see 770 person hours (i.e. larger
        figures for longer periods).

        Access via: ``PredictorType.CUMULATIVE``"""
        return PredictorType._get('Cumulative')
    @property
    def AVERAGE(cls): # type: () -> PredictorType
        """For an extra predictor that is normalized such that the length of the
        period has no effect e.g. an ``AVERAGE`` measure of occupancy could be
        the percentage of full occupancy. A building could be 50% occupied for a
        week, or a month, or a year – longer periods would not mean larger
        figures.

        Access via: ``PredictorType.AVERAGE``"""
        return PredictorType._get('Average')
    #EnumCopyEnd
_PredictorTypeSuper = _PredictorTypeMetaclass('_PredictorTypeSuper',
    (_Immutable,), {'__slots__': ()})
class PredictorType(_PredictorTypeSuper):
    """Defines an extra predictor's figures as being cumulative (increasing with
    time and naturally larger over longer periods) or average (normalized such
    that the length of the period has no effect)."""
    __slots__ = ('__name', '__nameUpper')
    __map = {} # type: dict[str, PredictorType]
    #EnumPaste(PredictorType)
    def __new__(cls):
        raise TypeError('This is not built for direct instantiation.  Please '
            'use PredictorType.CUMULATIVE or PredictorType.AVERAGE.')
    @classmethod
    def _create(cls, name): # type: (str) -> PredictorType
        newItem = super(PredictorType, cls).__new__(cls)
        if name in cls._NAMES:
            newItem.__name = name
        else:
            raise ValueError
        newItem.__nameUpper = name.upper()
        cls.__map[name] = newItem
        return newItem
    @classmethod
    def _get(cls, name): # type: (str) -> PredictorType
        return cls.__map[name]
    def __getattr__(self, name): # type: (str) -> str
        return getattr(_PredictorTypeMetaclass, name)
    def _equalityFields(self): # type: () -> str
        return self.__name
    def __str__(self): # type: () -> str
        return self.__name
    def __repr__(self):
        return 'PredictorType.' + self.__nameUpper
    def _toXml(self):
        return XmlElement('PredictorType').setValue(self.__name)
    @staticmethod
    def _check(param, paramName='predictorType'):
        # type: (PredictorType, str) -> PredictorType
        if type(param) is not PredictorType:
            raise TypeError(private.wrongTypeString(param, paramName,
                PredictorType,
                'PredictorType.CUMULATIVE or PredictorType.AVERAGE.'))
        return param
for _name in PredictorType._NAMES:
    PredictorType._create(_name)


class _RegressionTagMetaclass(type):
    _NAMES = ('Shortlist', 'NotableOther', 'Requested', 'InShortlistRange')
    def __iter__(cls): # type: () -> Iterator[RegressionTag]
        for name in cls._NAMES:
            yield RegressionTag._get(name)
    #EnumCopyStart(RegressionTag)
    @property
    def SHORTLIST(cls): # type: () -> RegressionTag
        """Indicates a regression that was automatically selected by the API as
        a shortlist regression – one that looks likely to describe the usage
        data better than the others tested.

        Access via: ``RegressionTag.SHORTLIST``"""
        return RegressionTag._get('Shortlist')
    @property
    def NOTABLE_OTHER(cls): # type: () -> RegressionTag
        """Indicates a regression that didn't make the :py:attr:`SHORTLIST`, but
        was considered notable. This might, for example, apply to the best
        CDD-only regression for a set of data that correlates better with HDD
        than CDD, or to a regression with shortlist-worthy stats but unexpected
        negative coefficients.

        Access via: ``RegressionTag.NOTABLE_OTHER``"""
        return RegressionTag._get('NotableOther')
    @property
    def REQUESTED(cls): # type: () -> RegressionTag
        """Indicates a regression that was explicitly specified in the request
        as one that should be returned.

        You can set requested regressions when you create the
        :py:class:`RegressionTestPlan`.

        Access via: ``RegressionTag.REQUESTED``"""
        return RegressionTag._get('Requested')
    @property
    def IN_SHORTLIST_RANGE(cls): # type: () -> RegressionTag
        """Indicates a regression that was explicitly specified in the request,
        and that has strong enough statistics to appear in the
        :py:attr:`SHORTLIST` even though it wasn't auto-selected to be in the
        shortlist (if it was it would have the :py:attr:`SHORTLIST` tag
        instead).

        It is possible for none of the :py:attr:`REQUESTED` regressions to have
        this tag if none of them have statistics as good as the auto-selected
        :py:attr:`SHORTLIST` regressions.

        Note that you can set requested regressions when you create the
        :py:class:`RegressionTestPlan`.

        Access via: ``RegressionTag.IN_SHORTLIST_RANGE``"""
        return RegressionTag._get('InShortlistRange')
    #EnumCopyEnd
_RegressionTagSuper = _RegressionTagMetaclass('_RegressionTagSuper',
    (_Immutable,), {'__slots__': ()})
class RegressionTag(_RegressionTagSuper):
    """Tags that the API adds to :py:class:`Regression` objects to indicate why
    it included them in a :py:class:`RegressionResponse`."""
    __slots__ = ('__name', '__nameUpper')
    __map = {} # type: dict[str, RegressionTag]
    #EnumPaste(RegressionTag)
    def __new__(cls):
        raise TypeError('This is not built for direct instantiation.  Please '
            'use RegressionTag.SHORTLIST, RegressionTag.NOTABLE_OTHER, '
            'RegressionTag.REQUESTED, or RegressionTag.IN_SHORTLIST_RANGE.')
    @classmethod
    def _create(cls, name): # type: (str) -> RegressionTag
        newItem = super(RegressionTag, cls).__new__(cls)
        if (name == 'Shortlist' or name == 'Requested'):
            newItem.__name = name
            newItem.__nameUpper = name.upper()
        elif name == 'NotableOther':
            newItem.__name = name
            newItem.__nameUpper = 'NOTABLE_OTHER'
        elif name == 'InShortlistRange':
            newItem.__name = name
            newItem.__nameUpper = 'IN_SHORTLIST_RANGE'
        else:
            raise ValueError
        cls.__map[name] = newItem
        return newItem
    @classmethod
    def _get(cls, name): # type: (str) -> RegressionTag
        return cls.__map[name]
    def __getattr__(self, name): # type: (str) -> str
        return getattr(_RegressionTagMetaclass, name)
    def _equalityFields(self): # type: () -> str
        return self.__name
    def __str__(self): # type: () -> str
        return self.__name
    def __repr__(self):
        return 'RegressionTag.' + self.__nameUpper
    @staticmethod
    def _check(param, paramName='regressionTag'):
        # type: (RegressionTag, str) -> RegressionTag
        if type(param) is not RegressionTag:
            raise TypeError(private.wrongTypeString(param, paramName,
                RegressionTag, 'RegressionTag.SHORTLIST, '
                'RegressionTag.NOTABLE_OTHER, RegressionTag.REQUESTED, or '
                'RegressionTag.IN_SHORTLIST_RANGE.'))
        return param
for _name in RegressionTag._NAMES:
    RegressionTag._create(_name)


_MAX_EXTRA_PREDICTORS = 2
_EXTRA_PREDICTOR_KEY_REGEXP_STRING = '[-_.a-zA-Z0-9]{1,60}$'
_EXTRA_PREDICTOR_KEY_REGEXP = re.compile(_EXTRA_PREDICTOR_KEY_REGEXP_STRING)



def _checkExtraPredictorKey(key, errorMessageStart=''):
    # type: (str, str) -> str
    if not private.isString(key):
        raise TypeError('%sExtra-predictor keys must be strings.' %
            errorMessageStart)
    if not _EXTRA_PREDICTOR_KEY_REGEXP.match(key):
        raise ValueError('%sInvalid extra-predictor key (%r) - it should match '
            'the regular expression %s.' % (errorMessageStart,
                private.logSafe(key), _EXTRA_PREDICTOR_KEY_REGEXP_STRING))
    return key


class InputPeriod(_Immutable):
    """Defines a dated period with its energy usage and any extra-predictor
    figures. A set of ``InputPeriod`` items together forms the
    :py:class:`InputData` required for every :py:class:`RegressionRequest`.

    :param degreedays.time.DayRange dayRange: the period of time covered.
    :param float usage: the energy usage over the specified `dayRange`.
    :param Mapping[str, float] | None extraPredictorsOrNone: a
        :py:class:`Mapping` (e.g. a ``dict``) of no more than 2 string
        extra-predictor keys to numeric extra-predictor values.  Extra-predictor
        keys must match the regular expression ``[-_.a-zA-Z0-9]{1,60}``, and
        cannot be ``'baseload'``, ``'heatingDegreeDays'``, or
        ``'coolingDegreeDays'``.
    :raise TypeError: if `dayRange` is not a
        :py:class:`degreedays.time.DayRange`, if `usage` is not a `float`, or if
        `extraPredictorsOrNone` is not a ``Mapping[str, float]`` or `None`.
    :raise ValueError: if `usage` or any extra-predictor values are `NaN` or
        infinity, or if there are more than 2 extra predictors, or if any
        extra-predictor keys do not match the specification detailed above.

    See `www.degreedays.net/api/regression
    <https://www.degreedays.net/api/regression>`__ for more information and
    code samples.  That page has some `sample code showing how to use extra
    predictors <https://www.degreedays.net/api/regression#extra-predictors>`__,
    and there's also some additional practical information on specifying and
    using extra predictors in the `docs for our website regression tool
    <https://www.degreedays.net/regression#extra-predictors>`__ (which itself
    uses the API internally)."""
    __slots__ = ('__dayRange', '__usage', '__extraPredictorsOrNone')
    def __init__(self,
            dayRange, # type: degreedays.time.DayRange
            usage, # type: float
            extraPredictorsOrNone=None # type: Mapping[str, float] | None
            ): # type: (...) -> None
        self.__dayRange = degreedays.time.DayRange._check(dayRange)
        self.__usage = private.checkNumeric(usage, 'usage')
        if extraPredictorsOrNone is None:
            self.__extraPredictorsOrNone = None
        else:
            dictCopy = private.checkMappingAndReturnDictCopy(
                extraPredictorsOrNone, 'extraPredictorsOrNone')
            epCount = len(dictCopy)
            if epCount == 0:
                self.__extraPredictorsOrNone = None
            else:
                if epCount > _MAX_EXTRA_PREDICTORS:
                    raise ValueError('Cannot have more than %d extra '
                        'predictors - %d is too many.' %
                        (_MAX_EXTRA_PREDICTORS, len(dictCopy)))
                for key, value in private.getDictItemsIterable(dictCopy):
                    _checkExtraPredictorKey(key)
                    private.checkNumeric(value, 'An extra-predictor value')
                self.__extraPredictorsOrNone = dictCopy
    def _equalityFields(self):
        # Order won't matter for equality comparisons of the dict
        return (self.__dayRange, self.__usage, self.__extraPredictorsOrNone)
    def __hash__(self):
        h = hash((self.__class__, self.__dayRange, self.__usage))
        if self.__extraPredictorsOrNone is not None:
            h = private.getDictHash(self.__extraPredictorsOrNone, h)
        return h
    @property
    def dayRange(self): # type: () -> degreedays.time.DayRange
        """The period of time covered by this ``InputPeriod``."""
        return self.__dayRange
    @property
    def usage(self): # type: () -> float
        """The energy usage over this ``InputPeriod``."""
        return self.__usage
    @property
    def extraPredictorCount(self): # type: () -> int
        """The number of extra predictors that are defined for this
        ``InputPeriod``."""
        if self.__extraPredictorsOrNone is None:
            return 0
        return len(self.__extraPredictorsOrNone)
    @property
    def extraPredictorKeys(self): # type: () -> Sequence[str]
        """A :py:class:`Sequence[str]` of the extra-predictor keys defined for
        this ``InputPeriod``.  This will be empty if no extra-predictors are
        defined."""
        # As of python 3.7 dicts are ordered by insertion order, which is what
        # we want for usability (though it's not essential).  So we don't do
        # anything extra to try to preserve insertion order.
        if self.__extraPredictorsOrNone is None:
            return ()
        return tuple(self.__extraPredictorsOrNone)
    def getExtraPredictor(self, key): # type: (str) -> float
        """Returns the `float` value of the extra predictor with the specified
        string `key`.

        :param str key: a string extra-predictor key.
        :raises TypeError: if `key` is not a `str`.
        :raises KeyError: if `key` isn't one of the extra-predictor keys
            stored in this object.

        See also: :py:attr:`extraPredictorKeys`"""
        private.checkString(key, 'key')
        if self.__extraPredictorsOrNone is None:
            raise KeyError(
                'This InputPeriod does not have any extra predictors.')
        else:
            # Following will throw a KeyError if key isn't found.
            return self.__extraPredictorsOrNone[key]
    def _extraPredictorsKeyEqualsOrderUnimportant(self, inputPeriod):
        # type: (InputPeriod) -> bool
        if self.__extraPredictorsOrNone is None:
            return inputPeriod.__extraPredictorsOrNone is None
        elif inputPeriod.__extraPredictorsOrNone is None:
            return False
        return ((len(self.__extraPredictorsOrNone) ==
                len(inputPeriod.__extraPredictorsOrNone)) and
            all(k in self.__extraPredictorsOrNone for
                k in inputPeriod.__extraPredictorsOrNone))
    def __str__(self):
        s = [] # type: list[str]
        if len(self.__dayRange) == 1:
            s.append(str(self.__dayRange.first))
        else:
            s.append(str(self.__dayRange))
        s.append(': %g' % self.__usage)
        if self.__extraPredictorsOrNone is not None:
            for key, value in private.getDictItemsIterable(
                    self.__extraPredictorsOrNone):
                s.append(', %s %g' % (key, value))
        return ''.join(s)
    def __repr__(self):
        if self.__extraPredictorsOrNone is None:
            return 'InputPeriod(%r, %r)' % (self.__dayRange, self.__usage)
        else:
            return ('InputPeriod(%r, %r, %r)' %
                (self.__dayRange, self.__usage, self.__extraPredictorsOrNone))
    def _toXml(self): # type: () -> XmlElement
        e = XmlElement('InputPeriod').addChild(self.__dayRange._toXml())
        e.newChild('Usage').setValue(self.__usage)
        if self.__extraPredictorsOrNone is not None:
            for k, v in private.getDictItemsIterable(
                    self.__extraPredictorsOrNone):
                e.newChild('ExtraPredictor').addAttribute('key', k).setValue(v)
        return e
    @staticmethod
    def _check(param, paramName="inputPeriod"):
        # type: (InputPeriod, str) -> InputPeriod
        if type(param) is not InputPeriod:
            raise TypeError(private.wrongTypeString(param, paramName,
                InputPeriod))
        return param


class InputData(_Immutable):
    """Defines the energy data (and any extra-predictor data) that the API
    should run regressions against.

    :param \\*args: up to 1096 :py:class:`InputPeriod` objects, or one or more
        sequences (e.g. lists or tuples) containing a total of up to 1096
        ``InputPeriod`` objects.
    :raises TypeError: if you pass in anything that isn't an
        :py:class:`InputPeriod` object or a sequence (e.g. list or tuple) of
        ``InputPeriod`` objects.
    :raises ValueError: if the :py:class:`InputPeriod` objects passed in do not
        match the specified :ref:`requirements <input-period-requirements>`.

    An `InputData` object is essentially a chronologically-ordered set of
    :py:class:`InputPeriod` objects, with each one specifying a dated period and
    the energy usage (and optionally any extra-predictor figures) for that
    period.

    The `regression API docs on our website
    <https://www.degreedays.net/api/regression>`__ have more information and
    code samples.

    .. _input-period-requirements:

    Requirements of the ``InputPeriod`` objects that make up an ``InputData`` object
    --------------------------------------------------------------------------------
    Input periods must be consecutively ordered, and cannot overlap. Gaps
    between input periods are OK though.

    If any input periods have extra-predictor figures, then all input periods
    must have figures for the same extra-predictor keys.

    The minimum number of input periods required is::

        minimumNumberOfInputPeriods = 3 + numberOfExtraPredictors

    Though this is just a bare minimum – you cannot hope for good
    regression results unless you have considerably more input periods than
    this. We recommend at least::

        recommendedMinimumNumberOfInputPeriods = 10 + numberOfExtraPredictors

    ``InputData`` allows a **maximum of 1096 input periods**. This is enough to
    cover 3 years of daily data (with one of those years being a leap year).

    See `www.degreedays.net/api/regression
    <https://www.degreedays.net/api/regression>`__ for more information and
    code samples."""
    __slots__ = ('__inputPeriods',)
    def __mustAddMessage(self, minimum, added, extraPredictors):
        # type: (int, int, int) -> str
        s = [] # type: list[str]
        s.append('%d InputPeriod ' % added)
        if added != 1:
            s.append('items ')
        s.append('is not enough. ')
        if extraPredictors > 0:
            s.append('With %d extra predictor' % extraPredictors)
            if extraPredictors > 1:
                s.append('s')
            s.append(' y')
        else:
            s.append('Y')
        s.append(('ou must have at least %d (although this is just a bare '
            'minimum to generate regressions - realistically you really want '
            'at least %d for useful results).') %
            (minimum, 10 + extraPredictors))
        return ''.join(s)
    def __init__(self, *args):
        # type: (InputPeriod | Iterable[InputPeriod]) -> None
        periods = [] # type: list[InputPeriod]
        def add(item): # type: (InputPeriod | Iterable[InputPeriod]) -> None
            index = len(periods)
            if index >= 1096:
                raise ValueError(
                    'Cannot have more than 1096 InputPeriod items.')
            if isinstance(item, InputPeriod):
                if index > 0:
                    last = periods[index - 1]
                    if not item.dayRange.first > last.dayRange.last:
                        raise ValueError(('Problem DayRange at index %d (%s) - '
                            'it must start after the previous DayRange (%s) '
                            'finished.') %
                                (index, item.dayRange, last.dayRange))
                    if not item._extraPredictorsKeyEqualsOrderUnimportant(last):
                        raise ValueError(('The item at index %d has different '
                            'extra-predictor keys %s to previous items %s.  If '
                            'adding extra predictors the same predictors must '
                            'be present for each and every InputPeriod.  If '
                            'you are missing extra-predictor data for some '
                            'periods, just leave those periods out of the '
                            'InputData.') % (index, item.extraPredictorKeys,
                                last.extraPredictorKeys))
                periods.append(item)
            elif private.isString(item):
                # Have to be careful with strings cos they look like a
                # sequence but will cause a stack overflow, see:
                # https://stackoverflow.com/questions/1835018/
                InputPeriod._check(item,
                    'An item passed into the InputData constructor')
            else:
                # assume it's a sequence, just let it throw error if not
                # Could do a try catch too, so can give a useful error
                # message if it's not a sequence or a InputPeriod.
                for innerItem in item:
                    add(innerItem)
        for arg in args:
            add(arg)
        length = len(periods)
        if length == 0:
            raise ValueError(self.__mustAddMessage(3, 0, 0))
        last = periods[-1]
        noExtraPredictors = last.extraPredictorCount
        minimum = 3 + noExtraPredictors
        if length < minimum:
            raise ValueError(self.__mustAddMessage(
                minimum, length, noExtraPredictors))
        self.__inputPeriods = tuple(periods)
    def _equalityFields(self):
        return self.__inputPeriods
    @property
    def periods(self): # type: () -> Sequence[InputPeriod]
        """A non-empty, chronologically-ordered :py:class:`Sequence` of the
        :py:class:`InputPeriod` objects that make up this ``InputData``."""
        return self.__inputPeriods
    @property
    def extraPredictorKeys(self): # type: () -> Collection[str]
        """A possibly-empty :py:class:`Collection` of extra-predictor keys that
        this ``InputData`` (and each :py:class:`InputPeriod` within it) has
        extra-predictor figures for."""
        return self.__inputPeriods[0].extraPredictorKeys
    @property
    def fullRange(self): # type: () -> degreedays.time.DayRange
        """A :py:class:`degreedays.time.DayRange` indicating the total period of
        time covered by this ``InputData`` object (including any gaps between
        its input periods)."""
        return degreedays.time.DayRange(self.__inputPeriods[0].dayRange.first,
            self.__inputPeriods[-1].dayRange.last)
    def __str__(self):
        s = [] # type: list[str]
        s.append('InputData(')
        s.append(str(len(self.__inputPeriods)))
        s.append(' periods from (')
        s.append(str(self.__inputPeriods[0]))
        s.append(') to (')
        s.append(str(self.__inputPeriods[-1]))
        s.append('))')
        return ''.join(s)
    def __repr__(self):
        return 'InputData(%r)' % (self.__inputPeriods,)
    def _toXml(self):
        e = XmlElement('InputData')
        for p in self.__inputPeriods:
            e.addChild(p._toXml())
        return e
    @staticmethod
    def _check(param, paramName="inputData"):
        # type: (InputData, str) -> InputData
        if type(param) is not InputData:
            raise TypeError(private.wrongTypeString(param, paramName,
                InputData))
        return param


class ExtraPredictorSpec(_Immutable):
    """Defines an extra predictor in terms of its :py:class:`PredictorType` and
    :py:class:`ExpectedCorrelation`, to help the API test and rank regressions
    that include data for that extra predictor.

    :param PredictorType predictorType: defines how the extra predictor's
        figures vary with the length of the periods they are measured over.
    :param ExpectedCorrelation expectedCorrelation: defines how the extra
        predictor is expected to correlate with energy usage.
    :raises TypeError: if `predictorType` is not a :py:class:`PredictorType`
        object, or `expectedCorrelation` is not an
        :py:class:`ExpectedCorrelation` object.

    ``ExtraPredictorSpec`` objects are held by the
    :py:class:`RegressionTestPlan`. There's some sample code in `the regression
    API docs on our website
    <https://www.degreedays.net/api/regression#extra-predictors>`__, and also
    there's some additional practical information on specifying and using
    extra predictors in the `docs for our website regression tool
    <https://www.degreedays.net/regression#extra-predictors>`__ (which itself
    uses the API internally)."""
    __slots__ = ('__predictorType', '__expectedCorrelation')
    def __init__(self, predictorType, expectedCorrelation):
        # type: (PredictorType, ExpectedCorrelation) -> None
        self.__predictorType = PredictorType._check(predictorType)
        self.__expectedCorrelation = ExpectedCorrelation._check(
            expectedCorrelation)
    def _equalityFields(self):
        return (self.__predictorType, self.__expectedCorrelation)
    @property
    def predictorType(self): # type: () -> PredictorType
        """The :py:class:`PredictorType` that defines how the extra predictor's
        figures vary with the length of the periods they are measured over."""
        return self.__predictorType
    @property
    def expectedCorrelation(self): # type: () -> ExpectedCorrelation
        """The :py:class:`ExpectedCorrelation` that defines how the extra
        predictor is expected to correlate with energy usage."""
        return self.__expectedCorrelation
    def _getInnerString(self):
        return '%s, %s' % (self.__predictorType, self.__expectedCorrelation)
    def __str__(self):
        return 'ExtraPredictorSpec(%s)' % self._getInnerString()
    def __repr__(self):
        return ('ExtraPredictorSpec(%r, %r)' %
            (self.__predictorType, self.__expectedCorrelation))
    def _toXml(self, key): # type: (str) -> XmlElement
        e = XmlElement('ExtraPredictorSpec').addAttribute('key', key)
        e.newChild('PredictorType').setValue(self.__predictorType)
        e.newChild('ExpectedCorrelation').setValue(self.__expectedCorrelation)
        return e
    @staticmethod
    def _check(param, paramName="extraPredictorSpec"):
        # type: (ExtraPredictorSpec, str) -> ExtraPredictorSpec
        if type(param) is not ExtraPredictorSpec:
            raise TypeError(private.wrongTypeString(param, paramName,
                ExtraPredictorSpec))
        return param


class RegressionSpec(_Immutable):
    """Defines a specification of a regression in terms of its HDD and/or CDD
    base temperature(s) and any extra predictors to be included.

    :param Temperature | None heatingBaseTemperatureOrNone: the base temperature
        of the heating degree days to be included in the specified regression,
        or the default value of `None` if heating degree days should not be
        included.
    :param Temperature | None coolingBaseTemperatureOrNone: the base temperature
        of the cooling degree days to be included in the specified regression,
        or the default value of `None` if cooling degree days should not be
        included.
    :param Iterable[str] | str extraPredictorKeys: an :py:class:`Iterable` (e.g.
        tuple or list) of string extra-predictor keys that identify the extra
        predictors to be included in the regression, or the default empty tuple
        to indicate that no extra predictors should be included. There can be a
        maximum of 2 keys.  Each key must match the regular expression 
        ``[-_.a-zA-Z0-9]{1,60}``, with ``'baseload'``, ``'heatingDegreeDays'``,
        and ``'coolingDegreeDays'`` specifically disallowed.  If you want to
        pass in just one key, for convenience you can optionally pass in just
        that one string instead of an ``Iterable[str]``.
    :raises TypeError: if `heatingBaseTemperatureOrNone` is not a
        :py:class:`Temperature <degreedays.api.data.Temperature>` or `None`, or
        if `coolingBaseTemperatureOrNone` is not a ``Temperature`` or `None`, or
        if `extraPredictorKeys` is not an :py:class:`Iterable` of string keys,
        or a single string key.
    :raises ValueError: if `extraPredictorKeys` does not match the specification
        detailed above.

    See `www.degreedays.net/api/regression
    <https://www.degreedays.net/api/regression>`__ for more information and
    code samples showing how to create ``RegressionSpec`` items and set them in
    your :py:class:`RegressionTestPlan` to ensure that the API will test and
    return those regressions."""
    __slots__ = ('__heatingBaseTemperatureOrNone',
        '__coolingBaseTemperatureOrNone', '__extraPredictorKeys')
    def __init__(self,
            heatingBaseTemperatureOrNone=None, # type: Temperature | None
            coolingBaseTemperatureOrNone=None, # type: Temperature | None
            extraPredictorKeys=() # type: Iterable[str] | str
            ): # type: (...) -> None
        if heatingBaseTemperatureOrNone is not None:
            Temperature._check(
                heatingBaseTemperatureOrNone, 'heatingBaseTemperatureOrNone')
        if coolingBaseTemperatureOrNone is not None:
            Temperature._check(
                coolingBaseTemperatureOrNone, 'coolingBaseTemperatureOrNone')
            if (heatingBaseTemperatureOrNone is not None and
                    (heatingBaseTemperatureOrNone.unit !=
                        coolingBaseTemperatureOrNone.unit)):
                raise ValueError('If heatingBaseTemperatureOrNone and '
                    'coolingBaseTemperatureOrNone are both supplied, they must '
                    'both have the same TemperatureUnit.')
        self.__heatingBaseTemperatureOrNone = heatingBaseTemperatureOrNone
        self.__coolingBaseTemperatureOrNone = coolingBaseTemperatureOrNone
        if private.isString(extraPredictorKeys):
            # Allow the user to pass a single string.
            epTuple = (private.castStr(extraPredictorKeys),)
        else:
            epTuple = tuple(extraPredictorKeys)
        self.__extraPredictorKeys = private.checkTupleItems(
            epTuple, private.checkString, 'extraPredictorKeys')
        if len(self.__extraPredictorKeys) > _MAX_EXTRA_PREDICTORS:
            raise ValueError('A RegressionSpec cannot have more than %d '
                'extra-predictor keys.' % _MAX_EXTRA_PREDICTORS)
    def _equalityFields(self):
        return (self.__heatingBaseTemperatureOrNone,
            self.__coolingBaseTemperatureOrNone,
            # Don't care about ordering for equality.
            frozenset(self.__extraPredictorKeys))
    @property
    def heatingBaseTemperatureOrNone(self): # type: () -> Temperature | None
        """The base temperature to be used for the heating degree days in the
        specified regression, or `None` if heating degree days should not be
        included."""
        return self.__heatingBaseTemperatureOrNone
    @property
    def coolingBaseTemperatureOrNone(self): # type: () -> Temperature | None
        """The base temperature to be used for the cooling degree days in the
        specified regression, or `None` if cooling degree days should not be
        included."""
        return self.__coolingBaseTemperatureOrNone
    @property
    def extraPredictorKeys(self): # type: () -> Collection[str]
        """The keys of the extra predictors to be included in the specified
        regression."""
        return self.__extraPredictorKeys
    def _appendInnerString(self, s): # type: (list[str]) -> None
        s.append('baseload')
        if self.__heatingBaseTemperatureOrNone is not None:
            s.append(', HDD %s' % self.__heatingBaseTemperatureOrNone)
        if self.__coolingBaseTemperatureOrNone is not None:
            s.append(', CDD %s' % self.__coolingBaseTemperatureOrNone)
        for key in self.__extraPredictorKeys:
            s.append(', ')
            s.append(key)
    def __str__(self):
        s = [] # type: list[str]
        s.append('RegressionSpec(')
        self._appendInnerString(s)
        s.append(')')
        return ''.join(s)
    def __repr__(self):
        s = [] # type: list[str]
        s.append('RegressionSpec(')
        added = False
        if self.__heatingBaseTemperatureOrNone is not None:
            s.append('heatingBaseTemperatureOrNone=%r' %
                self.__heatingBaseTemperatureOrNone)
            added = True
        if self.__coolingBaseTemperatureOrNone is not None:
            if added:
                s.append(', ')
            s.append('coolingBaseTemperatureOrNone=%r' %
                self.__coolingBaseTemperatureOrNone)
            added = True
        if len(self.__extraPredictorKeys) > 0:
            if added:
                s.append(', ')
            # Use repr instead of %r so dict doesn't get interpreted as args.
            s.append('extraPredictorKeys=' + repr(self.__extraPredictorKeys))
        s.append(')')
        return ''.join(s)
    def _toXml(self):
        e = XmlElement('RegressionSpec')
        if self.__heatingBaseTemperatureOrNone is not None:
            e.newChild('HeatingBaseTemperature').setValue(
                self.__heatingBaseTemperatureOrNone._toNumericString())
        if self.__coolingBaseTemperatureOrNone is not None:
            e.newChild('CoolingBaseTemperature').setValue(
                self.__coolingBaseTemperatureOrNone._toNumericString())
        for k in self.__extraPredictorKeys:
            e.newChild('ExtraPredictorKey').setValue(k)
        return e
    @staticmethod
    def _check(param, paramName="regressionSpec"):
        # type: (RegressionSpec, str) -> RegressionSpec
        if type(param) is not RegressionSpec:
            raise TypeError(private.wrongTypeString(param, paramName,
                RegressionSpec))
        return param


_MAX_CUSTOM_BASE_TEMPS = 120
_MAX_WITH_DEFAULT_CUSTOM_BASE_TEMPS = 60
_MAX_REQUESTED_REGRESSION_SPECS = 60

class RegressionTestPlan(_Immutable):
    """Defines how the API should test regressions against the
    :py:class:`InputData` you provide it.

    :param TemperatureUnit temperatureUnit: specifies whether Celsius-based or
        Fahrenheit-based degree days should be used in regressions.
    :param DayNormalization dayNormalization: specifies the
        :py:class:`DayNormalization` to be used in the regression process. By
        default this will be :py:attr:`DayNormalization.WEIGHTED`, which is the
        recommended option.
    :param Iterable[Temperature | float] customTestHeatingBaseTemperaturesOrNone:
        the base temperatures to be used for the HDD in regressions tested by
        the API.  By default this is `None` so the API will test a wide range of
        HDD base temperatures automatically.  `See examples of how to use custom
        base temperatures
        <https://www.degreedays.net/api/regression#custom-base-temperatures>`__.
    :param Iterable[Temperature | float] customTestCoolingBaseTemperaturesOrNone:
        the base temperatures to be used for the CDD in regressions tested by
        the API.  By default this is `None` so the API will test a wide range of
        CDD base temperatures automatically.  `See examples of how to use custom
        base temperatures
        <https://www.degreedays.net/api/regression#custom-base-temperatures>`__.
    :param Mapping[str, ExtraPredictorSpec] extraPredictorSpecs: a
        :py:class:`Mapping` (e.g. a :py:class:`dict`) with string
        extra-predictor keys as keys (these should match the extra-predictor
        keys used in each :py:class:`InputPeriod` of your
        :py:class:`InputData`), and the corresponding
        :py:class:`ExtraPredictorSpec` objects as values. Cannot have more than
        2 mappings, and must have valid keys matching the regular expression
        ``[-_.a-zA-Z0-9]{1,60}``, with ``'baseload'``, ``'heatingDegreeDays'``,
        and ``'coolingDegreeDays'`` specifically disallowed.  By default this is
        empty for the simple case of no extra predictors being used.
        `See more info and examples on using extra predictors from Python
        <https://www.degreedays.net/api/regression#extra-predictors>`__.
    :param Iterable[RegressionSpec] requestedRegressionSpecs: specifications for
        up to 60 regressions that you want to receive in the response from the
        API.  By default this is empty so the only regressions returned will be
        the ones chosen automatically by the API.  `See more info and examples
        on requesting specific regressions
        <https://www.degreedays.net/api/regression#requested>`__.
    :raises TypeError: if any of the arguments do not match the specifications
        detailed above.
    :raises ValueError: if any custom base :py:class:`Temperature
        <degreedays.api.data.Temperature>` objects have units that don't match
        `temperatureUnit`; if any `float` temperatures cannot be used to create
        a valid ``Temperature`` with `temperatureUnit` (e.g. because they're out
        of the allowed range, or `NaN`); if `requestedRegressionSpecs` contains
        any :py:class:`RegressionSpec` items with extra-predictor keys not
        covered by `extraPredictorSpecs`; or if any of
        `customTestHeatingBaseTemperaturesOrNone`,
        `customTestCoolingBaseTemperaturesOrNone`, `extraPredictorSpecs`, or
        `requestedRegressionSpecs` contain more than the maximum number of items
        allowed.  Note that the maximum number of
        `customTestHeatingBaseTemperaturesOrNone` depends on the maximum number
        of `customTestCoolingBaseTemperaturesOrNone` and vice versa, as
        explained `here
        <https://www.degreedays.net/api/regression#custom-base-temperatures>`__.

    You can create a ``RegressionTestPlan`` with default options like::

        testPlan = RegressionTestPlan(TemperatureUnit.CELSIUS)

    or::

        testPlan = RegressionTestPlan(TemperatureUnit.FAHRENHEIT)

    But there are lots of ways to configure a test plan further by specifiying
    optional parameters.  See `www.degreedays.net/api/regression
    <https://www.degreedays.net/api/regression>`__ for more information and
    code samples."""
    __slots__ = ('__temperatureUnit', '__dayNormalization',
        '__customTestHeatingBaseTemperaturesOrNone',
        '__customTestCoolingBaseTemperaturesOrNone',
        '__extraPredictorSpecs', '__requestedRegressionSpecs')
    def __getCustomTempsOrNone(self,
            unit, # type: TemperatureUnit
            tempsOrNone, # type: Iterable[Temperature | float] | None
            paramName # type: str
            ): # type: (...) -> tuple[Temperature, ...] | None
        if tempsOrNone is None:
            return None
        cleaned = set() # type: set[Temperature]
        for temp in tempsOrNone:
            if type(temp) is Temperature:
                if temp.unit != unit:
                    raise ValueError('All %s items must be specified in %s, '
                        'the unit specified for this RegressionTestPlan.' %
                            (paramName, unit))
                cleaned.add(temp)
            else:
                try:
                    cleaned.add(Temperature(temp, unit))
                except TypeError:
                    _, e, _ = sys.exc_info() # for Python 2.5 compatibility
                    raise TypeError('Problem value in %s: %s' % (paramName, e))
                except ValueError:
                    _, e, _ = sys.exc_info()
                    raise ValueError('Problem value in %s: %s' % (paramName, e))
        return tuple(sorted(cleaned))
    def __init__(self,
            temperatureUnit, # type: TemperatureUnit
            dayNormalization=DayNormalization.WEIGHTED, # type: DayNormalization
            customTestHeatingBaseTemperaturesOrNone=None, # type: Iterable[Temperature | float] | None
            customTestCoolingBaseTemperaturesOrNone=None, # type: Iterable[Temperature | float] | None
            extraPredictorSpecs={}, # type: Mapping[str, ExtraPredictorSpec]
            requestedRegressionSpecs=() # type: Iterable[RegressionSpec]
            ): # type: (...) -> None
        self.__temperatureUnit = TemperatureUnit._check(temperatureUnit)
        self.__dayNormalization = DayNormalization._check(dayNormalization)
        self.__customTestHeatingBaseTemperaturesOrNone = \
            self.__getCustomTempsOrNone(temperatureUnit,
                customTestHeatingBaseTemperaturesOrNone,
                'customTestHeatingBaseTemperaturesOrNone')
        self.__customTestCoolingBaseTemperaturesOrNone = \
            self.__getCustomTempsOrNone(temperatureUnit,
                customTestCoolingBaseTemperaturesOrNone,
                'customTestCoolingBaseTemperaturesOrNone')
        # Create a defensive copy of the dict for usual reasons but also so the
        # default {} value cannot be modified for future calls.
        self.__extraPredictorSpecs = private.checkMappingAndReturnDictCopy(
            extraPredictorSpecs, 'extraPredictorSpecs')
        if len(self.__extraPredictorSpecs) > _MAX_EXTRA_PREDICTORS:
            raise ValueError('extraPredictorSpecs has %d extra predictors, when'
                ' the maximum allowed is %d.' %
                    (len(self.__extraPredictorSpecs), _MAX_EXTRA_PREDICTORS))
        for k, v in private.getDictItemsIterable(self.__extraPredictorSpecs):
            _checkExtraPredictorKey(k,
                'Problem key in extraPredictorSpecs dict.  ')
            ExtraPredictorSpec._check(v, 'A value in extraPredictorSpecs dict')
        # Use set to exclude duplicates.  In other libraries we sort, but the
        # order doesn't actually matter so let's keep it simple.
        self.__requestedRegressionSpecs = frozenset(requestedRegressionSpecs)
        for spec in self.__requestedRegressionSpecs:
            if type(spec) is not RegressionSpec:
                raise TypeError('requestedRegressionSpecs must contain only '
                    'RegressionSpec objects.')
            for key in spec.extraPredictorKeys:
                if not key in self.__extraPredictorSpecs:
                    raise ValueError('You have a requested RegressionSpec with '
                        'an extra-predictor key %s, but extraPredictorSpecs '
                        'does not contain an ExtraPredictorSpec for that '
                        'extra-predictor key.' % key)
        if (len(self.__requestedRegressionSpecs) >
                _MAX_REQUESTED_REGRESSION_SPECS):
            raise ValueError('requestedRegressionSpecs has %d items, when the '
                'maximum allowed is %d.' % (len(self.__requestedRegressionSpecs),
                    _MAX_REQUESTED_REGRESSION_SPECS))
        def count(tempsOrNone): # type: (tuple[Temperature, ...] | None) -> int
            if tempsOrNone is None:
                return 0
            return len(tempsOrNone)
        customHdd = count(self.__customTestHeatingBaseTemperaturesOrNone)
        customCdd = count(self.__customTestCoolingBaseTemperaturesOrNone)
        customTotal = customHdd + customCdd
        if (((self.__customTestHeatingBaseTemperaturesOrNone is None) !=
                (self.__customTestCoolingBaseTemperaturesOrNone is None)) and
                customTotal > _MAX_WITH_DEFAULT_CUSTOM_BASE_TEMPS):
            if self.__customTestHeatingBaseTemperaturesOrNone is not None:
                defined = "customTestHeatingBaseTemperaturesOrNone"
                leftDefault = "cooling"
            else:
                defined = "customTestCoolingBaseTemperaturesOrNone"
                leftDefault = "heating"
            raise ValueError('You have defined the %s and left the API to '
                'choose the test %s base temperatures automatically.  In this '
                'case the maximum number of %s allowed is %d, but you have '
                'defined %d which is too many.' % (defined, leftDefault,
                    defined, _MAX_WITH_DEFAULT_CUSTOM_BASE_TEMPS, customTotal))
        elif customTotal > _MAX_CUSTOM_BASE_TEMPS:
            raise ValueError('You have defined %d custom test heating base '
                'temperatures and %d custom test cooling base temperatures, '
                'making %d in total, which is greater than the maximum allowed '
                'total of %d.' % (customHdd, customCdd, customTotal,
                    _MAX_CUSTOM_BASE_TEMPS))
    def _equalityFields(self):
        return (self.__temperatureUnit, self.__dayNormalization,
            self.__customTestHeatingBaseTemperaturesOrNone,
            self.__customTestCoolingBaseTemperaturesOrNone,
            self.__extraPredictorSpecs, self.__requestedRegressionSpecs)
    def __hash__(self):
        h = hash((self.__class__, self.__temperatureUnit,
            self.__dayNormalization,
            self.__customTestHeatingBaseTemperaturesOrNone,
            self.__customTestCoolingBaseTemperaturesOrNone,
            self.__requestedRegressionSpecs))
        return private.getDictHash(self.__extraPredictorSpecs, h)
    @property
    def temperatureUnit(self): # type: () -> TemperatureUnit
        """The :py:class:`TemperatureUnit <degreedays.api.data.TemperatureUnit>`
        that specifies whether Celsius-based or Fahrenheit-based degree days
        should be used in regressions."""
        return self.__temperatureUnit
    @property
    def dayNormalization(self): # type: () -> DayNormalization
        """The :py:class:`DayNormalization` to be used in the regression
        process."""
        return self.__dayNormalization
    @property
    def customTestHeatingBaseTemperaturesOrNone(self):
        # type: () -> Sequence[Temperature] | None
        """The custom set of base temperatures to be used for the HDD in
        regressions tested by the API, or `None` if no such base temperatures
        are specified.

        If this is an empty :py:class:`Sequence`, the API will not include HDD
        in any of its test regressions (unless
        :py:attr:`requestedRegressionSpecs` specifies any regressions with HDD
        in them)."""
        return self.__customTestHeatingBaseTemperaturesOrNone
    @property
    def customTestCoolingBaseTemperaturesOrNone(self):
        # type: () -> Sequence[Temperature] | None
        """The custom set of base temperatures to be used for the CDD in
        regressions tested by the API, or `None` if no such base temperatures
        are specified.

        If this is an empty :py:class:`Sequence`, the API will not include CDD
        in any of its test regressions (unless
        :py:attr:`requestedRegressionSpecs` specifies any regressions with CDD
        in them)."""
        return self.__customTestCoolingBaseTemperaturesOrNone
    @property
    def extraPredictorKeys(self): # type: () -> Collection[str]
        """The possibly-empty :py:class:`Collection` of extra-predictor keys
        that this ``RegressionTestPlan`` has :py:class:`ExtraPredictorSpec`
        objects for."""
        return tuple(self.__extraPredictorSpecs)
    def getExtraPredictorSpec(self, key): # type: (str) -> ExtraPredictorSpec
        # Following will throw a KeyError if key isn't found.
        """Returns the :py:class:`ExtraPredictorSpec` associated with the 
        specified string `key`.

        :param str key: a string extra-predictor key.
        :raises TypeError: if `key` is not a `str`.
        :raises KeyError: if `key` isn't associated with an
            :py:class:`ExtraPredictorSpec` in this object."""
        private.checkString(key, 'key')
        return self.__extraPredictorSpecs[key]
    @property
    def requestedRegressionSpecs(self): # type: () -> Collection[RegressionSpec]
        """A possibly-empty :py:class:`Collection` of specifications for
        regressions that the API is specifically instructed to test and return
        (on top of any others that it will test and potentially return anyway).
        """
        return self.__requestedRegressionSpecs
    def __tempsStr(self, temps): # type: (tuple[Temperature, ...]) -> str
        return str([t.value for t in temps])[1:-1]
    def __str__(self):
        s = [] # type: list[str]
        s.append('RegressionTestPlan(%s' % self.__temperatureUnit)
        if self.__dayNormalization != DayNormalization.WEIGHTED:
            s.append(', %s' % self.__dayNormalization)
        if self.__customTestHeatingBaseTemperaturesOrNone is not None:
            s.append(', customTestHeatingBaseTemperatures(%s)' %
                self.__tempsStr(self.__customTestHeatingBaseTemperaturesOrNone))
        if self.__customTestCoolingBaseTemperaturesOrNone is not None:
            s.append(', customTestCoolingBaseTemperatures(%s)' %
                self.__tempsStr(self.__customTestCoolingBaseTemperaturesOrNone))
        if len(self.__extraPredictorSpecs) > 0:
            s.append(', extraPredictorSpecs(')
            for k, v in private.getDictItemsIterable(
                    self.__extraPredictorSpecs):
                s.append('%s(%s)' % (k, v._getInnerString()))
                s.append(', ')
            s[-1] = ')'
        if len(self.__requestedRegressionSpecs) > 0:
            s.append(', requestedRegressionSpecs(')
            for spec in self.__requestedRegressionSpecs:
                s.append('(')
                spec._appendInnerString(s)
                s.append(')')
                s.append(', ')
            s[-1] = ')'
        s.append(')')
        return ''.join(s)
    def __repr__(self):
        s = [] # type: list[str]
        s.append('RegressionTestPlan(%r' % self.__temperatureUnit)
        if self.__dayNormalization != DayNormalization.WEIGHTED:
            s.append(', dayNormalization=%r' % self.__dayNormalization)
        if self.__customTestHeatingBaseTemperaturesOrNone is not None:
            # Use %s instead of %r cos %r will add quotes around the string.
            s.append(', customTestHeatingBaseTemperaturesOrNone=(%s)' %
                self.__tempsStr(self.__customTestHeatingBaseTemperaturesOrNone))
        if self.__customTestCoolingBaseTemperaturesOrNone is not None:
            s.append(', customTestCoolingBaseTemperaturesOrNone=(%s)' %
                self.__tempsStr(self.__customTestCoolingBaseTemperaturesOrNone))
        if len(self.__extraPredictorSpecs) > 0:
            s.append(', extraPredictorSpecs=')
            s.append(repr(self.__extraPredictorSpecs))
        if len(self.__requestedRegressionSpecs) > 0:
            s.append(', requestedRegressionSpecs=')
            s.append(repr(self.__requestedRegressionSpecs))
        s.append(')')
        return ''.join(s)
    def _toXml(self): # type: () -> XmlElement
        e = XmlElement('RegressionTestPlan')
        e.newChild('TemperatureUnit').setValue(self.__temperatureUnit)
        e.newChild('DayNormalization').setValue(self.__dayNormalization)
        def addCustomTemps(temps, parent, name):
            # type: (tuple[Temperature, ...], XmlElement, str) -> None
            wrapper = XmlElement(name)
            for temp in temps:
                wrapper.newChild('T').setValue(temp._toNumericString())
            parent.addChild(wrapper)
        if self.__customTestHeatingBaseTemperaturesOrNone is not None:
            addCustomTemps(self.__customTestHeatingBaseTemperaturesOrNone, e,
                'CustomTestHeatingBaseTemperatures')
        if self.__customTestCoolingBaseTemperaturesOrNone is not None:
            addCustomTemps(self.__customTestCoolingBaseTemperaturesOrNone, e,
                'CustomTestCoolingBaseTemperatures')
        if len(self.__extraPredictorSpecs) > 0:
            epSpecs = e.newChild('ExtraPredictorSpecs')
            for k, v in private.getDictItemsIterable(
                    self.__extraPredictorSpecs):
                epSpecs.addChild(v._toXml(k))
        if len(self.__requestedRegressionSpecs) > 0:
            rSpecs = e.newChild('RequestedRegressionSpecs')
            for s in self.__requestedRegressionSpecs:
                rSpecs.addChild(s._toXml())
        return e
    @staticmethod
    def _check(param, paramName='regressionTestPlan'):
        # type: (RegressionTestPlan, str) -> RegressionTestPlan
        if type(param) is not RegressionTestPlan:
            raise TypeError(private.wrongTypeString(param, paramName,
                RegressionTestPlan))
        return param


class RegressionRequest(degreedays.api.Request):
    #1 inheritance-diagram:: RegressionRequest
    """Defines a request for the API to test regressions against the specified
    energy data (:py:class:`InputData`) using degree days from the specified
    :py:class:`Location <degreedays.api.data.Location>`.

    :param Location location: the location for which the API should generate
        degree days to use in the regressions it tests against the
        ``InputData``. 
    :param InputData inputData: the dated records of energy usage and any
        extra-predictor data to be used in the regressions tested by the API.
    :param RegressionTestPlan testPlan: defining how the API should test
        regressions against the ``InputData``.  Must have an
        :py:class:`ExtraPredictorSpec` for any extra-predictor keys used in
        `inputData`, and, if it has any
        :py:attr:`RegressionTestPlan.requestedRegressionSpecs`, they must not
        contain any extra-predictor keys that do not have data in `inputData`.
    :raises TypeError: if `location` is not a subclass of :py:class:`Location`,
        or if `inputData` is not an :py:class:`InputData` object, or if
        `testPlan` is not a :py:class:`RegressionTestPlan` object.
    :raises ValueError: if `inputData` contains extra-predictor data but 
        `testPlan` does not contain an :py:class:`ExtraPredictorSpec` for each
        extra-predictor key included, or if `testPlan` contains any
        :py:class:`RegressionSpec` in
        :py:attr:`RegressionTestPlan.requestedRegressionSpecs` with an
        extra-predictor key that does not have data in `inputData`.
        
    A successfully-processed ``RegressionRequest``, sent to the API via
    :py:meth:`RegressionApi.runRegressions(regressionRequest)
    <RegressionApi.runRegressions>`, will result in a
    :py:class:`RegressionResponse` containing a list of the regressions with the
    best statistical fit.

    See `www.degreedays.net/api/regression
    <https://www.degreedays.net/api/regression>`__ for more information and
    code samples."""
    __slots__ = ('__location', '__inputData', '__testPlan')
    def __init__(self, location, inputData, testPlan):
        # type: (Location, InputData, RegressionTestPlan) -> None
        self.__location = Location._check(location)
        self.__inputData = InputData._check(inputData)
        self.__testPlan = RegressionTestPlan._check(testPlan, 'testPlan')
        inputDataKeys = inputData.extraPredictorKeys
        testPlanKeys = testPlan.extraPredictorKeys
        for key in inputDataKeys:
            if not key in testPlanKeys:
                raise ValueError('inputData has data for extra-predictor key '
                    '%s but testPlan contains no ExtraPredictorSpec for that '
                    'key.' % key)
        for spec in testPlan.requestedRegressionSpecs:
            for key in spec.extraPredictorKeys:
                if not key in inputDataKeys:
                    raise ValueError('testPlan contains a requested Regression '
                        'spec with extra-predictor key %s but inputData does '
                        'not have any figures for that extra predictor.' % key)
    def _equalityFields(self):
        return (self.__location, self.__inputData, self.__testPlan)
    @property
    def location(self): # type: () -> Location
        """The :py:class:`Location <degreedays.api.data.Location>` for which the
        API should generate degree days to use in the regressions it tests
        against the :py:attr:`inputData`."""
        return self.__location
    @property
    def inputData(self): # type: () -> InputData
        """The :py:class:`InputData` containing the dated records of energy
        usage and any extra-predictor data to be used in the regressions tested
        by the API."""
        return self.__inputData
    @property
    def testPlan(self): # type: () -> RegressionTestPlan
        """The :py:class:`RegressionTestPlan` that defines how the API should
        test regressions against the :py:attr:`inputData`."""
        return self.__testPlan
    def __str__(self):
        return ('RegressionRequest(%s, %s, %s)' %
            (self.__location, self.__inputData, self.__testPlan))
    def __repr__(self):
        return ('RegressionRequest(%r, %r, %r)' %
            (self.__location, self.__inputData, self.__testPlan))
    def _toXml(self): # type: () -> XmlElement
        return XmlElement('RegressionRequest') \
            .addChild(self.__location._toXml()) \
            .addChild(self.__testPlan._toXml()) \
            .addChild(self.__inputData._toXml())
    @staticmethod
    def _check(param, paramName='regressionRequest'):
        # type: (RegressionRequest, str) -> RegressionRequest
        if type(param) is not RegressionRequest:
            raise TypeError(private.wrongTypeString(
                param, paramName, RegressionRequest))
        return param


def _checkStandardError(param, paramName): # type: (float, str) -> float
    private.checkNumeric(param, paramName)
    if param < 0:
        raise ValueError('Invalid %s value (%g) - cannot be less than 0.' %
            (param, paramName))
    return param


class RegressionComponent(_Immutable):
    #1 inheritance-diagram:: RegressionComponent BaseloadRegressionComponent
    #   DegreeDaysRegressionComponent ExtraRegressionComponent
    """Contains details of a regression component e.g. the baseload (``b*days``)
    or the heating (``h*HDD``) component in a regression like
    ``E = b*days + h*HDD``"""
    __slots__ = ('__coefficient', '__coefficientStandardError',
        '__coefficientPValue')
    def __init__(self, coefficient, coefficientStandardError,
            coefficientPValue):
        # type: (float, float, float) -> None
        self.__coefficient = private.checkNumeric(coefficient, 'coefficient')
        self.__coefficientStandardError = _checkStandardError(
            coefficientStandardError, 'coefficientStandardError')
        private.checkNumeric(coefficientPValue, 'coefficientPValue')
        if coefficientPValue > 1 or coefficientPValue < 0:
            raise ValueError('Invalid coefficientPValue (%g) - cannot be less '
                'than 0 or greater than 1.' % coefficientPValue)
        self.__coefficientPValue = coefficientPValue
    def _equalityFieldsExtra(self): # type: () -> tuple[object, ...]
        raise NotImplementedError()
    def _equalityFields(self):
        return (self.__coefficient, self.__coefficientStandardError,
            self.__coefficientPValue) + self._equalityFieldsExtra()
    @property
    def coefficient(self): # type: () -> float
        """The coefficient of this regression component e.g. the ``b``, ``h``,
        or ``c`` (depending on the component in question) in a regression with
        an equation like ``E = b*days + h*HDD + c*CDD``"""
        return self.__coefficient
    @property
    def coefficientStandardError(self): # type: () -> float
        """The standard error of the :py:attr:`coefficient`. This is a measure
        of the precision of the regression model's estimate of the coefficient
        value. It's a common statistic (not energy specific) that you can look
        up online."""
        return self.__coefficientStandardError
    @property
    def coefficientPValue(self): # type: () -> float
        """The p-value of the :py:attr:`coefficient`. It can have values between
        0 (best) and 1 (worst), and you can use it as an indication of whether
        there is likely to be a meaningful relationship between the component
        and energy consumption. People often look for p-values of 0.05 or less,
        but really it is a sliding scale. p-value is a common statistic (not
        energy specific) that you can look up online.

        Note that, for a :py:class:`BaseloadRegressionComponent` the p-value is
        usually high if the coefficient is small, so it's often not as useful as
        the other p-values when assessing the quality of a regression."""
        return self.__coefficientPValue
    def _appendFormula(self, s): # type: (list[str]) -> None
        # Don't use the +- together unicode symbol cos it causes too many
        # problems in python 2.
        s.append('%g[+-%.4g,p=%.4g]' % (self.__coefficient,
            self.__coefficientStandardError, self.__coefficientPValue))


class BaseloadRegressionComponent(RegressionComponent):
    #1 inheritance-diagram:: BaseloadRegressionComponent
    """Contains details of the baseload component (non-weather-dependent energy
    usage) in a regression."""
    __slots__ = ('__multiplyByNumberOfDays',)
    def __init__(self, coefficient, coefficientStandardError, coefficientPValue,
            multiplyByNumberOfDays):
        # type: (float, float, float, bool) -> None
        super(BaseloadRegressionComponent, self).__init__(
            coefficient, coefficientStandardError, coefficientPValue)
        self.__multiplyByNumberOfDays = private.checkBoolean(
            multiplyByNumberOfDays, 'multiplyByNumberOfDays')
    def _equalityFieldsExtra(self):
        return (self.__multiplyByNumberOfDays,)
    @property
    def multiplyByNumberOfDays(self): # type: () -> bool
        """`True` if the baseload :py:attr:`coefficient
        <RegressionComponent.coefficient>` is a per-day value that should be
        multiplied by the number of days covered by the period in question; or
        `False` if the coefficient is such that it will only work for periods of
        the same length used in the :py:class:`InputData`.

        For the baseload component this will always be `True` unless you ran
        regressions with :py:attr:`DayNormalization.NONE`.
        
        The `notes on day normalization for our online regression tool
        <https://www.degreedays.net/regression#day-normalization>`__ have
        example regression equations that should help make this clearer."""
        return self.__multiplyByNumberOfDays
    def __str__(self):
        s = [] # type: list[str]
        s.append('BaseloadRegressionComponent(')
        self._appendFormula(s)
        if self.__multiplyByNumberOfDays:
            s.append(' * days')
        s.append(')')
        return ''.join(s)
    def __repr__(self):
        return ('BaseloadRegressionComponent(%r, %r, %r, %r)' %
            (self.coefficient, self.coefficientStandardError,
                self.coefficientPValue, self.__multiplyByNumberOfDays))
    @staticmethod
    def _check(param, paramName='baseload'):
        # type: (BaseloadRegressionComponent, str) -> BaseloadRegressionComponent
        if type(param) is not BaseloadRegressionComponent:
            raise TypeError(private.wrongTypeString(param, paramName,
                BaseloadRegressionComponent))
        return param


class ExtraRegressionComponent(RegressionComponent):
    #1 inheritance-diagram:: ExtraRegressionComponent
    """Contains details of an extra-predictor component in a regression."""
    __slots__ = ('__multiplyByNumberOfDays',)
    def __init__(self, coefficient, coefficientStandardError, coefficientPValue,
            multiplyByNumberOfDays):
        # type: (float, float, float, bool) -> None
        super(ExtraRegressionComponent, self).__init__(
            coefficient, coefficientStandardError, coefficientPValue)
        self.__multiplyByNumberOfDays = private.checkBoolean(
            multiplyByNumberOfDays, 'multiplyByNumberOfDays')
    def _equalityFieldsExtra(self):
        return (self.__multiplyByNumberOfDays,)
    @property
    def multiplyByNumberOfDays(self): # type: () -> bool
        """`True` if the :py:attr:`coefficient
        <RegressionComponent.coefficient>` is a per-day value that should be
        multiplied by the number of days covered by the period in question;
        `False` otherwise.

        This will be `True` for extra predictors with
        :py:attr:`PredictorType.AVERAGE`, and `False` for extra predictors with
        :py:attr:`PredictorType.CUMULATIVE`."""
        return self.__multiplyByNumberOfDays
    def __str__(self):
        s = [] # type: list[str]
        s.append('ExtraRegressionComponent(')
        self._appendFormula(s)
        if self.__multiplyByNumberOfDays:
            s.append(' * days')
        s.append(')')
        return ''.join(s)
    def __repr__(self):
        return ('ExtraRegressionComponent(%r, %r, %r, %r)' %
            (self.coefficient, self.coefficientStandardError,
                self.coefficientPValue, self.__multiplyByNumberOfDays))
    @staticmethod
    def _check(param, paramName):
        # type: (ExtraRegressionComponent, str) -> ExtraRegressionComponent
        if type(param) is not ExtraRegressionComponent:
            raise TypeError(private.wrongTypeString(param, paramName,
                ExtraRegressionComponent))
        return param


class DegreeDaysRegressionComponent(RegressionComponent):
    #1 inheritance-diagram:: DegreeDaysRegressionComponent
    """Contains details of a heating or cooling component in a regression, with
    the base temperature and degree days used, as well as the usual coefficient
    and stats."""
    __slots__ = ('__baseTemperature', '__sampleDegreeDaysDataSet',
        '__sampleDegreeDaysTotal')
    def __init__(self,
            coefficient, # type: float
            coefficientStandardError, # type: float
            coefficientPValue, # type: float
            baseTemperature, # type: Temperature
            sampleDegreeDaysDataSet, # type: DatedDataSet
            sampleDegreeDaysTotal # type: DataValue
            ): # type: (...) -> None
        super(DegreeDaysRegressionComponent, self).__init__(
            coefficient, coefficientStandardError, coefficientPValue)
        self.__baseTemperature = Temperature._check(
            baseTemperature, 'baseTemperature')
        self.__sampleDegreeDaysDataSet = DatedDataSet._check(
            sampleDegreeDaysDataSet, 'sampleDegreeDaysDataSet')
        self.__sampleDegreeDaysTotal = DataValue._check(
            sampleDegreeDaysTotal, 'sampleDegreeDaysTotal')
    def _equalityFieldsExtra(self):
        return (self.__baseTemperature, self.__sampleDegreeDaysTotal,
            self.__sampleDegreeDaysDataSet)
    @property
    def baseTemperature(self): # type: () -> Temperature
        """The base temperature of the degree days this regression component was
        calculated with."""
        return self.__baseTemperature
    @property
    def sampleDegreeDaysDataSet(self): # type: () -> DatedDataSet
        """The :py:class:`DatedDataSet <degreedays.api.data.DatedDataSet>` of
        the degree days this regression component was calculated with."""
        return self.__sampleDegreeDaysDataSet
    @property
    def sampleDegreeDaysTotal(self): # type: () -> DataValue
        """The :py:class:`DataValue <degreedays.api.data.DataValue>`
        representing the total number of degree days across all the periods this
        regression component was calculated for.

        This will have a value equal to the total of all the degree-day values
        in :py:attr:`sampleDegreeDaysDataSet`."""
        return self.__sampleDegreeDaysTotal
    def __str__(self):
        s = [] # type: list[str]
        s.append('DegreeDaysRegressionComponent(')
        self._appendFormula(s)
        s.append(', base %s, %s, total %s)' % (self.__baseTemperature,
            self.__sampleDegreeDaysDataSet, self.__sampleDegreeDaysTotal))
        return ''.join(s)
    def __repr__(self):
        return ('DegreeDaysRegressionComponent(%r, %r, %r, %r, %r, %r)' %
            (self.coefficient, self.coefficientStandardError,
                self.coefficientPValue, self.__baseTemperature,
                self.__sampleDegreeDaysDataSet, self.__sampleDegreeDaysTotal))
    @staticmethod
    def _check(param, paramName):
        # type: (DegreeDaysRegressionComponent, str) -> DegreeDaysRegressionComponent
        if type(param) is not DegreeDaysRegressionComponent:
            raise TypeError(private.wrongTypeString(param, paramName,
                DegreeDaysRegressionComponent))
        return param

# This class exists only to simplify the __init__ method of Regression.
class RegressionComponents(_Immutable):
    """Contains all the :py:class:`RegressionComponent` objects in a
    :py:class:`Regression`."""
    __slots__ = ('__baseload', '__heatingDegreeDaysOrNone',
        '__coolingDegreeDaysOrNone', '__extras')
    def __init__(self,
            baseload, # type: BaseloadRegressionComponent
            heatingDegreeDaysOrNone=None, # type: DegreeDaysRegressionComponent | None
            coolingDegreeDaysOrNone=None, # type: DegreeDaysRegressionComponent | None
            extras={} # type: Mapping[str, ExtraRegressionComponent]
            ): # type: (...) -> None
        self.__baseload = BaseloadRegressionComponent._check(baseload)
        if heatingDegreeDaysOrNone is None:
            self.__heatingDegreeDaysOrNone = None
        else:
            self.__heatingDegreeDaysOrNone = \
                DegreeDaysRegressionComponent._check(
                    heatingDegreeDaysOrNone, 'heatingDegreeDaysOrNone')
        if coolingDegreeDaysOrNone is None:
            self.__coolingDegreeDaysOrNone = None
        else:
            self.__coolingDegreeDaysOrNone = \
                DegreeDaysRegressionComponent._check(
                    coolingDegreeDaysOrNone, 'coolingDegreeDaysOrNone')
        if self.__heatingDegreeDaysOrNone is not None and \
                self.__coolingDegreeDaysOrNone is not None and \
                (self.__heatingDegreeDaysOrNone.baseTemperature.unit !=
                    self.__coolingDegreeDaysOrNone.baseTemperature.unit):
            raise ValueError('The heating degree days and cooling degree days '
                'must have the same temperature unit.')                
        # Create a defensive copy of the dict for usual reasons but also so the
        # default {} value cannot be modified for future calls.
        self.__extras = private.checkMappingAndReturnDictCopy(extras, 'extras')
        if len(self.__extras) > _MAX_EXTRA_PREDICTORS:
            raise ValueError('extras has %d extra components, when'
                ' the maximum allowed is %d.' %
                    (len(self.__extras), _MAX_EXTRA_PREDICTORS))
        for k, v in private.getDictItemsIterable(self.__extras):
            _checkExtraPredictorKey(k,
                'Problem key in extraPredictorSpecs dict.  ')
            ExtraRegressionComponent._check(v, 'A value in extras dict')
    def _equalityFields(self):
        return (self.__baseload, self.__heatingDegreeDaysOrNone,
            self.__coolingDegreeDaysOrNone, self.__extras)
    def __hash__(self):
        h = hash((self.__class__, self.__baseload,
            self.__heatingDegreeDaysOrNone, self.__coolingDegreeDaysOrNone))
        return private.getDictHash(self.__extras, h)
    @property
    def baseload(self): # type: () -> BaseloadRegressionComponent
        """The :py:class:`BaseloadRegressionComponent` object representing the
        baseload component (``b*days``) of the regression."""
        return self.__baseload
    @property
    def heatingDegreeDaysOrNone(self):
        """The :py:class:`DegreeDaysRegressionComponent` object representing the
        heating-degree-days component (``h*HDD``) of the regression, or `None`
        if no such component exists."""
        # type: () -> DegreeDaysRegressionComponent | None
        return self.__heatingDegreeDaysOrNone
    @property
    def coolingDegreeDaysOrNone(self):
        """The :py:class:`DegreeDaysRegressionComponent` object representing the
        cooling-degree-days component (``c*CDD``) of the regression, or `None`
        if no such component exists."""
        # type: () -> DegreeDaysRegressionComponent | None
        return self.__coolingDegreeDaysOrNone
    @property
    def extraPredictorKeys(self): # type: () -> Collection[str]
        """The possibly-empty :py:class:`Collection` of extra-predictor keys
        that the regression has extra components for.

        Remember that, in the usual case, if you provide extra-predictor data to
        the API, it will test regressions both with and without each extra
        predictor, and this will be reflected in the regressions you get back in
        the response.

        See also: :py:meth:`getExtraComponent`"""
        # Like elsewhere, use a tuple to maintain order, as in Python 3.7+ the
        # dict will maintain order by default.
        return tuple(self.__extras)
    @property
    def spec(self): # type: () -> RegressionSpec
        """The :py:class:`RegressionSpec` specifying the components that this
        object contains, such that a :py:class:`Regression` with equivalent
        components can be requested in another API request.
        
        See `how to request specific regressions to be returned
        <https://www.degreedays.net/api/regression#requested>`__."""
        hdd = None
        cdd = None
        if self.__heatingDegreeDaysOrNone is not None:
            hdd = self.__heatingDegreeDaysOrNone.baseTemperature
        if self.__coolingDegreeDaysOrNone is not None:
            cdd = self.__coolingDegreeDaysOrNone.baseTemperature
        return RegressionSpec(heatingBaseTemperatureOrNone=hdd,
            coolingBaseTemperatureOrNone=cdd,
            extraPredictorKeys=self.extraPredictorKeys)
    def hasExtraComponent(self, extraPredictorKey): # type: (str) -> bool
        """Returns `True` if the regression has an extra-predictor component
        with the specified `extraPredictorKey`; `False` otherwise.

        Remember that, in the usual case, if you provide extra-predictor data to
        the API, it will test regressions both with and without each extra
        predictor, and this will be reflected in the regressions you get back in
        the response.

        :param str extraPredictorKey: the string key that you used to identify
            the extra predictor in the :py:class:`InputData` of your request.
        :raises TypeError: if `extraPredictorKey` is not a `str`.

        See also: :py:meth:`getExtraComponent`, :py:attr:`extraPredictorKeys`"""
        private.checkString(extraPredictorKey, 'extraPredictorKey')
        return extraPredictorKey in self.__extras
    def getExtraComponent(self, extraPredictorKey):
        # type: (str) -> ExtraRegressionComponent
        """Returns the :py:class:`ExtraRegressionComponent` object with the
        specified `extraPredictorKey`, or throws a :py:class:`KeyError` if no
        such component exists in the regression (check
        :py:meth:`hasExtraComponent` before calling this).

        Remember that, in the usual case, if you provide extra-predictor data to
        the API, it will test regressions both with and without each extra
        predictor, and this will be reflected in the regressions you get back in
        the response.

        :param str extraPredictorKey: the string key that you used to identify
            the extra predictor in the :py:class:`InputData` of your request.
        :raises TypeError: if `extraPredictorKey` is not a `str`.
        :raises KeyError: if the regression does not have an extra-predictor
            component with the specified `extraPredictorKey`.

        See also: :py:meth:`hasExtraComponent`, :py:attr:`extraPredictorKeys`"""
        private.checkString(extraPredictorKey, 'extraPredictorKey')
        # Following will throw a KeyError if key isn't found.
        return self.__extras[extraPredictorKey]
    def __appendDegreeDays(self, s, component, name):
        # type: (list[str], DegreeDaysRegressionComponent, str) -> None
        s.append('(')
        component._appendFormula(s)
        s.append(' * %s%s[%s])' % (name,
            str(component.baseTemperature).replace(' ', ''),
            component.sampleDegreeDaysTotal))
    def __str__(self):
        s = [] # type: list[str]
        s.append('E = ')
        if self.__baseload.multiplyByNumberOfDays:
            s.append('(')
        self.__baseload._appendFormula(s)
        if self.__heatingDegreeDaysOrNone is not None:
            s.append(' + ')
            self.__appendDegreeDays(s, self.__heatingDegreeDaysOrNone, 'HDD')
        if self.__coolingDegreeDaysOrNone is not None:
            s.append(' + ')
            self.__appendDegreeDays(s, self.__coolingDegreeDaysOrNone, 'CDD')
        for k, v in private.getDictItemsIterable(self.__extras):
            s.append(' + (')
            v._appendFormula(s)
            s.append(' * ')
            s.append(k)
            if v.multiplyByNumberOfDays:
                s.append(' * days')
            s.append(')')
        return ''.join(s)
    def __repr__(self):
        s = [] # type: list[str]
        s.append('RegressionComponents(%r' % self.__baseload)
        if self.__heatingDegreeDaysOrNone is not None:
            s.append(', heatingDegreeDaysOrNone=%r' %
                self.__heatingDegreeDaysOrNone)
        if self.__coolingDegreeDaysOrNone is not None:
            s.append(', coolingDegreeDaysOrNone=%r' %
                self.coolingDegreeDaysOrNone)
        if len(self.__extras) > 0:
            s.append(', extras=%r' % self.__extras)
        s.append(')')
        return ''.join(s)
    @staticmethod
    def _check(param, paramName='components'):
        # type: (RegressionComponents, str) -> RegressionComponents
        if type(param) is not RegressionComponents:
            raise TypeError(private.wrongTypeString(param, paramName,
                RegressionComponents))
        return param


def _checkRSquared(param, paramName): # type: (float, str) -> float
    private.checkNumeric(param, paramName)
    if param > 1:
        raise ValueError('Invalid %s (%g) - cannot be greater than 1.' %
            (paramName, param))
    return param


class Regression(_Immutable):
    """Contains details of a regression model that the API calculated using the
    :py:class:`InputData` you provided and, typically, HDD and/or CDD as well.
    """
    __slots__ = ('__tags', '__components', '__sampleSize', '__sampleDays',
        '__sampleSpan', '__rSquared', '__adjustedRSquared',
        '__crossValidatedRSquared', '__standardError', '__cvrmse')
    def __init__(self,
            tags, # type: Iterable[RegressionTag]
            components, # type: RegressionComponents
            sampleSize, # type: int
            sampleDays, # type: int
            sampleSpan, # type: degreedays.time.DayRange
            rSquared, # type: float
            adjustedRSquared, # type: float
            crossValidatedRSquared, # type: float
            standardError, # type: float
            cvrmse # type: float
            ): # type: (...) -> None
        tagsTuple = private.checkTupleItems(
            tuple(tags), RegressionTag._check, 'tags')
        self.__tags = frozenset(tagsTuple)
        self.__components = RegressionComponents._check(components)
        self.__sampleSize = private.checkInt(sampleSize, 'sampleSize')
        if self.__sampleSize <= 0:
            raise ValueError(
                'Invalid sampleSize (%d) - must be greater than 0.' %
                    self.__sampleSize)
        self.__sampleDays = private.checkInt(sampleDays, 'sampleDays')
        if self.__sampleDays <= 0:
            raise ValueError(
                'Invalid sampleDays (%d) - must be greater than 0.' %
                    self.__sampleDays)
        self.__sampleSpan = degreedays.time.DayRange._check(
            sampleSpan, 'sampleSpan')
        if sampleDays > len(sampleSpan):
            raise ValueError('sampleDays cannot be %d when the sampleSpan (%s) '
                'is %d days long.' % (self.__sampleDays, self.__sampleSpan,
                    len(self.__sampleSpan)))
        self.__rSquared = _checkRSquared(rSquared, 'rSquared')
        self.__adjustedRSquared = _checkRSquared(
            adjustedRSquared, 'adjustedRSquared')
        self.__crossValidatedRSquared = _checkRSquared(
            crossValidatedRSquared, 'crossValidatedRSquared')
        self.__standardError = _checkStandardError(
            standardError, 'standardError')
        self.__cvrmse = private.checkNumeric(cvrmse, 'cvrmse')
    def _equalityFields(self):
        # tags are not included cos they are like metadata
        return (self.__components, self.__sampleSize,
            self.__sampleDays, self.__sampleSpan, self.__rSquared,
            self.__adjustedRSquared, self.__crossValidatedRSquared,
            self.__standardError, self.__cvrmse)
    @property
    def tags(self): # type: () -> Collection[RegressionTag]
        """A :py:class:`Collection` of the tags that describe how this
        ``Regression`` came to be included in the response from the API."""
        return self.__tags
    def hasTag(self, regressionTag): # type: (RegressionTag) -> bool
        """Returns `True` if this ``Regression`` contains the specified
        `regressionTag`; `False` otherwise.

        :param RegressionTag regressionTag: the :py:class:`RegressionTag` that's
            presence in this ``Regression`` is to be tested.
        :raises TypeError: if `regressionTag` is not a
            :py:class:`RegressionTag`.

        See also: :py:attr:`tags`"""
        RegressionTag._check(regressionTag)
        return regressionTag in self.__tags
    @property
    def baseload(self): # type: () -> BaseloadRegressionComponent
        """The :py:class:`BaseloadRegressionComponent` object representing the
        baseload component (``b*days``) of this ``Regression``."""
        return self.__components.baseload
    @property
    def heatingDegreeDaysOrNone(self):
        # type: () -> DegreeDaysRegressionComponent | None
        """The :py:class:`DegreeDaysRegressionComponent` object representing the
        heating-degree-days component (``h*HDD``) of this ``Regression``, or
        `None` if no such component exists."""
        return self.__components.heatingDegreeDaysOrNone
    @property
    def coolingDegreeDaysOrNone(self):
        # type: () -> DegreeDaysRegressionComponent | None
        """The :py:class:`DegreeDaysRegressionComponent` object representing the
        cooling-degree-days component (``c*CDD``) of this ``Regression``, or
        `None` if no such component exists."""
        return self.__components.coolingDegreeDaysOrNone
    @property
    def extraPredictorKeys(self): # type: () -> Collection[str]
        """The possibly-empty :py:class:`Collection` of extra-predictor keys
        that this ``Regression`` has extra components for.

        Remember that, in the usual case, if you provide extra-predictor data to
        the API, it will test regressions both with and without each extra
        predictor, and this will be reflected in the regressions you get back in
        the response.

        See also: :py:meth:`getExtraComponent`"""
        return self.__components.extraPredictorKeys
    def hasExtraComponent(self, extraPredictorKey): # type: (str) -> bool
        """Returns `True` if this ``Regression`` has an extra-predictor
        component with the specified `extraPredictorKey`; `False` otherwise.

        Remember that, in the usual case, if you provide extra-predictor data to
        the API, it will test regressions both with and without each extra
        predictor, and this will be reflected in the regressions you get back in
        the response.

        :param str extraPredictorKey: the string key that you used to identify
            the extra predictor in the :py:class:`InputData` of your request.
        :raises TypeError: if `extraPredictorKey` is not a `str`.

        See also: :py:meth:`getExtraComponent`, :py:attr:`extraPredictorKeys`"""
        return self.__components.hasExtraComponent(extraPredictorKey)
    def getExtraComponent(self, extraPredictorKey):
        # type: (str) -> ExtraRegressionComponent
        """Returns the :py:class:`ExtraRegressionComponent` object with the
        specified `extraPredictorKey`, or throws a :py:class:`KeyError` if no
        such component exists in this ``Regression`` (check
        :py:meth:`hasExtraComponent` before calling this).

        Remember that, in the usual case, if you provide extra-predictor data to
        the API, it will test regressions both with and without each extra
        predictor, and this will be reflected in the regressions you get back in
        the response.

        :param str extraPredictorKey: the string key that you used to identify
            the extra predictor in the :py:class:`InputData` of your request.
        :raises TypeError: if `extraPredictorKey` is not a `str`.
        :raises KeyError: if this ``Regression`` does not have an
            extra-predictor component with the specified `extraPredictorKey`.

        See also: :py:meth:`hasExtraComponent`, :py:attr:`extraPredictorKeys`"""
        return self.__components.getExtraComponent(extraPredictorKey)
    @property
    def sampleSize(self): # type: () -> int
        """The number of energy-usage figures used for this ``Regression``. This
        could be less than the number of input periods included in your request
        if the location could not provide enough weather data to cover all of
        them."""
        return self.__sampleSize
    @property
    def sampleDays(self): # type: () -> int
        """The number of days covered by the sample of data used for this
        ``Regression``, excluding any gaps between input periods."""
        return self.__sampleDays
    @property
    def sampleSpan(self): # type: () -> degreedays.time.DayRange
        """The :py:class:`DayRange <degreedays.time.DayRange>` representing the
        full period covered by the sample (including any gaps) that was used for
        this ``Regression``. This could be shorter than the full range of the
        :py:class:`InputData` sent in your request, if the location could not
        provide enough weather data to cover it all."""
        return self.__sampleSpan
    @property
    def sampleSpanDays(self): # type: () -> int
        """The number of days covered by the sample (including any gaps) that
        was used for this ``Regression``. This could be shorter than the number
        of days covered by the :py:class:`InputData` sent in your request, if
        the location could not provide enough weather data to cover it all."""
        return len(self.__sampleSpan)
    @property
    def standardError(self): # type: () -> float
        """The standard error of this ``Regression``. 

        You can read more about this and the other statistics in the
        `docs for our online regression tool
        <https://www.degreedays.net/regression#interpretation>`__ (which uses
        this API internally)."""
        return self.__standardError
    @property
    def rSquared(self): # type: () -> float
        """The R-squared value for this ``Regression``. 

        You can read more about this and the other statistics in the
        `docs for our online regression tool
        <https://www.degreedays.net/regression#interpretation>`__ (which uses
        this API internally)."""
        return self.__rSquared
    @property
    def adjustedRSquared(self): # type: () -> float
        """The adjusted-R-squared value for this ``Regression``. 

        You can read more about this and the other statistics in the
        `docs for our online regression tool
        <https://www.degreedays.net/regression#interpretation>`__ (which uses
        this API internally)."""
        return self.__adjustedRSquared
    @property
    def crossValidatedRSquared(self): # type: () -> float
        """The cross-validated-R-squared value for this ``Regression``. 

        You can read more about this and the other statistics in the
        `docs for our online regression tool
        <https://www.degreedays.net/regression#interpretation>`__ (which uses
        this API internally)."""
        return self.__crossValidatedRSquared
    @property
    def cvrmse(self): # type: () -> float
        """The CVRMSE of this ``Regression``. 

        You can read more about this and the other statistics in the
        `docs for our online regression tool
        <https://www.degreedays.net/regression#interpretation>`__ (which uses
        this API internally)."""
        return self.__cvrmse
    @property
    def spec(self): # type: () -> RegressionSpec
        """The :py:class:`RegressionSpec` specifying the components that this
        ``Regression`` contains, such that an equivalent ``Regression`` can be
        requested in another API request.
        
        See `how to request specific regressions to be returned
        <https://www.degreedays.net/api/regression#requested>`__."""
        return self.__components.spec
    def __str__(self):
        s = [] # type: list[str]
        s.append('Regression(%s, R2=%g, adj-R2=%g, cv-R2=%g, S=%g, CVRMSE=%g, '
            'from a sample of %d values covering ' % (self.__components,
                self.__rSquared, self.__adjustedRSquared,
                self.__crossValidatedRSquared, self.__standardError,
                self.__cvrmse, self.__sampleSize))
        sampleSpanDays = self.sampleSpanDays
        if sampleSpanDays == self.__sampleDays:
            s.append('all %d' % self.__sampleDays)
        else:
            s.append('%d of the %d' % (self.__sampleDays, sampleSpanDays))
        s.append(' days within %s)' % self.__sampleSpan)
        return ''.join(s)
    def __repr__(self):
        return ('Regression(%r, %r, %d, %d, %r, %r, %r, %r, %r, %r)' %
            (self.__tags, self.__components, self.__sampleSize,
                self.__sampleDays, self.__sampleSpan,
                self.__rSquared, self.__adjustedRSquared,
                self.__crossValidatedRSquared, self.__standardError,
                self.__cvrmse))
    @staticmethod
    def _check(param, paramName): # type: (Regression, str) -> Regression
        if type(param) is not Regression:
            raise TypeError(private.wrongTypeString(
                param, paramName, Regression))
        return param

class RegressionResponse(degreedays.api.Response):
    #1 inheritance-diagram:: RegressionResponse
    """Contains a selection of the regressions that the API tested against your
    :py:class:`RegressionRequest`, with the :py:class:`Regression` that gave the
    best statistical fit listed first.

    To get a ``RegressionResponse``, you would send a
    :py:class:`RegressionRequest` to the API via
    :py:meth:`RegressionApi.runRegressions(regressionRequest)
    <RegressionApi.runRegressions>`.  See `www.degreedays.net/api/regression
    <https://www.degreedays.net/api/regression>`__ for more information and
    code samples."""
    __slots__ = ('__metadata', '__stationId', '__targetLongLat', '__sources',
        '__regressionsResult')
    def __init__(self,
            metadata, # type: degreedays.api.ResponseMetadata
            stationId, # type: str
            targetLongLat, # type: degreedays.geo.LongLat
            sources, # type: Iterable[Source]
            regressionsOrFailure # type: Iterable[Regression] | degreedays.api.Failure
            ): # type: (...) -> None
        self.__metadata =  degreedays.api.ResponseMetadata._check(
            metadata, 'metadata')
        self.__stationId = private.checkStationId(stationId, False)
        self.__targetLongLat = degreedays.geo.LongLat._check(
            targetLongLat, 'targetLongLat')
        self.__sources = private.checkTupleItems(
            tuple(sources), Source._check, 'sources')
        if isinstance(regressionsOrFailure, degreedays.api.Failure):
            # Use isinstance for type compiler, but _check to prevent subclass
            degreedays.api.Failure._check(regressionsOrFailure)
            self.__regressionsResult = regressionsOrFailure
        else:
            self.__regressionsResult = private.checkTupleItems(
                tuple(regressionsOrFailure), Regression._check,
                'regressionsOrFailure')
    def _equalityFields(self):
        # metadata isn't included in equality check.
        return (self.__stationId, self.__targetLongLat, self.__sources,
            self.__regressionsResult)
    @property
    def metadata(self): # type: () -> degreedays.api.ResponseMetadata
        return self.__metadata
    @property
    def stationId(self): # type: () -> str
        """The non-empty canonical ID of the weather station or combination of
        weather stations that supplied the temperature data used to calculate
        the degree days used for the regressions in this response.  If this
        response does not actually contain any regressions, this will be the ID
        of the weather station that *would* have been used if it had had enough
        data to run regressions against the :py:class:`InputData` provided in
        the request.

        If the :py:class:`Location <degreedays.api.data.Location>` in the
        :py:class:`RegressionRequest` was a :py:class:`StationIdLocation
        <degreedays.api.data.impl.StationIdLocation>` (created via
        :py:meth:`Location.stationId <degreedays.api.data.Location.stationId>`),
        this method will simply return the canonical form of that weather
        station's ID. We say "canonical" because it's possible for a station ID
        to be expressed in more than one way, like upper case or lower case. The
        canonical form of the station ID is the form that you should display in
        a UI or store in a database if appropriate.

        If the :py:class:`Location <degreedays.api.data.Location>` in the
        :py:class:`RegressionRequest` was a :py:class:`GeographicLocation
        <degreedays.api.data.GeographicLocation>`, then:

        * If the degree days used in the regressions were calculated using
          temperature data from a single station (the usual case), this method
          will return the canonical form of that station's ID.
        * If the degree days used in the regressions were calculated using
          temperature data combined from multiple stations (something that the
          API might optionally start doing at some point in the future), this
          method will return the ID of a "virtual station" that represents the
          specific combination of weather stations used.

        Either way, the station ID returned by this method can be used to run
        more regressions or fetch more data from the same station(s) that were
        used to generate the degree days used for the regressions in this
        response. For example, you might want to start off using a
        :py:class:`GeographicLocation <degreedays.api.data.GeographicLocation>`
        initially, and then use the returned station ID to fetch more data or
        run more regressions using the same station."""
        return self.__stationId
    @property
    def targetLongLat(self): # type: () -> degreedays.geo.LongLat
        """The :py:class:`degreedays.geo.LongLat` object that specifies the
        geographic position of the :py:class:`Location
        <degreedays.api.data.Location>` from the :py:class:`RegressionRequest`
        that led to this response.

        If the :py:class:`Location <degreedays.api.data.Location>` from the
        request was a :py:class:`PostalCodeLocation
        <degreedays.api.data.impl.PostalCodeLocation>` (created via
        :py:meth:`Location.postalCode
        <degreedays.api.data.Location.postalCode>`), this will be the
        ``LongLat`` that the API determined to be the central point of that
        postal code.

        If the :py:class:`Location <degreedays.api.data.Location>` from the
        request was a :py:class:`StationIdLocation
        <degreedays.api.data.impl.StationIdLocation>` (created via
        :py:meth:`Location.stationId <degreedays.api.data.Location.stationId>`),
        this will be the ``LongLat`` of that station (also accessible through
        :py:attr:`sources`).

        If the :py:class:`Location <degreedays.api.data.Location>` from the
        request was a :py:class:`LongLatLocation
        <degreedays.api.data.impl.LongLatLocation>` (created via
        :py:meth:`Location.longLat <degreedays.api.data.Location.longLat>`),
        this will simply be the ``LongLat`` that was originally specified. (Bear
        in mind that the longitude and latitude may have been rounded slightly
        between the request and the response. Such rounding would only introduce
        very small differences that would be insignificant as far as the
        real-world position is concerned, but it's worth bearing this in mind in
        case you are comparing for equality the returned ``LongLat`` with the
        ``LongLat`` from the request. The two positions will be close, but they
        might not be equal.)"""
        return self.__targetLongLat
    @property
    def sources(self): # type: () -> Sequence[Source]
        """The non-empty :py:class:`Sequence` of source(s) (essentially weather
        stations) that were used to generate the degree days used for the
        regressions in this response. If this response does not actually contain
        any regressions, this will return the source(s) that *would* have been
        used if they had had enough data to run regressions against the
        :py:class:`InputData` provided in the request.

        At the time of writing there will only be one source for any given
        response (so ``sources[0]``) is the way to get it)... But at some point
        we might start combining data from multiple sources to satisfy requests
        for data from :py:class:`GeographicLocation
        <degreedays.api.data.GeographicLocation>` types. If we do add this
        feature, it will be optional, and disabled by default, so the behaviour
        of your system won't change unless you want it to."""
        return self.__sources
    def getRegressions(self): # type: () -> Sequence[Regression]
        """Returns a non-empty best-first ordered :py:class:`Sequence` of
        :py:class:`Regression` objects, or throws a :py:class:`SourceDataError
        <degreedays.api.data.SourceDataError>` if the API could not generate
        regressions because there was not enough good weather data for the
        :py:class:`Location <degreedays.api.data.Location>` specified in your
        :py:class:`RegressionRequest`.

        :raises SourceDataError: if the API could not generate any regressions
            because there wasn't enough good weather data available for the
            :py:class:`Location <degreedays.api.data.Location>` specified in
            your :py:class:`RegressionRequest`."""
        if isinstance(self.__regressionsResult, degreedays.api.Failure):
            raise SourceDataError(self.__regressionsResult)
        return self.__regressionsResult
    def __str__(self):
        s = degreedays.api.data._getLocationResponseStringStart(self)
        s.append(', ')
        if isinstance(self.__regressionsResult, degreedays.api.Failure):
            s.append(str(self.__regressionsResult))
        else:
            count = len(self.__regressionsResult)
            if count > 1:
                s.append('%d regressions starting with ' % count)
            else:
                s.append('1 regression ')
            s.append(str(self.__regressionsResult[0]))
        s.append(')')
        return ''.join(s)
    def __repr__(self):
        return ("RegressionResponse(%r, '%s', %r, %r, %r)" %
            (self.__metadata, self.__stationId, self.__targetLongLat,
                self.__sources, self.__regressionsResult))


class RegressionApi(object):
    """Provides easy, type-safe access to the API's data-related operations.

    **To get a** ``RegressionApi`` **object and use it**, create a
    :py:class:`degreedays.api.DegreeDaysApi` object, get the ``RegressionApi``
    object from that, then call the method you want.

    **Example code for running regressions:**

    Please see the Python code samples in the `regression API docs on our
    website <https://www.degreedays.net/api/regression>`__."""
    def __init__(self, requestProcessor):
        self.__requestProcessor = requestProcessor
    def __checkAndGet(self, request, expectedResponseType):
        # type: (degreedays.api.Request, type[_RES]) -> _RES
        response = self.__requestProcessor.process(request)
        if isinstance(response, expectedResponseType):
            return response
        elif isinstance(response, degreedays.api.FailureResponse):
            code = response.failure.code
            if code.startswith('Location'):
                raise degreedays.api.data.LocationError(response)
            # for general exceptions
            raise degreedays.api.RequestFailureError._create(response)
        else:
            raise ValueError('For a request of type %r, the RequestProcessor '
                'should return a response of type %r or a FailureResponse, not '
                '%r' % (type(request), expectedResponseType, type(response)))
    def runRegressions(self, regressionRequest):
        # type: (RegressionRequest) -> RegressionResponse
        """Sends your :py:class:`RegressionRequest` to the API servers so it can
        run regressions against your :py:class:`InputData` and return a
        :py:class:`RegressionResponse` containing the regressions that were
        statistically best and/or any that you specifically requested.

        :param RegressionRequest regressionRequest: specifying the
            :py:class:`InputData` (energy data) you want regressions to be run
            against, the :py:class:`Location <degreedays.api.data.Location>` for
            which degree days should be generated to use in those regressions,
            and the :py:class:`RegressionTestPlan` defining what regressions the
            API should test and potentially return.
        :return: :py:class:`RegressionResponse` containing the regressions that
            the API found to give the best statistical fit with your
            :py:class:`InputData`.
        :raises LocationError: if the request fails because of problems relating
            to the specified :py:class:`Location
            <degreedays.api.data.Location>`.
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
        :raises TypeError: if `regressionRequest` is not a
            :py:class:`RegressionRequest` object.

        The API's processing will typically require it to generate degree days
        to match the :py:class:`InputData` you provide in your request, so it
        can use those degree days in the regressions it tests. To do this it
        will use the :py:class:`Location <degreedays.api.data.Location>`
        specified in your request.

        If you specify a :py:class:`StationIdLocation
        <degreedays.api.data.impl.StationIdLocation>` (created via
        :py:meth:`Location.stationId <degreedays.api.data.Location.stationId>`),
        then the API will use data from that station. But, if you specify a
        :py:class:`GeographicLocation <degreedays.api.data.GeographicLocation>`,
        the API will choose which station(s) to use automatically. The choice
        will depend on the dates of your :py:class:`InputData` as well as the
        location you specify. Some stations have more data than others, and the
        quality of a station's data can vary over time. The API will choose the
        station(s) that can best match the data you provide in your request.

        If you specify an inactive weather station (see
        :py:attr:`LocationError.isDueToLocationNotSupported
        <degreedays.api.data.LocationError.isDueToLocationNotSupported>` for
        more on these), or a :py:class:`GeographicLocation
        <degreedays.api.data.GeographicLocation>` for which no active station
        can be found with enough data to run regressions against your
        :py:class:`InputData`, you will get a :py:class:`LocationError
        <degreedays.api.data.LocationError>` instead of a
        :py:class:`RegressionResponse`.

        **Regressions not covering all of your input data:**

        If the location you specify in your request does not have sufficient
        weather data for the API to run regressions against your full input
        data, it may still be able to run regressions against part of it. You
        can check the :py:attr:`Regression.sampleSpan` and the
        :py:attr:`Regression.sampleSize` of any :py:class:`Regression` in the
        response (comparing with :py:attr:`InputData.fullRange` and the ``len``
        of :py:attr:`InputData.periods`) to see if this has happened.

        It is unlikely to happen unless you are trying to run regressions
        against very old energy data, or very recent energy data e.g. that
        includes a day that finished in the last hour or two. If you want to be
        sure to prevent it from happening, you could make a
        :py:class:`LocationInfoRequest
        <degreedays.api.data.LocationInfoRequest>` first, specifying data with a
        :py:class:`DayRangePeriod <degreedays.api.data.impl.DayRangePeriod>`
        that matches your :py:class:`InputData` and with a
        `minimumDayRangeOrNone` that specifies that same
        :py:class:`degreedays.time.DayRange`.  If you get a successful response
        back you will have a weather station ID that you know you can use in
        your regression request. But you will have used only 1 request unit to
        find that out (versus however many it might take to run a load of
        regressions that might only cover part of your data).

        More info and code samples
        --------------------------
        Please see the `regression API docs on our website
        <https://www.degreedays.net/api/regression>`__ for more information and
        Python code samples showing how to run regressions through the API."""
        RegressionRequest._check(regressionRequest)
        return self.__checkAndGet(regressionRequest, RegressionResponse)
