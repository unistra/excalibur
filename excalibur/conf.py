# -*- coding: utf-8 -*-


class Sources(object):

    """
    """
    structure_type = {'3': 'project', '1': 'flat'}

    def get_level(self):
        """
        """
        def find_plugins(l, i):
            where_to_search = l[0] if type(l) == list else l
            if "plugins" in where_to_search.keys():
                return i
            else:
                i = i + 1
                return find_plugins(where_to_search.values(), i)
        return find_plugins(self.__dict__, 0)

    def __getitem__(self, key):
        """
        """
        ret = None
        try:
            ret = getattr(self, key)
        except AttributeError as ae:
            raise KeyError()
        return ret

    def keys(self):
        """
        """
        return self.__dict__.keys()

    def values(self):
        """
        """
        return self.__dict__.values()


class Ressources(object):

    """
    """

    def __init__(self):
        """
        """

    def __getitem__(self, key):
        """
        """
        ret = None
        try:
            ret = getattr(self, key)
        except AttributeError as ae:
            raise KeyError()
        return ret

    def keys(self):
        """
        """
        return self.__dict__.keys()


class Acl(object):

    """
    """

    def __getitem__(self, key):
        """
        """
        ret = None
        try:
            ret = getattr(self, key)
        except AttributeError as ae:
            raise KeyError()
        return ret
