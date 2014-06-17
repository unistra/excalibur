# -*- coding: utf-8 -*-


class ExcaliburError(Exception):

    """
    base exception for excalibur
    """

    def __init__(self, *args, **kwargs):
        super(ExcaliburError, self).__init__(*args, **kwargs)




class ExcaliburClientError(ExcaliburError):

    """
    base exception for excalibur
    """

    def __init__(self, *args, **kwargs):
        super(ExcaliburClientError, self).__init__(*args, **kwargs)



class ExcaliburInternalError(ExcaliburError):

    """
    base exception for excalibur
    """

    def __init__(self, *args, **kwargs):
        super(ExcaliburInternalError, self).__init__(*args, **kwargs)



class ConfigurationLoaderError(ExcaliburInternalError):

    """
    base exception for configuration loader
    """

    def __init__(self, message, *args, **kwargs):
        super(ConfigurationLoaderError, self).__init__(*args, **kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class PluginLoaderError(ExcaliburInternalError):

    """
    base exception for plugin loader
    """

    def __init__(self, message, *args, **kwargs):
        super(PluginLoaderError, self).__init__(*args, **kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message
    
class PluginRunnerError(ExcaliburInternalError):

    """
    base exception for plugin runner
    """

    def __init__(self, message, *args, **kwargs):
        super(PluginRunnerError, self).__init__(*args, **kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class ArgumentError(ExcaliburClientError):

    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(ArgumentError, self).__init__(*args, **kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class ArgumentCheckMethodNotFoundError(ExcaliburInternalError):

    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(ArgumentCheckMethodNotFoundError, self).__init__(*args, **kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class CheckMethodError(ExcaliburInternalError):

    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(CheckMethodError, self).__init__(*args, **kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class NoACLMatchedError(ExcaliburClientError):

    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(NoACLMatchedError, self).__init__(*args, **kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class RessourceNotFoundError(ExcaliburClientError):

    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(RessourceNotFoundError, self).__init__(*args, **kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class MethodNotFoundError(ExcaliburClientError):

    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(MethodNotFoundError, self).__init__(*args, **kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class HTTPMethodError(ExcaliburClientError):

    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(HTTPMethodError, self).__init__(*args, **kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class SourceNotFoundError(ExcaliburClientError):

    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(SourceNotFoundError, self).__init__(*args, **kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class IPNotAuthorizedError(ExcaliburClientError):

    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(IPNotAuthorizedError, self).__init__(*args, **kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class WrongSignatureError(ExcaliburClientError):

    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(WrongSignatureError, self).__init__(*args, **kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class DecodeAlgorithmNotFoundError(ExcaliburInternalError):

    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(DecodeAlgorithmNotFoundError, self).__init__(*args, **kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message

