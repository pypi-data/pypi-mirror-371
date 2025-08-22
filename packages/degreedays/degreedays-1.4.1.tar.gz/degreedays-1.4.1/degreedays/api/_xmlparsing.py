
# Disable most type checking in this module.  There's no need for it in this
# private module.
# pyright: reportUnknownParameterType=false
# pyright: reportMissingParameterType=false
# pyright: reportIncompatibleMethodOverride=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportOptionalMemberAccess=false
# pyright: reportArgumentType=false
# pyright: reportAttributeAccessIssue=false

import datetime
from xml.sax import ContentHandler, parse
from degreedays.api import RateLimit, ResponseMetadata, Failure, FailureResponse
from degreedays.api.data import Station, Source, DatedDataValue, DatedDataSet, \
    DataValue, AverageDataSet, TimeSeriesDataValue, TimeSeriesDataSet, \
    DataSets, LocationDataResponse, LocationInfoResponse, TemperatureUnit, \
    Temperature
from degreedays.api.regression import RegressionTag, \
    BaseloadRegressionComponent, ExtraRegressionComponent, \
    DegreeDaysRegressionComponent, RegressionComponents, Regression, \
    RegressionResponse
from degreedays.geo import LongLat, Distance
from degreedays.time import DayRange, _createTimeZone
import degreedays._private as private

# Don't actually use this - just take a function.
class CollectionCallback(object):
    def collectionEnded(self, collected):
        pass

class DelegateLifetime(object):
    def onStart(self, name, attributes):
        pass
    def isEnd(self, name):
        pass

class SimpleDelegateLifetime(DelegateLifetime):
    def __init__(self, name):
        self.__name = name
        self.__count = 1
    def isEnd(self, name):
        if self.__name == name:
            self.__count -= 1
            if self.__count == 0:
                return True
        return False
    def onStart(self, name, attributes):
        if self.__name == name:
            self.__count += 1

class CharacterCollectionStrategy(object):
    # Return none if it doesn't want the characters for this name
    def getCollectionCallbackOrNone(self, name, attributes):
        pass

class FixedCharacterCollectionStrategy(CharacterCollectionStrategy):
    def __init__(self, nameSet):
        self.__nameSet = nameSet
        self.__nameToCollectedStringMap = {}
    def getCollectionCallbackOrNone(self, name, attributes):
        if name in self.__nameSet:
            def callback(collected):
                self.__nameToCollectedStringMap[name] = collected
            return callback
        else:
            return None
    def getCollectedOrNone(self, name):
        return self.__nameToCollectedStringMap.get(name)


