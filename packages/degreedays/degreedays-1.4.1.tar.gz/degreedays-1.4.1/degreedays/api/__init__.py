"""
Core Degree Days.net API classes, including :py:class:`DegreeDaysApi
<degreedays.api.DegreeDaysApi>` - the starting point for all API operations.
"""

from degreedays._private import _Immutable
import degreedays._private as private

try:
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        from degreedays.api.data import DataApi
        from degreedays.api.regression import RegressionApi
except ImportError:
    pass


__all__ = ('AccountKey', 'SecurityKey',
    'Request', 'Response',
    'ResponseMetadata',
    'RateLimit',
    'Failure',
    'FailureResponse',
    'DegreeDaysApiError', 'TransportError', 'FailureError',
    'RequestFailureError', 'InvalidRequestError', 'RateLimitError',
    'ServiceError',
    'DegreeDaysApi')

# lower-case letters apart from i, l, o, and digits apart from 0 and 1.  Doesn't
# include the hyphen which is allowed in certain places.
_KEY_CHARS = frozenset('abcdefghjkmnpqrstuvwxyz23456789')
_UPPER_CASE_KEY_LETTERS = frozenset('ABCDEFGHJKMNPQRSTUVWXYZ')
class _KeyValidator(object):
    def __init__(self, noBlocks, keyName): # type: (int, str) -> None
        expectedNoHyphens = noBlocks - 1
        self.minLength = noBlocks * 4
        self.expectedLength = self.minLength + expectedNoHyphens
        self.noBlocks = noBlocks
        self.keyName = keyName
    def _getValidCharOrNone(self, c): # type: (str) -> str | None
        if c in _KEY_CHARS:
            return c
        elif c in _UPPER_CASE_KEY_LETTERS:
            return c.lower()
        else:
            return None
    def getValidOrNone(self, s): # type: (str) -> str | None
        if len(s) < self.minLength:
            return None
        validChars = [] # type: list[str]
        for c in s:
            validChar = self._getValidCharOrNone(c)
            if validChar is not None:
                length = len(validChars)
                if length >= self.expectedLength:
                    # Too many valid chars means it's invalid
                    return None
                if length > 0 and (length + 1) % 5 == 0:
                    validChars.append('-')
                validChars.append(validChar)
        if len(validChars) != self.expectedLength:
            return None
        return ''.join(validChars)
    def getValidOrThrow(self, s): # type: (str) -> str
        valid = self.getValidOrNone(s)
        if valid is not None:
            return valid
        raise ValueError("Invalid %s - it should be a %d-character string made "
            "up of %d 4-character blocks separated by hyphens.  The 4-character"
            " blocks can contain lower-case Latin alphabet characters apart "
            "from 'i', 'l', and 'o', and numeric digits apart from '0' and "
            "'1'." % (self.keyName, self.expectedLength, self.noBlocks))

_ACCOUNT_KEY_VALIDATOR = _KeyValidator(3, 'stringAccountKey')
class AccountKey(_Immutable):
    """The shorter of the two API access keys, the account key identifies a
    unique Degree Days.net API account.

    :param str stringAccountKey: a Degree Days.net API account key.

    :raises TypeError: if `stringAccountKey` is not a `str`.

    :raises ValueError: if `stringAccountKey` cannot reasonably be parsed as a
        Degree Days.net API security key (see below for a description of the
        correct format).
    
    Each API account has two API access keys: an account key and a security key.
    `Sign up for a Degree Days.net API account
    <https://www.degreedays.net/api/signup>`__ to get your own API access keys.
    Or for development you can use the `free test account
    <https://www.degreedays.net/api/test>`__, though it comes with heavy
    restrictions on the locations you can fetch data for.

    The account key identifies the unique Degree Days.net API account. It is a
    public key in the sense that there is no need to keep it secret.
    
    Here's an example of an account key::

        k9vs-e6a3-zh8r
    
    Like the example above, all account keys are made up of three 4-character
    blocks separated by hyphens, with each non-hyphen character being one of the
    following::

        abcdefghjkmnpqrstuvwxyz23456789

    Account keys do not contain upper-case characters or any of the following
    easily-confused letters and digits: 'i', 'l', 'o', '0' and '1'. The same is
    true of security keys (the other type of access key). The intention is to
    make these keys easy for non-technical users to handle (e.g. if entering them
    into software that you've made for them).

    An :py:class:`AccountKey` object is a wrapper around a string account key.
    It is useful for validating account keys from user input, since the
    constructor will only allow an :py:class:`AccountKey` object to be created
    with a string of the correct format or a string that can be manipulated
    into the correct format without too much ambiguity."""
    __slots__ = ('__stringAccountKey',)
    def __init__(self, stringAccountKey): # type: (str) -> None
        self.__stringAccountKey = _ACCOUNT_KEY_VALIDATOR.getValidOrThrow(
            stringAccountKey)
    def _equalityFields(self):
        return self.__stringAccountKey
    def __repr__(self):
        return 'AccountKey(%s)' % self.__stringAccountKey
    def __str__(self):
        return self.__stringAccountKey
    @staticmethod
    def _check(param, paramName='accountKey'):
        # type: (AccountKey, str) -> AccountKey
        if type(param) is not AccountKey:
            raise TypeError(private.wrongTypeString(param, paramName,
                AccountKey, "AccountKey('test-test-test')"))
        return param


