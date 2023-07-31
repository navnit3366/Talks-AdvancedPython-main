from inspect import Parameter, Signature
import re


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
            
class Descriptor:
    def __init__(self, name=None):
        self.name = name

    def __set__(self, instance, value, /):
        instance.__dict__[self.name] = value

    def __delete__(self, instance, /):
        raise AttributeError(f'Cannot delete')
    

class Typed(Descriptor):
    typ = object

    def __set__(self, instance, value, /):
        if not isinstance(value, self.typ):
            raise TypeError(f'Wrong type, expected {self.typ.__name__}')
        super().__set__(instance, value)


class Integer(Typed):
    typ = int


class Float(Typed):
    typ = float


class String(Typed):
    typ = str


class Positive(Descriptor):
    def __set__(self, instance, value, /):
        if value < 0:
            raise ValueError(f'Expected >= 0')
        super().__set__(instance, value)


class PositiveInteger(Integer, Positive):
    pass


class PositiveFloat(Float, Positive):
    pass


class Sized(Descriptor):
    def __init__(self, *args, max_length, **kwargs):
        self.max_length = max_length
        super().__init__(*args, **kwargs)

    def __set__(self, instance, value, /):
        if len(value) > self.max_length:
            raise ValueError(f'Too big, expected length < {self.max_length}')
        super().__set__(instance, value)


class SizedString(String, Sized):
    pass


class Regex(Descriptor):
    def __init__(self, *args, pattern, **kwargs):
        self.pattern = re.compile(pattern)
        super().__init__(*args, **kwargs)

    def __set__(self, instance, value, /):
        if not self.pattern.match(value):
            raise ValueError(f'Value did not match')
        super().__set__(instance, value)


class RegexString(String, Regex):
    pass


class SizedRegexString(SizedString, Regex):
    pass


class Host(Structure):
    __fields__ = ('address', 'port')
    address = SizedRegexString('address', max_length=15, pattern=r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')
    port = PositiveInteger('port')

