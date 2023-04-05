class _option:
    class OptionError(TypeError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.OptionError("Can't rebind option (%s)" % name)
        self.__dict__[name] = value


import sys

sys.modules[__name__] = _option()