# TODO - look into security of strings and bytes in Python, and the way that key
# is expected, and think about whether you really want to be storing or
# converting to bytes here.
_SECURITY_KEY_VALIDATOR = _KeyValidator(13, 'stringSecurityKey')
_SECURITY_KEY_EXAMPLE = "SecurityKey('" + ('test-' * 13).rstrip('-') + "')"
class SecurityKey(_Immutable):
    """The longer of the two API access keys that are needed to use the Degree
    Days.net API, the security key is a private key that should be kept secret.

    :param str stringSecurityKey: a Degree Days.net API security key.

    :raises TypeError: if `stringSecurityKey` is not a `str`.

    :raises ValueError: if `stringSecurityKey` cannot reasonably be parsed as a
        Degree Days.net API security key (see below for a description of the
        correct format).
    
    Each API account has two API access keys: an account key and a security key.
    `Sign up for a Degree Days.net API account
    <https://www.degreedays.net/api/signup>`__ to get your own API access keys.
    Or for development you can use the `free test account
    <https://www.degreedays.net/api/test>`__, though it comes with heavy
    restrictions on the locations you can fetch data for.
    
    The security key is a private key that should be kept secret. In this
    respect it is like a password. The only entities that should have access to
    the security key are: Degree Days.net (systems and staff), the API account
    holder(s), and any trusted software systems that the API account holder(s)
    are using to manage their interactions with the API.

    Here's an example of a security key::
    
        b79h-tmgg-dwv5-cgxq-j5k9-n34w-mvxv-b5be-kqp5-b6hb-3bey-h5gg-swwd
    
    Like the example above, all security keys are made up of thirteen
    4-character blocks separated by hyphens, with each non-hyphen character
    being one of the following::

        abcdefghjkmnpqrstuvwxyz23456789

    Security keys do not contain upper-case characters or any of the following
    easily-confused letters and digits: 'i', 'l', 'o', '0' and '1'. The same is
    true of account keys (the other type of access key). The intention is to
    make these keys easy for non-technical users to handle (e.g. if entering
    them into software that you've made for them).

    A :py:class:`SecurityKey` object is a wrapper around the characters that
    constitute a string security key. It is useful for validating security keys
    from user input, since the constructor will only allow a
    :py:class:`SecurityKey` object to be created with a string of the correct
    format or a string that can be manipulated into the correct format without
    too much ambiguity."""
    __slots__ = ('__bytes',)
    def __init__(self, stringSecurityKey): # type: (str) -> None
        stringSecurityKey = _SECURITY_KEY_VALIDATOR.getValidOrThrow(
            stringSecurityKey)
        self.__bytes = stringSecurityKey.encode('utf-8')
    def _equalityFields(self):
        return self.__bytes
    def __repr__(self):
        return 'SecurityKey(string not included for security reasons)'
    def getBytes(self):
        """Returns a byte array containing the canonical security key's
        characters encoded into bytes using the UTF-8 character set."""
        return self.__bytes
    def toStringKey(self):
        """Returns the canonical string security key. Take care to ensure that
        the returned string doesn't accidentally appear in log files or error
        messages."""
        return self.__bytes.decode('utf-8')
    @staticmethod
    def _check(param, paramName='securityKey'):
        # type: (SecurityKey, str) -> SecurityKey
        if type(param) is not SecurityKey:
            raise TypeError(private.wrongTypeString(param, paramName,
                AccountKey, _SECURITY_KEY_EXAMPLE))
        return param

class Request(_Immutable):
    #2 inheritance-diagram:: degreedays.api.Request
    #   degreedays.api.data.LocationDataRequest
    #   degreedays.api.data.LocationInfoRequest
    #   degreedays.api.regression.RegressionRequest
    """Specifies an operation that you'd like the API to do (e.g. calculating
    a specific type of degree-day data for a specific location).

    This is an abstract class.  You wouldn't create a :py:class:`Request`
    directly, rather you would create one of its subclasses:
    :py:class:`degreedays.api.data.LocationDataRequest`,
    :py:class:`degreedays.api.data.LocationInfoRequest`, or
    :py:class:`degreedays.api.regression.RegressionRequest`.

    Every subclass of :py:class:`Request` has an equivalent subclass of
    :py:class:`Response`. For example,
    :py:class:`degreedays.api.data.LocationDataRequest` has
    :py:class:`degreedays.api.data.LocationDataResponse`."""
    __slots__ = ()
    def __init__(self):
        raise TypeError('Request is an abstract superclass.  To create an '
            'instance, create a LocationDataRequest, LocationInfoRequest, or '
            'RegressionRequest (all subclasses of Request).')

