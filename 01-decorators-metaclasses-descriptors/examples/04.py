from inspect import Parameter, Signature


def make_signature(fields):
    return Signature([
        Parameter(name, Parameter.POSITIONAL_OR_KEYWORD)
        for name in fields
    ])


class add_signature:
    def __init__(self, fields):
        self.fields = fields

    def __call__(self, cls):
        cls.__signature__ = make_signature(cls)
        return cls


class Structure:
    __fields__ = ()

    def __init__(self, *args, **kwargs):
        bound = self.__signature__.bind(*args, **kwargs)
        for field, arg in bound.arguments.items():
            setattr(self, field, arg)


@add_signature(('x', 'y', 'z'))
class Point(Structure):
    pass