class SimpleSaxHandler(ContentHandler):
    def __init__(self):
        ContentHandler.__init__(self)
        self.__delegateHandlingEndedCallback = None
        self.__parent = None
        self.__childDelegates = []
        self.__childDelegateLifetimes = []
        self.__currentDelegate = None
        self.__currentDelegateLifetime = None
        self.__characterCollectionStrategy = None
        # Following are non None if characters are being collected.  Then back
        # to None when we're done.
        self.__collectionCallbackOrNone = None
        self.__characterCollector = None

    def withDelegateHandlingEndedCallback(self, callback):
        self.__delegateHandlingEndedCallback = callback
        return self

    def setCharacterCollectionStrategy(self, strategy):
        self.__characterCollectionStrategy = strategy
        return strategy

    def __getRootAncestor(self):
        testHandler = self
        while testHandler.__parent is not None:
            testHandler = testHandler.__parent
        return testHandler

    def startElement(self, name, attrs):
        if self.__currentDelegate is not None:
            self.__currentDelegateLifetime.onStart(name, attrs)
            self.__currentDelegate.startElement(name, attrs)
        else:
            if self.__characterCollectionStrategy is not None:
                callbackOrNone = self.__characterCollectionStrategy \
                    .getCollectionCallbackOrNone(name, attrs)
                if callbackOrNone is not None:
                    self.collectCharacters(callbackOrNone)
            self.startElementImpl(name, attrs)

    def startElementImpl(self, name, attributes):
        pass

    def endElement(self, name):
        isDelegated = False
        if self.__currentDelegate is not None:
            if self.__currentDelegateLifetime.isEnd(name):
                self.__currentDelegate.delegateHandlingEnded()
                noParents = len(self.__childDelegates)
                if noParents > 0:
                    self.__currentDelegate = self.__childDelegates.pop()
                    self.__currentDelegateLifetime = \
                        self.__childDelegateLifetimes.pop()
                else:
                    self.__currentDelegate = None
                    self.__currentDelegateLifetime = None
            else:
                self.__currentDelegate.endElement(name)
                isDelegated = True
        if not isDelegated:
            if self.__collectionCallbackOrNone is not None:
                collected = ''.join(self.__characterCollector)
                self.__collectionCallbackOrNone(collected)
                # reset now to save memory.
                self.__characterCollector = None
                # Set to null so we know not to collect more.
                self.__collectionCallbackOrNone = None
            self.endElementImpl(name)

    def endElementImpl(self, name):
        pass

    def addDelegate(self, delegate, lifetimeOrNameForEnd):
        delegate.__parent = self
        root = self.__getRootAncestor()
        if not isinstance(lifetimeOrNameForEnd, DelegateLifetime):
            lifetimeOrNameForEnd = \
                SimpleDelegateLifetime(lifetimeOrNameForEnd)
        root.__addDelegateImpl(delegate, lifetimeOrNameForEnd)

    def __addDelegateImpl(self, delegate, lifetime):
        if self.__currentDelegate is not None:
            self.__childDelegates.append(self.__currentDelegate)
            self.__childDelegateLifetimes.append(self.__currentDelegateLifetime)
        self.__currentDelegate = delegate
        self.__currentDelegateLifetime = lifetime

    # Subclasses can override this if they want to be told when they are no
    # longer the delegate handler.  Override this to get the completed stuff
    # out of a delegate when it's done.
    def delegateHandlingEnded(self):
        if self.__delegateHandlingEndedCallback is not None:
            self.__delegateHandlingEndedCallback(self)

    # To be called by a subclass in {@link #startElementImpl}.  Probably
    # unnecessary to call this if using a {@link CharacterCollectionStrategy}.
    def collectCharacters(self, collectionCallback):
        self.__characterCollector = [] # type: list[str]
        self.__collectionCallbackOrNone = collectionCallback

    def characters(self, content):
        if self.__currentDelegate is not None:
            self.__currentDelegate.characters(content)
        elif self.__collectionCallbackOrNone is not None:
            self.__characterCollector.append(content)

REQUEST_UNITS_AVAILABLE = 'RequestUnitsAvailable'
MINUTES_TO_RESET = 'MinutesToReset'
# set and frozenset were both introduced in Python 2.4.  So there's no reason
# to use set when frozenset is better here (as it's immutable).
RATE_LIMIT_NAMES = frozenset((REQUEST_UNITS_AVAILABLE, MINUTES_TO_RESET))

class SaxHandlerForRateLimit(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(RATE_LIMIT_NAMES))
    def getRateLimit(self):
        requestUnits = int(self.chars.getCollectedOrNone(
            REQUEST_UNITS_AVAILABLE))
        minutesToReset = int(self.chars.getCollectedOrNone(
            MINUTES_TO_RESET))
        return RateLimit(requestUnits, minutesToReset)

class SaxHandlerForResponseMetadata(SimpleSaxHandler):
    def startElementImpl(self, name, attributes):
        if "RateLimit" == name:
            def callback(handler):
                self.rateLimit = handler.getRateLimit()
            self.addDelegate(SaxHandlerForRateLimit() \
                .withDelegateHandlingEndedCallback(callback), name)
    def getMetadata(self):
        return ResponseMetadata(self.rateLimit)

CODE = 'Code'
MESSAGE = 'Message'
FAILURE_NAMES = frozenset((CODE, MESSAGE))

class SaxHandlerForFailure(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(FAILURE_NAMES))
    def getFailure(self):
        return Failure(
            self.chars.getCollectedOrNone(CODE),
            self.chars.getCollectedOrNone(MESSAGE))

class SaxHandlerForFailureResponse(SaxHandlerForFailure):
    def getResponse(self, metadata):
        return FailureResponse(metadata, self.getFailure())

def parseLongLat(attributes):
    return LongLat(float(attributes.getValue('longitude')),
        float(attributes.getValue('latitude')))

def parseMetresDistance(distanceString):
    return Distance.metres(float(distanceString))