class RateLimit(_Immutable):
    """A snapshot of an API account's rate limit.

    The real state of an account's rate limit changes over time and as more
    requests are made to the API.  So a ``RateLimit`` object, which is a
    snapshot, is best checked soon after it is received.  It is accessible
    through the :py:class:`ResponseMetadata` that is included with
    each API :py:class:`Response` (accessible via :py:attr:`Response.metadata`)
    and with each :py:class:`RequestFailureError` (accessible via
    :py:attr:`RequestFailureError.responseMetadata`).
    """
    __slots__ = ('__requestUnitsAvailable', '__minutesToReset')
    def __init__(self, requestUnitsAvailable, minutesToReset):
        # type: (int, int) -> None
        self.__requestUnitsAvailable = private.checkInt(
            requestUnitsAvailable, 'requestUnitsAvailable')
        self.__minutesToReset = private.checkInt(
            minutesToReset, 'minutesToReset')
        if requestUnitsAvailable < 0:
            raise ValueError('Invalid requestUnitsAvailable (%s) - cannot be '
                '< 0.' % requestUnitsAvailable)
        if minutesToReset < 1:
            raise ValueError('Invalid minutesToReset (%s) - cannot be < 1.' %
                minutesToReset)
    def _equalityFields(self):
        return (self.__requestUnitsAvailable, self.__minutesToReset)
    def __repr__(self):
        return ('RateLimit(requestUnitsAvailable=%d, minutesToReset=%d)' %
            (self.__requestUnitsAvailable, self.__minutesToReset))
    @property
    def requestUnitsAvailable(self): # type: () -> int
        """The number of request units available for use before the next reset,
        at the time that this snapshot of the rate-limit state was taken."""
        return self.__requestUnitsAvailable
    @property
    def minutesToReset(self): # type: () -> int
        """The number of minutes until the rate limit is reset, at the time that
        this snapshot of the rate-limit state was taken."""
        return self.__minutesToReset
    @staticmethod
    def _check(param, paramName='rateLimit'):
        # type: (RateLimit, str) -> RateLimit
        if type(param) is not RateLimit:
            raise TypeError(private.wrongTypeString(param, paramName,
                RateLimit))
        return param

class ResponseMetadata(_Immutable):
    """Extra data that comes back with every response from the Degree Days.net
    API.

    The metadata for any particular response can be accessed via
    :py:attr:`Response.metadata` (if your API request succeeds and you get a
    :py:class:`Response` object back), or via
    :py:attr:`RequestFailureError.responseMetadata` (if a
    :py:class:`RequestFailureError` is thrown to indicate a failure in the
    server's processing of your API request)."""
    __slots__ = ('__rateLimit',)
    def __init__(self, rateLimit): # type: (RateLimit) -> None
        self.__rateLimit = RateLimit._check(rateLimit)
    def _equalityFields(self):
        return self.__rateLimit
    def __repr__(self):
        return 'ResponseMetadata(%r)' % self.__rateLimit
    @property
    def rateLimit(self): # type: () -> RateLimit
        """Details of the rate limit that is currently associated with the API
        account."""
        return self.__rateLimit
    @staticmethod
    def _check(param, paramName='responseMetadata'):
        # type: (ResponseMetadata, str) -> ResponseMetadata
        if type(param) is not ResponseMetadata:
            raise TypeError(private.wrongTypeString(param, paramName,
                ResponseMetadata))
        return param

class Failure(_Immutable):
    """Contains details of a failure in the server-side processing of all or
    part of an API request.
    
    .. _failure-codes:
    
    Failure codes
    -------------
    Every failure has a :py:attr:`code` that indicates the cause of the failure.

    These codes are named in a hierarchical way. For example, if a failure is
    caused by an invalid request, its code will begin with "InvalidRequest". The
    idea is that you can quickly test for broader types of failure code without
    having to know or itemize all the sub-types (like "InvalidRequestAccount"
    and "InvalidRequestSignature").

    New codes may be added into the API at any time. New codes might be
    sub-types of existing types (like if "InvalidRequestSomeNewCode" was added
    as a sub-type of "InvalidRequest"), or they might be completely new (like
    "SomeCompletelyNewCode"). If you're writing logic that checks for different
    failure codes, make sure that it won't blow up if it comes across a code
    that it doesn't recognize. Though **you are unlikely to need to deal with
    failure codes directly**, as API methods like
    :py:meth:`DataApi.getLocationData` and :py:meth:`DataSets.get`
    will automatically turn any failure codes into appropriate subclasses of
    :py:class:`FailureError`."""
    __slots__ = ('__code', '__message')
    def __init__(self, code, message): # type: (str, str) -> None
        self.__code = private.checkString(code, 'code')
        self.__message = private.checkString(message, 'message')
    def _equalityFields(self):
        return (self.__code, self.__message)
    def __repr__(self):
        return "Failure(code='%s', message='%s')" % (self.__code, self.__message)
    @property
    def code(self): # type: () -> str
        """The string :ref:`failure code <failure-codes>` associated with this
        failure."""
        return self.__code
    @property
    def message(self): # type: () -> str
        """The string message associated with this failure, providing
        explanatory information about the :py:attr:`code` and what went wrong.

        The format of messages, and any details contained within them, are
        unspecified and subject to change. By all means use them for logging and
        display purposes, but please don't parse specific details from them. If
        you need programmatic access to information that is only available in a
        message, please let us know so we can think about how we could make that
        information available in another format."""
        return self.__message
    @staticmethod
    def _check(param, paramName='failure'):
        # type: (Failure, str) -> Failure
        if type(param) is not Failure:
            raise TypeError(private.wrongTypeString(param, paramName, Failure))
        return param

