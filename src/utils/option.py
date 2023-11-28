class _option:
    class OptionError(TypeError):
        pass

    def __setattr__(self, name, value):
        self.__dict__[name] = value


import sys

sys.modules[__name__] = _option()
