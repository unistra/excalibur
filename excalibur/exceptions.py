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