class Response(_Immutable):
    #2 inheritance-diagram:: degreedays.api.Response
    #   degreedays.api.data.LocationDataResponse
    #   degreedays.api.data.LocationInfoResponse
    #   degreedays.api.regression.RegressionResponse
    """Models the API's response to a :py:class:`Request` (e.g. degree-day data
    returned in response to a request for that data).
    
    This is an abstract class.  Any :py:class:`Response` objects you receive
    from the API will be a subclass of this, with the type depending on the type
    of :py:class:`Request` you made.  A
    :py:class:`degreedays.api.data.LocationDataRequest` will give you a
    :py:class:`degreedays.api.data.LocationDataResponse`; a
    :py:class:`degreedays.api.data.LocationInfoRequest` will give you a
    :py:class:`degreedays.api.data.LocationInfoResponse`; and a
    :py:class:`degreedays.api.regression.RegressionRequest` will
    give you a :py:class:`degreedays.api.regression.RegressionResponse`."""
    __slots__ = ()
    def __init__(self):
        raise TypeError('This is an abstract superclass.  '
            'LocationDataResponse is a subclass that can be instantiated '
            'directly (though typically you would submit a LocationDataRequest '
            'and let the API create the LocationDataResponse automatically).')
    @property
    def metadata(self): # type: () -> ResponseMetadata
        """An object containing metadata sent back with every response from the
        API servers, including details of the account's current rate limit."""
        raise NotImplementedError()

class FailureResponse(Response):
    #1 inheritance-diagram:: FailureResponse
    """A type of API :py:class:`Response` that indicates a failure in the
    server-side processing of a :py:class:`Request`.

    You will probably only need to deal with this class directly if you are 
    throwing subclasses of :py:class:`RequestFailureError` for testing purposes
    (e.g. to test your code's handling of such exceptions).  In normal usage of
    this client library, any ``FailureResponse`` objects will be turned into
    :py:class:`RequestFailureError` objects automatically."""
    __slots__ = ('__metadata', '__failure')
    def __init__(self, metadata, failure):
        # type: (ResponseMetadata, Failure) -> None
        self.__metadata = ResponseMetadata._check(metadata, 'metadata')
        self.__failure = Failure._check(failure)
    def _equalityFields(self):
        # metadata is not considered in equality.
        return self.__failure
    def __repr__(self):
        return 'FailureResponse(%r, %r)' % (self.__metadata, self.__failure)
    @property
    def metadata(self): # type: () -> ResponseMetadata
        return self.__metadata
    @property
    def failure(self): # type: () -> Failure
        """The :py:class:`Failure` object that contains details of the failure
        in the API's server-side processing of the request."""
        return self.__failure
    @staticmethod
    def _check(param, paramName='failureResponse'):
        # type: (FailureResponse, str) -> FailureResponse
        if type(param) is not FailureResponse:
            raise TypeError(private.wrongTypeString(param, paramName,
                FailureResponse))
        return param

class DegreeDaysApiError(Exception):
    #1 inheritance-diagram:: degreedays.api.DegreeDaysApiError
    #   degreedays.api.InvalidRequestError
    #   degreedays.api.RateLimitError
    #   degreedays.api.ServiceError
    #   degreedays.api.data.LocationError
    #   degreedays.api.data.SourceDataError
    #   degreedays.api.TransportError
    """Superclass of all the API exceptions that you are likely to want to catch
    explicitly.

    .. _error-handling:
    
    Handling the exceptions thrown by this client library
    -----------------------------------------------------
    Subclasses of this exception are thrown by all the methods accessible
    through :py:class:`DegreeDaysApi` to indicate problems like network failure
    (:py:class:`TransportError`), service failure (:py:class:`ServiceError`) i.e.
    our server-side processing going wrong, a rate limit being reached
    (:py:class:`RateLimitError`), invalid authentication credientials
    (:py:class:`InvalidRequestError`), and other types of exception that are
    specific to the API operation in question.

    The likelihood of many of these exceptions occurring will depend on how you
    are using the API. For example, if your customers install your application
    and then enter their own :ref:`API access keys <access-keys>` into it, you
    might expect the odd :py:class:`InvalidRequestError` because of typos.
    However, such an exception would be less likely to occur if your application
    was a centrally-running background process that used a single API account to
    collect data. And consequently you might be less likely to want to handle
    :py:class:`InvalidRequestError` explicitly.

    So a typical approach would be to catch just those subclasses that you're
    interested in (if any), catching :py:class:`DegreeDaysApiError` last as a
    kind of catch all, or just letting any unhandled exceptions bubble up the
    call stack."""
    def __str__(self):
        # important to implement this well, cos people often print exceptions
        # like print(e): https://stackoverflow.com/questions/1483429/
        return repr(self) # we implement __repr__ on subclasses

class TransportError(DegreeDaysApiError):
    #1 inheritance-diagram:: degreedays.api.TransportError
    """Indicates an error transporting a request to the API servers or
    transporting a response back. Typically some sort of network or connection
    issue."""
    def __init__(self, message=None): # type: (str | None) -> None
        self.__message = private.checkStringOrNone(message, 'message')
    def __repr__(self):
        # __cause__ is added by raiseWrapped, not passed into the constructor,
        # but it's so important for TransportError we include it in the repr
        # anyway. Don't worry about not replicating the constructor exactly:
        # https://stackoverflow.com/questions/1436703/
        if hasattr(self, '__cause__'):
            # repr (%r) doesn't give great messages for the exceptions we
            # wrap, doing our own with class name + string is better.
            # Use " inside cos it fits better than ' with the str
            # implementations of typical exceptions too.
            causeBit = ', __cause__=%s("%s")' % (private.fullNameOfClass(
                self.__cause__.__class__), self.__cause__)
        else:
            causeBit = ''
        return '%s(message="%s"%s)' % (private.fullNameOfClass(
            self.__class__), self.__message, causeBit)

