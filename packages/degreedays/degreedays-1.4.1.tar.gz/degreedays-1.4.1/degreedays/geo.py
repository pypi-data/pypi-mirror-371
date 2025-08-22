"""
Classes for handling geographic information like longitude/latitude positions
and distances.
"""

from degreedays._private import _Immutable, XmlElement
import degreedays._private as private
try:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        import sys
        if sys.version_info >= (3, 9):
            from collections.abc import Iterator
        else:
            from typing import Iterator
except ImportError:
    pass

__all__ = ['LongLat', 'DistanceUnit', 'Distance']

# Allows for slight rounding errors on calculated longitude and latitude values.
_MARGIN = 0.001
class LongLat(_Immutable):
    """Defines a geographic position in terms of its longitude and latitude
    coordinates (take care not to mix these up in the constructor).
    
    :param float longitude: a number between -180 and 180 (both inclusive)
        representing the West/East coordinate. A zero longitude value represents
        a line passing to the rear of the Royal Observatory, Greenwich (near
        London in the UK). Negative values are to the West of that line (e.g.
        locations in the US all have negative longitude values), and positive
        values are to the East of that line.
        
    :param float latitude: a number between -90 and 90 (both inclusive) representing
        the South/North coordinate. -90 represents the South Pole, 90 represents
        the North Pole, and 0 represents the equator.
        
    :raises TypeError: if either the longitude or latitude is not a numeric
        type.
        
    :raises ValueError: if either the longitude or latitude is `NaN` or outside
        of its allowed range."""
    __slots__ = ('__longitude', '__latitude')
    def __fail(self, longitude, latitude): # type: (float, float) -> None
        raise ValueError("Problem longitude (%r) or latitude (%r)." %
                         (longitude, latitude))
    def __init__(self, longitude, latitude): # type: (float, float) -> None
        longitude = private.checkNumeric(longitude, 'longitude')
        latitude = private.checkNumeric(latitude, 'latitude')
        if longitude > 180.0:
            if longitude > 180.0 + _MARGIN:
                self.__fail(longitude, latitude)
            longitude = 180.0
        elif longitude < -180.0:
            if longitude < -180.0 - _MARGIN:
                self.__fail(longitude, latitude)
        if latitude > 90.0:
            if latitude > 90.0 + _MARGIN:
                self.__fail(longitude, latitude)
            latitude = 90.0
        elif latitude < -90.0:
            if latitude < -90.0 - _MARGIN:
                self.__fail(longitude, latitude)
            latitude = -90.0
        self.__longitude = longitude
        self.__latitude = latitude
    def _equalityFields(self):
        return (self.__longitude, self.__latitude)
    @property
    def longitude(self): # type: () -> float
        """The longitude of this :py:class:`LongLat` object: a number between
        -180 and 180 (both inclusive) representing the West/East coordinate,
        zeroed on a line passing to the rear of the Royal Observatory, Greenwich
        (near London in the UK). Negative values are to the West of that line
        (e.g. locations in the US all have negative longitude values); positive
        values are to the East of that line."""
        return self.__longitude
    @property
    def latitude(self): # type: () -> float
        """The latitude of this :py:class:`LongLat` object: a number between -90
        and 90 (both inclusive) representing the South/North coordinate. -90
        represents the South Pole, 90 represents the North Pole, and 0
        represents the equator."""
        return self.__latitude
    def __repr__(self):
        return 'LongLat(%f, %f)' % (self.__longitude, self.__latitude)
    def _toXml(self):
        # Will str localize it?  Hard to find in docs, but I tested it with
        # Windows set to a french locale and it didn't, which is good.
        return (XmlElement("LongLat")
                .addAttribute("longitude", str(self.__longitude))
                .addAttribute("latitude", str(self.__latitude)))
    @staticmethod
    def _check(param, paramName='longLat'):
        # type: (LongLat, str) -> LongLat
        if type(param) is not LongLat:
            raise TypeError(private.wrongTypeString(param, paramName, LongLat,
                'LongLat(-74.0064, 40.7142)'))
        return param

# See TemperatureUnit for an explanation of this pattern
class _DistanceUnitMetaclass(type):
    _SYMBOLS = ('m', 'km', 'ft', 'mi')
    def __iter__(self): # type: () -> Iterator[DistanceUnit]
        for symbol in _DistanceUnitMetaclass._SYMBOLS:
            yield DistanceUnit._get(symbol)
    #EnumCopyStart(DistanceUnit)
    @property
    def METRES(cls): # type: () -> DistanceUnit
        """For the SI base unit of length, the metre (m).

        Access via: ``DistanceUnit.METRES``"""
        return DistanceUnit._get('m')
    @property
    def KILOMETRES(cls): # type: () -> DistanceUnit
        """For the metric unit the kilometre (km); 1 kilometre = 1000 metres.

        Access via: ``DistanceUnit.KILOMETRES``"""
        return DistanceUnit._get('km')
    @property
    def FEET(cls): # type: () -> DistanceUnit
        """For the imperial unit the foot (ft).

        Access via: ``DistanceUnit.FEET``"""
        return DistanceUnit._get('ft')
    @property
    def MILES(cls): # type: () -> DistanceUnit
        """For the imperial unit the mile (mi); 1 mile = 5280 feet.

        Access via: ``DistanceUnit.MILES``"""
        return DistanceUnit._get('mi')
    #EnumCopyEnd
