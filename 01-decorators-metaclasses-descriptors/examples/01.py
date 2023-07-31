
def log_attributes(cls):
    orignial_getattribue = cls.__getattribute__

    def __getattribute__(self, name):
        value = orignial_getattribue(self, name)
        print(f'Get: {name} -> {value}')
        return value

    cls.__getattribute__ = __getattribute__
    return cls


@log_attributes
class Host:
    def __init__(self, address, port):
        self.address = address
        self.port = port