# Could put this in time module, but not sure we want to commit to keeping it.
def parseIsoDate(dateString):
    split = dateString.split('-', 2)
    return datetime.date(int(split[0]), int(split[1]), int(split[2]))

def parsePercentageEstimated(peString):
    return float(peString)

def parsePercentageEstimatedAttribute(attributes):
    if 'pe' in attributes:
        return float(attributes.getValue('pe'))
    else:
        return 0.0

def parseDegreeDayValue(valueString):
    return float(valueString)

class SaxHandlerForTargetLocation(SimpleSaxHandler):
    def startElementImpl(self, name, attributes):
        if 'LongLat' == name:
            self.longLat = parseLongLat(attributes)

ID = 'Id'
ELEVATION_METRES = 'ElevationMetres'
DISPLAY_NAME = 'DisplayName'
STATION_NAMES = frozenset((ID, ELEVATION_METRES, DISPLAY_NAME))
class SaxHandlerForStation(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(STATION_NAMES))
    def startElementImpl(self, name, attributes):
        if 'LongLat' == name:
            self.longLat = parseLongLat(attributes)
    def getStation(self):
        return Station(
            self.chars.getCollectedOrNone(ID),
            self.longLat,
            parseMetresDistance(
                self.chars.getCollectedOrNone(ELEVATION_METRES)),
            self.chars.getCollectedOrNone(DISPLAY_NAME))

METRES_FROM_TARGET = 'MetresFromTarget'
SOURCE_NAMES = frozenset((METRES_FROM_TARGET,))
class SaxHandlerForSource(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(SOURCE_NAMES))
    def startElementImpl(self, name, attributes):
        if 'Station' == name:
            def callback(handler):
                self.station = handler.getStation()
            self.addDelegate(SaxHandlerForStation() \
                .withDelegateHandlingEndedCallback(callback), name)
    def getSource(self):
        return Source(self.station, parseMetresDistance(
            self.chars.getCollectedOrNone(METRES_FROM_TARGET)))

