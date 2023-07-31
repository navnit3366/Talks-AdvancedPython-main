from inspect import Parameter, Signature


def make_signature(fields):
    return Signature([
        Parameter(name, Parameter.POSITIONAL_OR_KEYWORD)
        for name in fields
    ])


class StructureMeta(type):
    def __new__(mcs, name, bases, namespace, **kwds):
        cls = super().__new__(mcs, name, bases, namespace, **kwds)
        cls.__signature__ = make_signature(cls.__fields__)
        return cls


class Structure(metaclass=StructureMeta):
    __fields__ = ()

    def __init__(self, *args, **kwargs):
        bound = self.__signature__.bind(*args, **kwargs)
        for field, arg in bound.arguments.items():
            setattr(self, field, arg)



class Point(Structure):
    __fields__ = ('x', 'y', 'z')


class Host(Structure):
    __fields__ = ('address', 'port')