class FailureError(DegreeDaysApiError):
    #1 inheritance-diagram:: degreedays.api.FailureError
    #   degreedays.api.RequestFailureError
    #   degreedays.api.data.SourceDataError
    """Superclass of exceptions that indicate a :py:class:`Failure` in the API's
    processing of all or part of a request.

    Apart from :py:class:`TransportError`, all concrete subclasses of
    :py:class:`DegreeDaysApiError` are subclasses of :py:class:`FailureError`,
    and carry a coded :py:class:`Failure` which originates from the server-side
    processing of an API request.

    Most types of :py:class:`FailureError` extend
    :py:class:`RequestFailureError`, which indicates that the API servers
    completely failed to process an API request (sending back only a
    :py:class:`Failure` as their response). But a failure doesn't *have* to
    relate to a full request - it is possible for parts of a request to work and
    parts to fail.  Right now the only example of this is
    :py:class:`SourceDataError` which indicates that the API servers failed to
    generate a specific set of data as *part* of a batch request.

    .. _is-due-to-properties:

    `isDueToXXX` properties on subclasses of :py:class:`FailureError`
    -----------------------------------------------------------------
    Some of the subclasses of :py:class:`FailureError` have `isDueToXXX`-style
    methods. These work by inspecting the :ref:`failure code <failure-codes>` of
    the :py:class:`Failure` object that the exception carries.

    The `isDueToXXX` properties follow a simple pattern: they will always be
    `True` if the failure code starts with the `XXX` part of the method name.
    So, for example, :py:attr:`ServiceError.isDueToServiceTemporarilyDown` will
    be `True` if the code is "ServiceTemporarilyDown" or
    "ServiceTemporarilyDownForPostalCodeLookups" (a failure code that isn't
    actually in use at the time of writing, but that may come into use at some
    point in the future).

    If you're checking `isDueToXXX` properties, bear in mind that it's possible
    for *none* of them to be `True`. This client library doesn't expose all
    possible failure codes through the `isDueToXXX` properties, only the ones
    that are likely to arise through use of the client library, and only the
    ones that were defined at the time this version of the client library was
    released. New codes may be added into the API over time, and they shouldn't
    cause incompaiblities with code that you've already written to test the
    existing `isDueToXXX` properties.

    In a nutshell: when writing code that tests `isDueToXXX` properties (e.g. to
    decide what message to show in a UI), make sure that your code will work
    well if none of those properties are `True`."""
    def __init__(self, failure): # type: (Failure) -> None
        self.__failure = Failure._check(failure)
    @property
    def failure(self): # type: () -> Failure
        """The :py:class:`Failure` object containing details of the failure on
        the API servers that led to this exception on the client."""
        return self.__failure
    def _testCode(self, code): # type: (str) -> bool
        return self.__failure.code.startswith(code)
    def __repr__(self):
        # include the full name of the class cos if people do print(e), which
        # is common, it won't get included automatically.
        return '%s(%r)' % (private.fullNameOfClass(self.__class__),
            self.__failure)

class RequestFailureError(FailureError):
    #1 inheritance-diagram:: degreedays.api.RequestFailureError
    #   degreedays.api.InvalidRequestError
    #   degreedays.api.RateLimitError
    #   degreedays.api.ServiceError
    #   degreedays.api.data.LocationError
    """Superclass of exceptions that indicate that the API's processing of a
    request resulted in a :py:class:`Failure`.

    The key point here is that the API servers were not able to process the
    request at all, and their response contained only:
    
    * Details of the failure, exposed through the subclasses of this exception
      type and through the :py:class:`Failure` object itself (accessible via
      :py:attr:`FailureError.failure`).
    * Response metadata, accessible via the :py:attr:`responseMetadata` property
      of this exception."""
    def __init__(self, failureResponse): # type: (FailureResponse) -> None
        FailureResponse._check(failureResponse)
        FailureError.__init__(self, failureResponse.failure)
        self.__responseMetadata = failureResponse.metadata
    @property
    def responseMetadata(self): # type: () -> ResponseMetadata
        """The metadata from the :py:class:`FailureResponse` that brought
        details of this failure back from the API servers."""
        return self.__responseMetadata
    @staticmethod
    def _create(failureResponse):
        # type: (FailureResponse) -> RequestFailureError
        code = failureResponse.failure.code
        if code.startswith('InvalidRequest'):
            return InvalidRequestError(failureResponse)
        elif code.startswith('RateLimit'):
            return RateLimitError(failureResponse)
        elif code.startswith('Service'):
            return ServiceError(failureResponse)
        else:
            # Shouldn't happen, unless new codes are added in.
            return RequestFailureError(failureResponse)
    def __repr__(self):
        return '%s(%r)' % (private.fullNameOfClass(self.__class__),
            FailureResponse(self.responseMetadata, self.failure))

