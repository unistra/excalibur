# -*- coding: utf-8 -*-


class ExcaliburError(Exception):
    """
    base exception for excalibur
    """
    def __init__(self, *args, **kwargs):
        super(ExcaliburError, self).__init__(*args, **kwargs)

    def __str__(self):
        return self.message


class ConfigurationLoaderError(ExcaliburError):
    """
    base exception for configuration loader
    """

    def __init__(self, message, *args, **kwargs):
        super(ConfigurationLoaderError, self).__init__(*args,**kwargs)
        self.message = '%s : %s ' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class PluginLoaderError(ExcaliburError):
    """
    base exception for plugin loader
    """

    def __init__(self, message, *args, **kwargs):
        super(PluginLoaderError, self).__init__(*args,**kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class ArgumentError(ExcaliburError):
    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(ArgumentError, self).__init__(*args,**kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class ArgumentCheckMethodNotFoundError(ExcaliburError):
    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(ArgumentCheckMethodNotFoundError, self).__init__(*args,**kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class CheckMethodError(ExcaliburError):
    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(CheckMethodError, self).__init__(*args,**kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class NoACLMatchedError(ExcaliburError):
    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(NoACLMatchedError, self).__init__(*args,**kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class RessourceNotFoundError(ExcaliburError):
    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(RessourceNotFoundError, self).__init__(*args,**kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class MethodNotFoundError(ExcaliburError):
    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(MethodNotFoundError, self).__init__(*args,**kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class HTTPMethodError(ExcaliburError):
    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(HTTPMethodError, self).__init__(*args,**kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class SourceNotFoundError(ExcaliburError):
    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(SourceNotFoundError, self).__init__(*args,**kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class IPNotAuthorizedError(ExcaliburError):
    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(IPNotAuthorizedError, self).__init__(*args,**kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class WrongSignatureError(ExcaliburError):
    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(WrongSignatureError, self).__init__(*args,**kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class DecodeAlgorithmNotFoundError(ExcaliburError):
    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(DecodeAlgorithmNotFoundError, self).__init__(*args,**kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message


class RunPluginsError(ExcaliburError):
    """
    check error
    """

    def __init__(self, message, *args, **kwargs):
        super(RunPluginsError, self).__init__(*args,**kwargs)
        self.message = '%s : %s' % (self.__class__.__name__, message)

    def __str__(self):
        return self.message
    