_DistanceUnitSuper = _DistanceUnitMetaclass('_DistanceUnitSuper', (_Immutable,),
    {'__slots__': ()})
_FEET_IN_METRE = 3.28083989501
class DistanceUnit(_DistanceUnitSuper):
    """Defines the units of distance measurement with constants to represent
    metres, kilometres, feet, and miles."""
    __slots__ = ('__symbol', '__singularName', '__pluralName', '__isMetric',
        '__noOfBase', '__pluralNameUpper')
    __map = {} # type: dict[str, DistanceUnit]
    #EnumPaste(DistanceUnit)
    def __new__(cls) :
        """:meta private:"""
        raise TypeError('This is not built for direct instantiation.  Please '
            'use DistanceUnit.METRES, DistanceUnit.KILOMETRES, '
            'DistanceUnit.FEET, or DistanceUnit.MILES.')
    def __initImpl(self, symbol, singularName, pluralName, isMetric, noOfBase):
        # type: (str, str, str, bool, int) -> None
        self.__symbol = symbol
        self.__singularName = singularName
        self.__pluralName = pluralName
        self.__isMetric = isMetric
        # Store it as a float so as to force floating-point division in python 2.
        # Otherwise it will do integer division when converting and e.g. 5800 m
        # will come out as 5 km.
        self.__noOfBase = float(noOfBase)
        self.__pluralNameUpper = pluralName.upper()
    @classmethod
    def _create(cls, symbol): # type: (str) -> DistanceUnit
        newItem = super(DistanceUnit, cls).__new__(cls)
        if symbol == 'm':
            newItem.__initImpl('m', 'metre', 'metres', True, 1)
        elif symbol == 'km':
            newItem.__initImpl('km', 'kilometre', 'kilometres', True, 1000)
        elif symbol == 'ft':
            newItem.__initImpl('ft', 'foot', 'feet', False, 1)
        elif symbol == 'mi':
            newItem.__initImpl('mi', 'mile', 'miles', False, 5280)
        else:
            raise ValueError
        cls.__map[newItem.__symbol] = newItem
        return newItem
    @classmethod
    def _get(cls, symbol): # type: (str) -> DistanceUnit
        return cls.__map[symbol]
    def __getattr__(self, name): # type: (str) -> str
        return getattr(_DistanceUnitMetaclass, name)
    def _equalityFields(self): # type: () -> object
        return self.__symbol
    def __convertValueToSameSchemeUnit(self, value, sameSchemeUnit):
        # type: (float, DistanceUnit) -> float
        if self == sameSchemeUnit:
            return value
        elif sameSchemeUnit.__noOfBase == 1:
            return value * self.__noOfBase
        elif self.__noOfBase == 1:
            return value / sameSchemeUnit.__noOfBase
        else:
            raise ValueError('This should not happen with the range of units '
                'we have')
    def _convertValue(self, value, newUnit):
        # type: (float, DistanceUnit) -> float
        if self.__isMetric == newUnit.__isMetric:
            return self.__convertValueToSameSchemeUnit(value, newUnit)
        elif self.__isMetric:
            inMetres = self.__convertValueToSameSchemeUnit(
                value, DistanceUnit._get('m'))
            inFeet = inMetres * _FEET_IN_METRE
            return DistanceUnit._get('ft').__convertValueToSameSchemeUnit(
                inFeet, newUnit)
        else:
            inFeet = self.__convertValueToSameSchemeUnit(
                value, DistanceUnit._get('ft'))
            inMetres = inFeet / _FEET_IN_METRE
            return DistanceUnit._get('m').__convertValueToSameSchemeUnit(
                inMetres, newUnit)
    def __str__(self):
        return self.__pluralName
    def __repr__(self):
        return 'DistanceUnit.' + self.__pluralNameUpper
    @property # as property to make it immutable (or as much as is possible)
    def _symbol(self): # type: () -> str
        return self.__symbol
    @staticmethod
    def _check(param, paramName='distanceUnit'):
        # type: (DistanceUnit, str) -> DistanceUnit
        if type(param) is not DistanceUnit:
            raise TypeError(private.wrongTypeString(param, paramName,
                DistanceUnit, 'DistanceUnit.METRES, DistanceUnit.KILOMETRES, '
                'DistanceUnit.FEET, DistanceUnit.MILES'))
        return param
for _symbol in DistanceUnit._SYMBOLS:
    DistanceUnit._create(_symbol)