class SaxHandlerForSources(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.sources = []
    def startElementImpl(self, name, attributes):
        if 'Source' == name:
            def callback(handler):
                self.sources.append(handler.getSource())
            self.addDelegate(SaxHandlerForSource() \
                .withDelegateHandlingEndedCallback(callback), name)

STATION_ID = "StationId"
LOCATION_RESPONSE_HEAD_NAMES = frozenset((STATION_ID,))
class SaxHandlerForLocationResponseHead(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(LOCATION_RESPONSE_HEAD_NAMES))
        self.targetLongLat = None
        self.sources = None
    def startElementImpl(self, name, attributes):
        if 'TargetLocation' == name:
            def callback(handler):
                self.targetLongLat = handler.longLat
            self.addDelegate(SaxHandlerForTargetLocation() \
                .withDelegateHandlingEndedCallback(callback), name)
        elif 'Sources' == name:
            def callback(handler):
                self.sources = handler.sources
            self.addDelegate(SaxHandlerForSources() \
                .withDelegateHandlingEndedCallback(callback), name)
    def fillDict(self, d):
        d['stationId'] = self.chars.getCollectedOrNone(STATION_ID)
        d['targetLongLat'] = self.targetLongLat
        d['sources'] = self.sources

PERCENTAGE_ESTIMATED = 'PercentageEstimated'
DATED_DATA_SET_HEAD_NAMES = frozenset((PERCENTAGE_ESTIMATED,))

class SaxHandlerForDatedDataSetHead(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(DATED_DATA_SET_HEAD_NAMES))
    def fillDict(self, d):
        d['percentageEstimated'] = parsePercentageEstimated(
            self.chars.getCollectedOrNone(PERCENTAGE_ESTIMATED))

class SaxHandlerForDatedDataSetValues(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.setCharacterCollectionStrategy(self)
        self.datedDataValues = []
    def getCollectionCallbackOrNone(self, name, attributes):
        if name != 'V':
            return None
        firstDay = parseIsoDate(attributes.getValue('d'))
        if 'ld' in attributes:
            lastDay = parseIsoDate(attributes.getValue('ld'))
            self.dayRange = DayRange(firstDay, lastDay)
        else:
            self.dayRange = DayRange.singleDay(firstDay)
        self.percentageEstimated = parsePercentageEstimatedAttribute(attributes)
        return self.collectionEnded
    def collectionEnded(self, collected):
        value = parseDegreeDayValue(collected)
        datedDataValue = DatedDataValue(
            value, self.percentageEstimated, self.dayRange)
        self.datedDataValues.append(datedDataValue)

class SaxHandlerForDatedDataSet(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.params = {}
    def startElementImpl(self, name, attributes):
        if 'Head' == name:
            def callback(handler):
                handler.fillDict(self.params)
            self.addDelegate(SaxHandlerForDatedDataSetHead() \
                .withDelegateHandlingEndedCallback(callback), name)
        elif 'Values' == name:
            def callback(handler):
                self.params['values'] = handler.datedDataValues
            self.addDelegate(SaxHandlerForDatedDataSetValues() \
                .withDelegateHandlingEndedCallback(callback), name)
    def getResult(self):
        return DatedDataSet(**self.params)

FIRST_YEAR = 'FirstYear'
LAST_YEAR = 'LastYear'
AVERAGE_DATA_SET_HEAD_NAMES = frozenset((FIRST_YEAR, LAST_YEAR))
class SaxHandlerForAverageDataSetHead(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(AVERAGE_DATA_SET_HEAD_NAMES))
    def fillDict(self, d):
        d['firstYear'] = int(self.chars.getCollectedOrNone(FIRST_YEAR))
        d['lastYear'] = int(self.chars.getCollectedOrNone(LAST_YEAR))

class SaxHandlerForAverageDataSetMonthlyValues(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.setCharacterCollectionStrategy(self)
        self.monthlyAverages = []
    def getCollectionCallbackOrNone(self, name, attributes):
        if name != 'M':
            return None
        self.percentageEstimated = parsePercentageEstimatedAttribute(attributes)
        return self.collectionEnded
    def collectionEnded(self, collected):
        value = parseDegreeDayValue(collected)
        dataValue = DataValue(value, self.percentageEstimated)
        self.monthlyAverages.append(dataValue)

class SaxHandlerForAverageDataSetValues(SimpleSaxHandler):
    def startElementImpl(self, name, attributes):
        if 'Monthly' == name:
            def callback(handler):
                self.monthlyAverages = handler.monthlyAverages
            self.addDelegate(SaxHandlerForAverageDataSetMonthlyValues() \
                .withDelegateHandlingEndedCallback(callback), name)
        elif 'Annual' == name:
            percentageEstimated = parsePercentageEstimatedAttribute(attributes)
            def collectionEnded(collected):
                value = parseDegreeDayValue(collected)
                self.annualAverage = DataValue(value, percentageEstimated)
            self.collectCharacters(collectionEnded)

class SaxHandlerForAverageDataSet(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.params = {}
    def startElementImpl(self, name, attributes):
        if 'Head' == name:
            def callback(handler):
                handler.fillDict(self.params)
            self.addDelegate(SaxHandlerForAverageDataSetHead() \
                .withDelegateHandlingEndedCallback(callback), name)
        elif 'Values' == name:
            def callback(handler):
                self.params['annualAverage'] = handler.annualAverage
                self.params['monthlyAverages'] = handler.monthlyAverages
            self.addDelegate(SaxHandlerForAverageDataSetValues() \
                .withDelegateHandlingEndedCallback(callback), name)
    def getResult(self):
        return AverageDataSet(**self.params)

class SaxHandlerForTimeSeriesDataSetValues(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.setCharacterCollectionStrategy(self)
        self.timeSeriesDataValues = []
        self.__dateTimeParser = private.IsoDateTimeParser(_createTimeZone)
    def getCollectionCallbackOrNone(self, name, attributes):
        if name != 'V':
            return None
        self.datetime = self.__dateTimeParser.parse(attributes.getValue('dt'))
        self.percentageEstimated = parsePercentageEstimatedAttribute(attributes)
        return self.collectionEnded
    def collectionEnded(self, collected):
        value = float(collected)
        timeSeriesDataValue = TimeSeriesDataValue(
            value, self.percentageEstimated, self.datetime)
        self.timeSeriesDataValues.append(timeSeriesDataValue)

class SaxHandlerForTimeSeriesDataSet(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.params = {}
    def startElementImpl(self, name, attributes):
        if 'Head' == name:
            def callback(handler):
                handler.fillDict(self.params)
            # We use the handler for DatedDataSet Head, cos it's exactly what
            # we want, even though its name is wrong.
            self.addDelegate(SaxHandlerForDatedDataSetHead() \
                .withDelegateHandlingEndedCallback(callback), name)
        elif 'Values' == name:
            def callback(handler):
                self.params['values'] = handler.timeSeriesDataValues
            self.addDelegate(SaxHandlerForTimeSeriesDataSetValues() \
                .withDelegateHandlingEndedCallback(callback), name)
    def getResult(self):
        return TimeSeriesDataSet(**self.params)

class SaxHandlerForDataSetFailure(SaxHandlerForFailure):
    def getResult(self):
        return self.getFailure()

class SaxHandlerForDataSets(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.resultsMap = {}
    def __addHandler(self, name, attributes, newHandler):
        def callback(handler):
            self.resultsMap[attributes.getValue('key')] = handler.getResult()
        newHandler = newHandler.withDelegateHandlingEndedCallback(callback)
        self.addDelegate(newHandler, name)
    def startElementImpl(self, name, attributes):
        if 'DatedDataSet' == name:
            self.__addHandler(name, attributes, SaxHandlerForDatedDataSet())
        elif 'AverageDataSet' == name:
            self.__addHandler(name, attributes, SaxHandlerForAverageDataSet())
        elif 'TimeSeriesDataSet' == name:
            self.__addHandler(name, attributes, SaxHandlerForTimeSeriesDataSet())
        elif 'Failure' == name:
            self.__addHandler(name, attributes, SaxHandlerForDataSetFailure())
    def getDataSets(self, dataSpecsOrNone):
        return DataSets(dataSpecsOrNone, self.resultsMap)

TAGS_DICT = {}
for tag in RegressionTag:
    TAGS_DICT[str(tag)] = tag
class SaxHandlerForRegressionTags(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.tags = []
        self.setCharacterCollectionStrategy(self)
    def collectionEnded(self, collected):
        tagOrNone = TAGS_DICT.get(collected)
        if tagOrNone is not None:
            self.tags.append(tagOrNone)
    def getCollectionCallbackOrNone(self, name, attributes):
        if name == 'Tag':
            return self.collectionEnded
        return None
    def getResult(self):
        return self.tags

class RegressionComponentType:
    BASELOAD = None
    HEATING_DEGREE_DAYS = None
    COOLING_DEGREE_DAYS = None
    EXTRA = None
    def __init__(self, name, cls):
        self.name = name
        self.infoName = name + 'Info'
        self.cls = cls
    def getResult(self, params):
        return self.cls(params)
RegressionComponentType.BASELOAD = RegressionComponentType(
    'Baseload', BaseloadRegressionComponent)
RegressionComponentType.HEATING_DEGREE_DAYS = RegressionComponentType(
    'HeatingDegreeDays', DegreeDaysRegressionComponent)
RegressionComponentType.COOLING_DEGREE_DAYS = RegressionComponentType(
    'CoolingDegreeDays', DegreeDaysRegressionComponent)
RegressionComponentType.EXTRA = RegressionComponentType(
    'Extra', ExtraRegressionComponent)

COEFFICIENT = 'Coefficient'
COEFFICIENT_STANDARD_ERROR = 'CoefficientStandardError'
COEFFICIENT_P_VALUE = 'CoefficientPValue'
REGRESSION_COMPONENT_NAMES = frozenset((COEFFICIENT, COEFFICIENT_STANDARD_ERROR,
    COEFFICIENT_P_VALUE))
class SaxHandlerForRegressionComponent(SimpleSaxHandler):
    def __init__(self, componentType, extraHandler):
        SimpleSaxHandler.__init__(self)
        self.componentType = componentType
        self.extraHandler = extraHandler
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(REGRESSION_COMPONENT_NAMES))
    def startElementImpl(self, name, attributes):
        if self.componentType.infoName == name:
            self.addDelegate(self.extraHandler, name)
    def getResult(self):
        d = {}
        d['coefficient'] = float(self.chars.getCollectedOrNone(COEFFICIENT))
        d['coefficientStandardError'] = float(
            self.chars.getCollectedOrNone(COEFFICIENT_STANDARD_ERROR))
        d['coefficientPValue'] = float(
            self.chars.getCollectedOrNone(COEFFICIENT_P_VALUE))
        self.extraHandler.fillDict(d)
        return self.componentType.cls(**d)

CELSIUS_BASE_TEMPERATURE = 'CelsiusBaseTemperature'
FAHRENHEIT_BASE_TEMPERATURE = 'FahrenheitBaseTemperature'
SAMPLE_DEGREE_DAYS_DATA_SET_KEY = 'SampleDegreeDaysDataSetKey'
SAMPLE_DEGREE_DAYS_TOTAL = 'SampleDegreeDaysTotal'
DEGREE_DAYS_REGRESSION_COMPONENT_NAMES = frozenset((CELSIUS_BASE_TEMPERATURE,
    FAHRENHEIT_BASE_TEMPERATURE, SAMPLE_DEGREE_DAYS_DATA_SET_KEY))
class SaxHandlerForDegreeDaysRegressionComponentExtra(SimpleSaxHandler):
    def __init__(self, dataSets):
        SimpleSaxHandler.__init__(self)
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(
                DEGREE_DAYS_REGRESSION_COMPONENT_NAMES))
        self.sampleDegreeDaysTotal = None
        self.dataSets = dataSets
    def startElementImpl(self, name, attributes):
        if SAMPLE_DEGREE_DAYS_TOTAL == name:
            pe = parsePercentageEstimatedAttribute(attributes)
            def collectionEnded(collected):
                value = parseDegreeDayValue(collected)
                self.sampleDegreeDaysTotal = DataValue(value, pe)
            self.collectCharacters(collectionEnded)
    def fillDict(self, d):
        baseStr = self.chars.getCollectedOrNone(CELSIUS_BASE_TEMPERATURE)
        if baseStr is not None:
            baseUnit = TemperatureUnit.CELSIUS
        else:
            baseStr = self.chars.getCollectedOrNone(FAHRENHEIT_BASE_TEMPERATURE)
            baseUnit = TemperatureUnit.FAHRENHEIT
        d['baseTemperature'] = Temperature(float(baseStr), baseUnit)
        dataSetKey = self.chars.getCollectedOrNone(
                SAMPLE_DEGREE_DAYS_DATA_SET_KEY)
        d['sampleDegreeDaysDataSet'] = self.dataSets[dataSetKey]
        d['sampleDegreeDaysTotal'] = self.sampleDegreeDaysTotal

MULTIPLY_BY_NUMBER_OF_DAYS = 'MultiplyByNumberOfDays'
MULTIPLY_BY_NUMBER_OF_DAYS_REGRESSION_COMPONENT_NAMES = frozenset((
    MULTIPLY_BY_NUMBER_OF_DAYS,))
class SaxHandlerForMultiplyByNumberOfDaysRegressionComponentExtra(
        SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(
                MULTIPLY_BY_NUMBER_OF_DAYS_REGRESSION_COMPONENT_NAMES))
    def parseMultiplyByNumberOfDays(self):
        value = self.chars.getCollectedOrNone(MULTIPLY_BY_NUMBER_OF_DAYS)
        if value == 'true':
            return True
        elif value == 'false':
            return False
        else:
            return None
    def fillDict(self, d):
        d['multiplyByNumberOfDays'] = self.parseMultiplyByNumberOfDays()

class SaxHandlerForRegressionComponents(SimpleSaxHandler):
    def __init__(self, dataSetsOrNone):
        SimpleSaxHandler.__init__(self)
        self.dataSetsOrNone = dataSetsOrNone
        self.params = {}
        self.params['extras'] = {}
    def startElementImpl(self, name, attributes):
        if 'Baseload' == name:
            def callback(handler):
                self.params['baseload'] = handler.getResult()
            handler = SaxHandlerForRegressionComponent(
                    RegressionComponentType.BASELOAD,
                    SaxHandlerForMultiplyByNumberOfDaysRegressionComponentExtra()) \
                .withDelegateHandlingEndedCallback(callback)
            self.addDelegate(handler, name)
        elif 'HeatingDegreeDays' == name:
            def callback(handler):
                self.params['heatingDegreeDaysOrNone'] = handler.getResult()
            handler = SaxHandlerForRegressionComponent(
                    RegressionComponentType.HEATING_DEGREE_DAYS,
                    SaxHandlerForDegreeDaysRegressionComponentExtra(
                        self.dataSetsOrNone)) \
                .withDelegateHandlingEndedCallback(callback)
            self.addDelegate(handler, name)
        elif 'CoolingDegreeDays' == name:
            def callback(handler):
                self.params['coolingDegreeDaysOrNone'] = handler.getResult()
            handler = SaxHandlerForRegressionComponent(
                    RegressionComponentType.COOLING_DEGREE_DAYS,
                    SaxHandlerForDegreeDaysRegressionComponentExtra(
                        self.dataSetsOrNone)) \
                .withDelegateHandlingEndedCallback(callback)
            self.addDelegate(handler, name)
        elif 'Extra' == name:
            key = attributes.getValue('key')
            def callback(handler):
                self.params['extras'][key] = handler.getResult()
            handler = SaxHandlerForRegressionComponent(
                    RegressionComponentType.EXTRA,
                    SaxHandlerForMultiplyByNumberOfDaysRegressionComponentExtra()) \
                .withDelegateHandlingEndedCallback(callback)
            self.addDelegate(handler, name)
    def getResult(self):
        return RegressionComponents(**self.params)

SAMPLE_SIZE = 'SampleSize'
SAMPLE_DAYS = 'SampleDays'
R_SQUARED = 'RSquared'
ADJUSTED_R_SQUARED = 'AdjustedRSquared'
CROSS_VALIDATED_R_SQUARED = 'CrossValidatedRSquared'
STANDARD_ERROR = 'StandardError'
CVRMSE = 'Cvrmse'
REGRESSION_NAMES = frozenset((SAMPLE_SIZE, SAMPLE_DAYS, R_SQUARED,
    ADJUSTED_R_SQUARED, CROSS_VALIDATED_R_SQUARED, STANDARD_ERROR, CVRMSE))
class SaxHandlerForRegression(SimpleSaxHandler):
    def __init__(self, dataSetsOrNone):
        SimpleSaxHandler.__init__(self)
        self.dataSetsOrNone = dataSetsOrNone
        self.chars = self.setCharacterCollectionStrategy(
            FixedCharacterCollectionStrategy(REGRESSION_NAMES))
        self.tags = None
        self.components = None
        self.sampleSpan = None
    def startElementImpl(self, name, attributes):
        if 'Tags' == name:
            def callback(handler):
                self.tags = handler.getResult()
            handler = SaxHandlerForRegressionTags() \
                .withDelegateHandlingEndedCallback(callback)
            self.addDelegate(handler, name)
        elif 'Components' == name:
            def callback(handler):
                self.components = handler.getResult()
            handler = SaxHandlerForRegressionComponents(self.dataSetsOrNone) \
                .withDelegateHandlingEndedCallback(callback)
            self.addDelegate(handler, name)
        elif 'SampleSpan' == name:
            self.sampleSpan = DayRange(
                parseIsoDate(attributes.getValue('first')),
                parseIsoDate(attributes.getValue('last')))
    def getResult(self):
        return Regression(self.tags,
            self.components,
            int(self.chars.getCollectedOrNone(SAMPLE_SIZE)),
            int(self.chars.getCollectedOrNone(SAMPLE_DAYS)),
            self.sampleSpan,
            float(self.chars.getCollectedOrNone(R_SQUARED)),
            float(self.chars.getCollectedOrNone(ADJUSTED_R_SQUARED)),
            float(self.chars.getCollectedOrNone(CROSS_VALIDATED_R_SQUARED)),
            float(self.chars.getCollectedOrNone(STANDARD_ERROR)),
            float(self.chars.getCollectedOrNone(CVRMSE)))

class SaxHandlerForRegressions(SimpleSaxHandler):
    def __init__(self, dataSetsOrNone):
        SimpleSaxHandler.__init__(self)
        self.regressions = []
        self.dataSetsOrNone = dataSetsOrNone
    def startElementImpl(self, name, attributes):
        if 'Regression' == name:
            def callback(handler):
                self.regressions.append(handler.getResult())
            handler = SaxHandlerForRegression(self.dataSetsOrNone) \
                .withDelegateHandlingEndedCallback(callback)
            self.addDelegate(handler, name)
    def getRegressions(self):
        return self.regressions

class SaxHandlerForLocationDataResponse(SimpleSaxHandler):
    def __init__(self, locationDataRequestOrNone):
        SimpleSaxHandler.__init__(self)
        if locationDataRequestOrNone is None:
            self.dataSpecsOrNone = None
        else:
            self.dataSpecsOrNone = locationDataRequestOrNone.dataSpecs
        self.params = {}
    def startElementImpl(self, name, attributes):
        if 'Head' == name:
            def callback(handler):
                handler.fillDict(self.params)
            self.addDelegate(SaxHandlerForLocationResponseHead() \
                .withDelegateHandlingEndedCallback(callback), name)
        elif 'DataSets' == name:
            def callback(handler):
                self.params['dataSets'] = handler.getDataSets(
                    self.dataSpecsOrNone)
            self.addDelegate(SaxHandlerForDataSets() \
                .withDelegateHandlingEndedCallback(callback), name)
    def getResponse(self, metadata):
        self.params['metadata'] = metadata
        return LocationDataResponse(**self.params)

class SaxHandlerForLocationInfoResponse(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.params = {}
    def startElementImpl(self, name, attributes):
        if 'Head' == name:
            def callback(handler):
                handler.fillDict(self.params)
            self.addDelegate(SaxHandlerForLocationResponseHead() \
                .withDelegateHandlingEndedCallback(callback), name)
    def getResponse(self, metadata):
        self.params['metadata'] = metadata
        return LocationInfoResponse(**self.params)

class SaxHandlerForRegressionResponse(SimpleSaxHandler):
    def __init__(self):
        SimpleSaxHandler.__init__(self)
        self.params = {}
        self.dataSetsOrNone = None
    def startElementImpl(self, name, attributes):
        if 'Head' == name:
            def callback(handler):
                handler.fillDict(self.params)
            self.addDelegate(SaxHandlerForLocationResponseHead() \
                .withDelegateHandlingEndedCallback(callback), name)
        elif 'DataSets' == name:
            def callback(handler):
                self.dataSetsOrNone = handler.getDataSets(None)
            self.addDelegate(SaxHandlerForDataSets() \
                .withDelegateHandlingEndedCallback(callback), name)
        elif 'Regressions' == name:
            def callback(handler):
                self.params['regressionsOrFailure'] = handler.getRegressions()
            self.addDelegate(SaxHandlerForRegressions(self.dataSetsOrNone) \
                .withDelegateHandlingEndedCallback(callback), name)
        elif 'Failure' == name:
            def callback(handler):
                self.params['regressionsOrFailure'] = handler.getFailure()
            self.addDelegate(SaxHandlerForFailure() \
                .withDelegateHandlingEndedCallback(callback), name)
    def getResponse(self, metadata):
        self.params['metadata'] = metadata
        return RegressionResponse(**self.params)

class SaxHandlerForResponse(SimpleSaxHandler):
    def __init__(self, requestOrNone):
        SimpleSaxHandler.__init__(self)
        self.requestOrNone = requestOrNone
    def startElementImpl(self, name, attributes):
        if 'Metadata' == name:
            def callback(handler):
                self.metadata = handler.getMetadata()
            self.addDelegate(SaxHandlerForResponseMetadata() \
                .withDelegateHandlingEndedCallback(callback), name)
        elif 'LocationDataResponse' == name:
            def callback(handler):
                self.response = handler.getResponse(self.metadata)
            self.addDelegate(
                SaxHandlerForLocationDataResponse(self.requestOrNone) \
                    .withDelegateHandlingEndedCallback(callback), name)
        elif 'LocationInfoResponse' == name:
            def callback(handler):
                self.response = handler.getResponse(self.metadata)
            self.addDelegate(
                SaxHandlerForLocationInfoResponse() \
                    .withDelegateHandlingEndedCallback(callback), name)
        elif 'RegressionResponse' == name:
            def callback(handler):
                self.response = handler.getResponse(self.metadata)
            self.addDelegate(
                SaxHandlerForRegressionResponse() \
                    .withDelegateHandlingEndedCallback(callback), name)
        elif 'Failure' == name:
            def callback(handler):
                self.response = handler.getResponse(self.metadata)
            self.addDelegate(SaxHandlerForFailureResponse() \
                .withDelegateHandlingEndedCallback(callback), name)

class DefaultResponseParser(object):
    def parseResponse(self, responseStream, request):
        handler = SaxHandlerForResponse(request)
        parse(responseStream, handler)
        return handler.response