class InvalidRequestError(RequestFailureError):
    #1 inheritance-diagram:: degreedays.api.InvalidRequestError
    """Indicates that the API could not process a request because it was invalid
    in some way (e.g. authenticated with invalid :ref:`access keys
    <access-keys>`).

    This exception corresponds to any :ref:`failure code <failure-codes>`
    starting with "InvalidRequest".

    The ``isDueToInvalidRequestXXX`` properties of this class make it easy to
    test for the "InvalidRequestXXX" codes that you are likely to want to test
    for. There are also several "InvalidRequestXXX" codes that do not have
    corresponding ``isDueToInvalidRequestXXX`` convenience properties, but these
    codes should not arise through normal use of this Python client library. For
    example, there's an "InvalidRequestXml" code that you should never receive
    unless you have modified the mechanism that this Python client library uses
    to generate the XML requests (something you're unlikely to want to do).

    All "InvalidRequestXXX" codes will cause this exception to be thrown,
    irrespective of whether they have their own ``isDueToInvalidRequestXXX``
    properties. If, for some reason, you need to explicitly check for an
    "InvalidRequestXXX" code that does not have its own
    ``isDueToInvalidRequestXXX`` property, you can always check for it by
    testing the failure code string directly.

    If you're testing the ``isDueToInvalidRequestXXX`` properties, please do
    make sure that your code won't blow up if none of them are ``True``.

    See also:

    * :ref:`Failure codes <failure-codes>`
    * :ref:`isDueToXXX properties <is-due-to-properties>`"""
    def __init__(self, failureResponse): # type: (FailureResponse) -> None
        RequestFailureError.__init__(self, failureResponse)
    @property
    def isDueToInvalidRequestAccount(self):
        """`True` if the request failed because the :py:class:`AccountKey` was
        unrecognized (e.g. because of a typo) or the API account has been
        cancelled by the user or `automatically expired after a billing failure 
        <https://www.degreedays.net/api/account-management>`__; `False`
        otherwise.

        The account key would typically be set when creating
        :py:class:`DegreeDaysApi`."""
        return self._testCode('InvalidRequestAccount')
    @property
    def isDueToInvalidRequestForAccountPlan(self):
        """`True` if this failure came in response to a request for data that is
        not available on the API account plan associated with the
        :py:class:`AccountKey`; `False` otherwise.
        
        The Degree Days.net website has details of `the different account plans
        <https://www.degreedays.net/api/signup>`__ and `how to upgrade
        <https://www.degreedays.net/api/account-management>`__."""
        return self._testCode('InvalidRequestForAccountPlan')
    @property
    def isDueToInvalidRequestSignature(self):
        """`True` if this failure came in response to a request that was sent
        with an invalid signature, typically caused by a problem with the
        :py:class:`SecurityKey`; `False` otherwise.

        Signatures are used as part of the key-based security mechanism that
        protects the usage quotas associated with customer accounts. This Python
        client library generates all signatures automatically, so this type of
        failure should only come about if a signature is generated using an
        erroneous security key (e.g. one that was entered with a typo).

        The security key of the account is set when creating
        :py:class:`DegreeDaysApi`."""
        return self._testCode('InvalidRequestSignature')
    @property
    def isDueToInvalidRequestTimestamp(self):
        """`True` if this failure came in response to a request that was sent
        with an invalid timestamp, typically caused by an out-of-sync clock on
        the client machine; `False` otherwise.

        When a request is packaged up and sent to the API servers, a timestamp
        is included to indicate the time, in UTC (GMT), that the request was
        sent. This timestamp is checked against the server's clock as part of a
        system designed to prevent unwanted replays of previous requests.

        This type of failure can occur if the client's clock is badly out of
        sync (like 15 minutes or more from the real time). If the computer's
        clock *looks* right, and you're still getting this type of failure, then
        it's likely that the computer's clock is set with the wrong time-zone.
        The timestamps sent to the server are UTC timestamps, and, unless the
        computer's time-zone is set correctly, its concept of UTC time is likely
        to be out by at least an hour."""
        return self._testCode('InvalidRequestTimestamp')

class RateLimitError(RequestFailureError):
    #1 inheritance-diagram:: degreedays.api.RateLimitError
    """Indicates that the API servers did not process a request because the
    :py:class:`RateLimit` for the account's plan had been reached.

    The best way to handle this exception is often to wait until the rate limit
    is reset. You can figure out how long that is from the :py:class:`RateLimit`
    object, accessible through the :py:attr:`responseMetadata` property of this
    exception. Or you can upgrade your account to increase your rate limit.
    `Choose the API plan you want
    <https://www.degreedays.net/api/signup#plans>`__ and `email us 
    <https://www.degreedays.net/contact>`__ to let us know.

    This exception corresponds to any :ref:`failure code <failure-codes>`
    starting with "RateLimit".

    You can interrogate the :ref:`isDueToXXX <is-due-to-properties>` properties
    of this exception to find out more about the cause. There is only one such
    property at the moment, but more may be added in a future version of this
    client library."""
    def __init__(self, failureResponse): # type: (FailureResponse) -> None
        RequestFailureError.__init__(self, failureResponse)
    @property
    def isDueToRateLimitOnLocationChanges(self):
        """`True` if this failure was caused by a rate limit on the number of
        times a location-limited account can change the location(s) that they
        access data for; `False` otherwise.
        
        Location-limited accounts are low-end accounts that are used for
        fetching regular updates for a limited number of locations. The number
        of locations allowed depends on the location-limited account in
        question.

        Allowed locations are set automatically. If a location-limited account
        successfully fetches data for a given location, that location is
        assigned to the account, and the account is able to continue fetching
        data for that location as time goes on (e.g. fetching
        daily/weekly/monthly updates).
        
        A certain amount of location turnover is allowed. Offices and people
        move to new buildings, and occasionally weather stations go down and
        replacements need to be found (see
        :py:attr:`degreedays.api.data.LocationError.isDueToLocationNotSupported`
        for more on this). As new locations are added to an account's list of
        allowed locations, older locations are removed on a least-recently-used
        basis. There are limits on the number of "location changes" that a
        location-limited account can make in any given period of time. These
        limits aren't explicitly published, and may change over time, but the
        idea is that it should be very unlikely for a location-limited account
        to hit its limit on location changes. Location-limited accounts are
        built for a certain style of usage only (fetching regular updates for a
        mostly-fixed set of locations).

        **From a programming perspective, dealing with a rate limit on location
        changes is unlikely to be any different from dealing with the usual rate
        limit on the number of request units.** If you have a user-driven
        application, you might want to call this method to help you decide what
        message to show in the UI... But, if your program is a background task
        that fetches data at regular intervals, you probably won't need to
        distinguish between a limit on request units (all accounts have these)
        and a limit on location changes (only location-limited accounts have
        these). If an account hits a rate limit (whether on request units or
        location changes), you'll get a :py:class:`RateLimitError`, and you'll
        generally just want to wait the specified number of minutes
        (:py:attr:`RateLimit.minutesToReset`) until the rate limit is reset::

            except RateLimitError as e:
                minutesToWait = e.responseMetadata.rateLimit.minutesToReset
        """
        return self._testCode('RateLimitOnLocationChanges')

