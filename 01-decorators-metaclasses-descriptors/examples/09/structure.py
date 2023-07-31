from collections import OrderedDict
from inspect import Parameter, Signature
import re


def _make_init(fields):
    code = 'def __init__(self, {}):\n'.format(', '.join(fields))
    for name in fields:
        code += f'    self.{name} = {name}\n'
    return code


def _make_setter(descriptor_cls):
    code = 'def __set__(self, instance, value, /):\n'
    for cls in descriptor_cls.__mro__:
        if 'set_code' in cls.__dict__:
            for line in cls.set_code():
                code += f'    {line}\n'
    return code


class DescriptorMeta(type):
    def __init__(cls, name, bases, namespace, **kwds):
        if '__set__' in namespace:
            raise AttributeError('Descriptors should implement set_code instead')
        exec(_make_setter(cls), globals(), namespace)
        cls.__set__ = namespace['__set__']


class Descriptor(metaclass=DescriptorMeta):
    def __init__(self, name=None):
        self.name = name

    @staticmethod
    def set_code():
        return [
            'instance.__dict__[self.name] = value'
        ]

    def __delete__(self, instance, /):
        raise AttributeError(f'Cannot delete')


class StructureMeta(type):
    @classmethod
    def __prepare__(metacls, name, bases, **kwds):
        return OrderedDict()

    def __new__(mcs, name, bases, namespace, **kwds):
        fields = [
            k for k, v in namespace.items()
            if isinstance(v, Descriptor)
        ]
        for name in fields:
            namespace[name].name = name
        if fields:
            exec(_make_init(fields), globals(), namespace)
        namespace['__fields__'] = fields
        return super().__new__(mcs, name, bases, namespace, **kwds)


class Structure(metaclass=StructureMeta):
    pass
            

class Typed(Descriptor):
    typ = object

    @staticmethod
    def set_code():
        return [
            'if not isinstance(value, self.typ):',
            '    raise TypeError(f"Wrong type, expected {self.typ.__name__}")',
        ]


class Integer(Typed):
    typ = int


class Float(Typed):
    typ = float


class String(Typed):
    typ = str


class Positive(Descriptor):
    @staticmethod
    def set_code():
        return [
            'if value < 0:',
            '    raise ValueError(f"Expected >= 0")',
        ]


class PositiveInteger(Integer, Positive):
    pass


class PositiveFloat(Float, Positive):
    pass


class Sized(Descriptor):
    def __init__(self, *args, max_length, **kwargs):
        self.max_length = max_length
        super().__init__(*args, **kwargs)

    @staticmethod
    def set_code():
        return [
            'if len(value) > self.max_length:',
            '    raise ValueError(f"Too big, expected length < {self.max_length}")',
        ]


class SizedString(String, Sized):
    pass


class Regex(Descriptor):
    def __init__(self, *args, pattern, **kwargs):
        self.pattern = re.compile(pattern)
        super().__init__(*args, **kwargs)

    @staticmethod
    def set_code():
        return [
            'if not self.pattern.match(value):',
            '    raise ValueError(f"Value did not match")',
        ]


class RegexString(String, Regex):
    pass


class SizedRegexString(SizedString, Regex):
    pass