class Distance(_Immutable):
    """Defines a distance in terms of its numeric value and its unit of
    measurement (e.g. 20 miles).
    
    **To create a** :py:class:`Distance` **object**, it's usually easiest to use
    the class methods: :py:meth:`metres`, :py:meth:`kilometres`,
    :py:meth:`feet`, and :py:meth:`miles`. For example:
    
    ``twentyMiles = Distance.miles(20)``
    
    It's easy to convert between units:
    
    ``twentyMilesInMetres = twentyMiles.inMetres()``"""
    __slots__ = ('__value', '__unit')
    def __init__(self, value, unit): # type: (float, DistanceUnit) -> None
        self.__value = private.checkNumeric(value, 'value')
        self.__unit = DistanceUnit._check(unit, 'unit')
    def _equalityFields(self):
        return (self.__value, self.__unit)
    @property
    def value(self):
        """The numeric value of this :py:class:`Distance` object."""
        return self.__value
    @property
    def unit(self):
        """The :py:class:`DistanceUnit` of this :py:class:`Distance` object."""
        return self.__unit
    @staticmethod
    def metres(value): # type: (float) -> Distance
        """Returns a :py:class:`Distance` object with the specified `value` and
        :py:const:`DistanceUnit.METRES` as the unit of measurement.
        
        :param int|float value: the number of metres that the returned
            :py:class:`Distance` should represent.
        
        :raises TypeError: if `value` is not a numeric type.
        
        :raises ValueError: if `value` is `NaN` or infinite."""
        return Distance(value, DistanceUnit.METRES)
    @staticmethod
    def kilometres(value): # type: (float) -> Distance
        """Returns a :py:class:`Distance` object with the specified `value` and
        :py:const:`DistanceUnit.KILOMETRES` as the unit of measurement.
        
        :param int|float value: the number of kilometres that the returned
            :py:class:`Distance` should represent.
        
        :raises TypeError: if `value` is not a numeric type.
        
        :raises ValueError: if `value` is `NaN` or infinite."""
        return Distance(value, DistanceUnit.KILOMETRES)
    @staticmethod
    def feet(value): # type: (float) -> Distance
        """Returns a :py:class:`Distance` object with the specified `value` and
        :py:const:`DistanceUnit.FEET` as the unit of measurement.
        
        :param int|float value: the number of feet that the returned
            :py:class:`Distance` should represent.
        
        :raises TypeError: if `value` is not a numeric type.
        
        :raises ValueError: if `value` is `NaN` or infinite."""
        return Distance(value, DistanceUnit.FEET)
    @staticmethod
    def miles(value): # type: (float) -> Distance
        """Returns a :py:class:`Distance` object with the specified `value` and
        :py:const:`DistanceUnit.MILES` as the unit of measurement.
        
        :param int|float value: the number of miles that the returned
            :py:class:`Distance` should represent.
        
        :raises TypeError: if `value` is not a numeric type.
        
        :raises ValueError: if `value` is `NaN` or infinite."""
        return Distance(value, DistanceUnit.MILES)
    def __toUnit(self, newUnit): # type: (DistanceUnit) -> Distance
        if newUnit == self.__unit:
            return self
        return Distance(self.__unit._convertValue(self.__value, newUnit),
            newUnit)
    def inMetres(self): # type: () -> Distance
        """Returns a :py:class:`Distance` object that represents this
        :py:class:`Distance` converted into metres."""
        return self.__toUnit(DistanceUnit.METRES)
    def inKilometres(self): # type: () -> Distance
        """Returns a :py:class:`Distance` object that represents this
        :py:class:`Distance` converted into kilometres."""
        return self.__toUnit(DistanceUnit.KILOMETRES)
    def inFeet(self): # type: () -> Distance
        """Returns a :py:class:`Distance` object that represents this
        :py:class:`Distance` converted into feet."""
        return self.__toUnit(DistanceUnit.FEET)
    def inMiles(self): # type: () -> Distance
        """Returns a :py:class:`Distance` object that represents this
        :py:class:`Distance` converted into miles."""
        return self.__toUnit(DistanceUnit.MILES)
    # "in" is a reserved word so we can't use that.  PEP8 recommends to add a
    # trailing underscore and this seems to be a kind of convention in Python.
    def in_(self, unit): # type: (DistanceUnit) -> Distance
        """Returns a :py:class:`Distance` object that represents this
        :py:class:`Distance` converted into the specified unit of measurement.
        
        For example, ``Distance.metres(1000).in_(DistanceUnit.KILOMETRES)`` will
        return a :py:class:`Distance` that is equal to
        ``Distance.kilometres(1)``.
        
        :param DistanceUnit unit: the unit of measurement that the returned
            :py:class:`Distance` should have.
        
        :raises TypeError: if `unit` is not a :py:class:`DistanceUnit`."""
        return self.__toUnit(unit)
    def __str__(self):
        return '%g %s' % (self.__value, self.__unit._symbol)
    def __repr__(self):
        return 'Distance.%s(%g)' % (self.__unit, self.__value)
    @staticmethod
    def _check(param, paramName='distance'):
        # type: (Distance, str) -> Distance
        if type(param) is not Distance:
            raise TypeError(private.wrongTypeString(param, paramName, Distance,
                'Distance.metres(20)'))
        return param