class ServiceError(RequestFailureError):
    #1 inheritance-diagram:: degreedays.api.ServiceError
    """Indicates that the API servers failed to process a request because of
    temporary downtime or an unexpected error (sorry!).

    This exception corresponds to any :ref:`failure code <failure-codes>`
    starting with "Service".

    You can interrogate the :ref:`isDueToXXX <is-due-to-properties>` properties
    of this exception to find out more about the cause.  But do note that it is
    possible for none of those properties to be `True` if a relevant new failure
    code is added into the API. Be prepared for this in your handling.
    """
    def __init__(self, failureResponse): # type: (FailureResponse) -> None
        RequestFailureError.__init__(self, failureResponse)
    @property
    def isDueToServiceTemporarilyDown(self):
        """`True` if this failure was caused by a temporary problem preventing
        the API service from functioning properly (sorry!); `False` otherwise.

        This might, for example, be caused by a temporary network error
        preventing our API servers from accessing the database of weather data
        that the calculation process relies upon. Or it could be caused by other
        essential systems being overloaded.

        The best way to handle this type of failure is usually to try the
        request again until it works (waiting a little while between repeated
        submissions). If you get this type of failure for one request, it is
        quite likely that some or all of your requests will fail in the same way
        until the problem is resolved (which hopefully won't take long)."""
        return self._testCode('ServiceTemporarilyDown')
    @property
    def isDueToServiceUnexpectedError(self):
        """`True` if this failure was caused by a unexpected error in the API
        service (sorry!); `False` otherwise.

        If an unexpected error in the API service should occur, it is quite
        likely that it would only be triggered by a specific request (e.g. a
        request for data from a particular weather station). This is different
        to the service going :py:attr:`temporarily down
        <isDueToServiceTemporarilyDown>` and affecting most or all requests
        until the problem is resolved.

        If a request triggers a "ServiceUnexpectedError" failure, there probably
        won't be any point in trying that particular request repeatedly. Other
        requests will probably continue to work OK, but the problem request, if
        repeatedly submitted, will probably repeatedly fail until the underlying
        bug in the system is addressed. This is the sort of thing that would
        typically take at least a day or two, or potentially much longer (some
        bugs are beyond our sphere of control).

        If you're getting this type of failure repeatedly, and it's getting in
        the way of what you're trying to achieve with the API, please email us to
        let us know. Our logging system should alert us each time an error like
        this occurs, but it's always useful to hear more information. Also, if
        it's not something we can fix on our end, we might well be able to
        suggest some sort of workaround."""
        return self._testCode('ServiceUnexpectedError')

class DegreeDaysApi(object):
    """**The starting point for all API operations.**  If you're new to this
    API, read the docs for this class first.

    **To create a** ``DegreeDaysApi`` **object**, use the
    :py:meth:`fromKeys` method. For example::

        api = DegreeDaysApi.fromKeys(
            AccountKey('test-test-test'),
            SecurityKey('test-test-test-test-test-test-test-test-test-test-test-test-test'))

    The :ref:`API access keys <access-keys>` above (account key and security
    key) are for the `free test account
    <https://www.degreedays.net/api/test>`__, which is heavily limited but
    usable for basic development and testing.  For much more flexibility and
    production use, you can `sign up for a full Degree Days.net API account
    <https://www.degreedays.net/api/signup>`__ to get your own API access keys.

    Assuming you have a ``DegreeDaysApi`` object called ``api``, as in the
    example code above, then you can make three main types of request (and get
    three main types of response) using the objects and methods accessible
    through that ``api`` object.  **The links below have more information and
    sample code** for each:

    * :py:meth:`api.dataApi.getLocationData(locationDataRequest)
      <degreedays.api.data.DataApi.getLocationData>` to fetch degree-day
      data and/or hourly temperature data from the API, for any specified
      weather station, postal/zip code, or longitude/latitude position.
    * :py:meth:`api.dataApi.getLocationInfo(locationInfoRequest)
      <degreedays.api.data.DataApi.getLocationInfo>` to find out what weather
      station the API would use to represent any specified postal/zip code or
      longitude/latitude position.
    * :py:meth:`api.regressionApi.runRegressions(regressionRequest)
      <degreedays.api.regression.RegressionApi.runRegressions>` to send your
      energy data to the API so the API can test thousands of regressions
      against it (using HDD and CDD with a wide range of base temperatures), and
      return the regressions that give the best statistical fit (including base
      temperatures and coefficients you can use for further calculations).

    More on how the API works: requests, responses, and errors
    ----------------------------------------------------------
    * You create a :py:class:`Request` object that specifies what you want the
      API to do. There are different types of ``Request`` for different API
      operations, like :py:class:`LocationDataRequest
      <degreedays.api.data.LocationDataRequest>` for requesting degree-day data.
    * Your ``Request`` gets processed. (Internally this library will turn your
      request into XML, send it to the API servers, and parse the XML response
      that the servers send back.)
    * You'll get a :py:class:`Response` object back (assuming no errors). There
      are different types of ``Response``, mirroring the different types of
      ``Request``. For example, if you use a ``LocationDataRequest`` to request
      some degree-day data, successful processing will give you a
      :py:class:`LocationDataResponse
      <degreedays.api.data.LocationDataResponse>`.

    If something goes wrong in sending your request to the API servers, or in
    getting your response back, you'll get a :py:class:`TransportError`.
    Typically that means there was a network error of some sort.

    If your request was transported to the API servers OK, but couldn't be
    processed properly, you'll get a :py:class:`RequestFailureError` instead of
    a ``Response``. There are different types of ``RequestFailureError`` for the
    different types of ``Request``. For example, take a look at the docs for
    :py:class:`degreedays.api.data.DataApi.getLocationData` to see the
    exceptions that can be thrown if the API servers can't process a
    ``LocationDataRequest``. The exceptions should help you determine the cause
    of the failure and decide what to do next.

    .. _access-keys:

    API access keys: the account key and the security key
    -----------------------------------------------------
    Every customer's API account is associated with two access keys: a public
    "account key" and a private "security key", both of which are generated
    automatically on `signup <https://www.degreedays.net/api/signup>`__. These
    keys are used to secure each request sent to the API by the customer (or by
    software trusted to work on their behalf), to protect the API usage that the
    customer has paid to enable.

    **The account key** is used to uniquely identify the customer account. It is
    a public key in the sense that there is no need to keep it secret.

    Here's an example account key::

        k9vs-e6a3-zh8r

    **The security key** is a private key that should be kept secret. In this
    respect it is like a password. The only entities that should have access to
    the security key are: Degree Days.net (systems and staff), the API account
    holder(s), and any trusted software systems that the API account holder(s)
    are using to manage their interactions with the API.

    Here's an example security key::

        b79h-tmgg-dwv5-cgxq-j5k9-n34w-mvxv-b5be-kqp5-b6hb-3bey-h5gg-swwd

    For more on the format of these access keys, see the notes in
    :py:class:`AccountKey` and :py:class:`SecurityKey`.

    To get your own API access keys you can `sign up for an API account here 
    <https://www.degreedays.net/api/signup>`__.  Or, for basic development and
    testing, you can try out the `free test account
    <https://www.degreedays.net/api/test>`__.

    Using a ``DegreeDaysApi`` object
    -----------------------------------
    You'd typically create just one ``DegreeDaysApi`` object for use throughout
    your application. It is perfectly safe for use from multiple threads. But
    there's nothing to stop you creating and using as many instances as you
    like.

    For more information and code samples on how to use a ``DegreeDaysApi``
    object that you have created (let's call it ``api`` as per the example
    further above), please see the docs for the 3 main methods accessible
    through it:

    * :py:meth:`api.dataApi.getLocationData(locationDataRequest)
      <degreedays.api.data.DataApi.getLocationData>`
    * :py:meth:`api.dataApi.getLocationInfo(locationInfoRequest)
      <degreedays.api.data.DataApi.getLocationInfo>`
    * :py:meth:`api.regressionApi.runRegressions(regressionRequest)
      <degreedays.api.regression.RegressionApi.runRegressions>`"""
    def __init__(self, requestProcessor):
        """:meta private:"""
        self.__requestProcessor = requestProcessor
    @staticmethod
    def fromKeys(accountKey, securityKey):
        # type: (AccountKey, SecurityKey) -> DegreeDaysApi
        """Creates a ``DegreeDaysApi`` object configured with the specified
        API access keys.

        :param AccountKey accountKey: a wrapper around the string account key
            that identifies the Degree Days.net API account.
    
        :param SecurityKey securityKey: a wrapper around the string security key
            associated with the account.
    
        :raises TypeError: if either `accountKey` is not an
            :py:class:`AccountKey` or `securityKey` is not a
            :py:class:`SecurityKey`."""
        AccountKey._check(accountKey)
        SecurityKey._check(securityKey)
        # This import must come below the stuff above like FailureResponse and
        # TransportException that _processing imports itself.  Otherwise I guess
        # it makes some sort of circular import issue.  Really this module
        # shouldn't depend on processing, but I think it's OK for the
        # convenience that this method brings.
        from degreedays.api._processing import _buildXmlHttpRequestProcessor
        return DegreeDaysApi(_buildXmlHttpRequestProcessor(
            accountKey, securityKey))
    @property
    def dataApi(self): # type: () -> DataApi
        """A :py:class:`degreedays.api.data.DataApi` object that provides access
        to the API's data-related operations."""
        from degreedays.api.data import DataApi
        return DataApi(self.__requestProcessor)
    @property
    def regressionApi(self): # type: () -> RegressionApi
        """A :py:class:`degreedays.api.regression.RegressionApi` object that
        provides access to the API's regression-related operations."""
        from degreedays.api.regression import RegressionApi
        return RegressionApi(self.__requestProcessor)
