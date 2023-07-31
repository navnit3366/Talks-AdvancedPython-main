
# Title Slide

- Decorators and Metaclasses and Descriptors &mdash; Oh My!

# Requirements
#TODO check requirements & add links
- Python 3.3 minimum
- Link to GitHub repo with sample code

# Introduction
- Python 3 and metaprogramming

## Metaprogramming
- Code that manupulates code
- e.g.
	- decorators
	- metaclasses
	- descriptors
- Used extensively in frameworks and libraries
- Gives a better understanding of how python works

# DRY
- Don't repeat yourself
	- multiple times on slide
- Avoid repetition because
	- slow to write
	- hard to read
	- difficult to modify

# Inspiration
- David Beazley - Python 3 Metaprogramming - Pycon 2013

# Preliminaries
## Building Blocks
### Statements
- Do things in the program
- Execute with two scopes
	- global (module dictionary)
	- locals (enclosing function, class, etc)

### Functions
- Definition example
- Base code unit
	- Module-level
	- Class methods
- Calling conventions
	- Positional args
	- Keyword args
	- Default args
		- set at definition time
		- immutable!
	- `*args` and `**kwargs`
	- Keyword-only args
	- Positional-only args
- Closures
	- Functions returning functions
	- Local variables are captured

### Classes
- Members
	- Static methods
	- Class variables & methods
	- Instance variables & methods
- Dunder methods allow for customisation of almost everything
- Inheritance
- Objects = dictionaries

# Basics
Motivating example: debugging

```python
def add(x, y):
	return x + y
```

Add debugging to test the function

```python
def add(x, y):
	print(f'Calling add with arguments `x={x}` and `y={y}`')
	result = x + y
	print(f'add returned `{result}`)
	return result
```

More functions to debug
- `add`
- `sub`
- `mul`
- `div`

Lots of repeated code

## Decorators
- Function which creates a wrapper around another

```python
from functools import wraps

def debug(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		print(f'Calling {func.__qualname__} with', args, kwargs)
		result = func(*args, **kwargs)
		print(f'{func.__qualname__} returned {result}')
		return result
	return wrapper
```

- Create wrapper function which `wraps` the input `func`
- n.b. `wraps` is another decorator
	- copies the name, doc string, and attributes of the original function to the new one
	- demonstrate weirdness from not using `wraps`

- The `@decorator` syntax is sugar for
```python
def foo(a, b, c):
	...
	
foo = decorator(foo)
```

- Example use
```python
@debug
def add(x, y):
	return x + y
	
@debug
def sub(x, y):
	return x - y
	
@debug
def mul(x, y):
	return x * y
	
@debug
def div(x, y):
	return x / y
```

- Much less repetition and code is cleaner (demo functionality)

- We could quite easily add logging or a special 'debug mode'
	- we can change the decorator independently of the code using it

- Add a debugging prefix as an argument
	- first with nested functions
	- add the ability to use `@debug` instead of `@debug()` if no prefix is supplied

## Class Decorators
- Suppose we want to add debug information to all methods of a class

```python
def debugmethods(cls):
	for name, value in vars(cls).items():
		if callable(val):
			setattr(cls, name, debug(val))
	return cls
```

- Outline how the above code works
- Only works for instance methods

### Debugging member access
- If we override `__getattribute__`, we can debug attribute access
```python
def debugattr(cls):
	orig_getattribute = cls.__getattribute__

	def __getattribute__(self, name):
		value = orig_getattribute(self, name)
		print(f'Get: {name} -> {value}')
		return value

	cls.__getattribute__ = __getattribute__
	return cls
```

- Demonstrate on simple `Point` class

- What if we want to debug all the subclasses of a class?
	- show mess

- Solution: metaclass which applies `debugattr` in `__new__` to the newly created class object
	- show definition and usage

# Types
- In Python, all values have a type
- This type is itself a value - so it has a type

```python
>>> type(5) == int
>>> type(int) == type
>>> type(type) == type
```

- `type` is a built in class

- How is a class created?
```python
class Greeter(Base):
	def __init__(self, name):
		self.name = name

	def greet(self):
		print(f'Hello, {self.name}')
```

1) The body is isolated
```python
body = '''
	def __init__(self, name):
		self.name = name

	def greet(self):
		print(f'Hello, {self.name}')
'''
```

2) The class dictionary is created to hold the local namespace
```python
clsdict = type.__prepare__('Greeter', (Base,))
```
- By default, `type.__prepare__` returns a `dict`

3) Body is executed into `clsdict`
```python
exec(body, globals(), clsdict)
```

```python
>>> clsdict
{
	'__init__': <function __init__ at 0x...>,
	'greet': <function greet at 0x...>
}
```

4) The class is constructed as an instance of `type`
```python
Greeter = type('Greeter', (Base,), clsdict)
```

```python
>>> Greeter
<class 'Greeter'>
>>> g = Greeter('world')
>>> g.greet()
Hello, world!
```

- `metaclass` is a keyword argument which is used to set a class to create the type
	- by default, `metaclass=type`

- New metaclasses can be defined by inheriting from `type`
	- typically override either `__new__` or `__init__`

- Metaclasses get information about class definitions when the class is defined
	- they can both inspect and modify this data
	- similar to a class decorator
- Unlike class decorators, metaclasses are inherited

# Progress Report
- Mostly wrapping and rewriting
- Decorators can wrap functions and classes
- Metaclasses can interfere with classes and their descendants

# Structures
#TODO Change friends to a simpler field
```python
class Person:
	def __init__(self, name, age, friends=None):
		self.name = name
		self.age = age
		self.friends = [] if friends is None else friends

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class Host:
	def __init__(self, address, port):
		self.address = address
		self.port = port
```

- Lots of boilerplate!
	- We'll pretend for now that the `dataclasses` module doesn't exist

- We'll be iterating on this solution to remove as much boilerplate as possible (and then make it a bit more abstract)

## Solution 1
- Create a class `Structure` which has a class member `__fields__` (defaults to `[]`).
- The initialiser of `Structure` takes `self` and `*args`.
	- Ensure `args` is the same length as `__fields__`
	- Iterate over `__fields__` and `args` simultaneously, setting each field to the given value

- Other classes inherit from `Structure` and declare a `__fields__` member to be a list of the names of the fields

### Issues
- No keyword args
- Missing signatures
```python
>>> import inspect
>>> print(inspect.signature(MyStructure))
(*args)
```

## Solution 2
- Build a function signature object
```python
>>> from inspect import Parameter, Signature
>>> fields = [ ... ]
>>> params = [Parameter(name, Parameter.POSITIONAL_OR_KEYWORD) for name in fields]
>>> sig = Signature(params)
```

- Having the signature allows us to bind arguments to parameters
- Both positional and keyword arguments now work
- Providing too many or too few arguments also works

### Issues
- Now every class must define `__signature__`, which is always assigned to the result of calling `make_signature` on the fields.

- We could either use decorators or metaclasses
	- Which is more appropriate?

## Solution 3.1
- Create a class decorator to add a signature to the class
```python
class add_signature:
	def __init__(self, *names):
		self.names = names

	def __call__(self, cls):
		cls.__signature__ = make_signature(self.names)
		return cls
```

- Show usage

## Solution 3.2
- Create a metaclass, `StructureMeta`, which, in `__new__`:
	1) creates class object with a call to the `super` implentation
	2) makes a signature from `clsobj.__fields__`
	3) sets `__signature__` to the signature
- Create a class `Structure` with metaclass `StructureMeta` which by default has `__fields__` set to `[]` and, in `__init__`:
	1) binds `*args` and  `**kwargs` to `__signature__`
	2) loops through `bound.arguments.items()` to set each field appropriately

### Considerations
- If the `Structure` class is to be expanded, it may be useful for `__fields__` to still exist in the class (e.g. for `__repr__`)
- Typechecking might be important

- Whilst more complex, metaclasses are probably more appropriate as here, the goal is inheritance

### Issues
- Correctness
	- Duck typing
```python
p = Person('Fred', 21, [])
p.name = 42
p.age = 'young at heart'
p.friends = 1j
```
- Maybe we should just use Rust

## Solution 4
- `@property`
```python
class Person(Structure):
	__fields__ = ['name', 'age', 'friends']

	@property
	def age(self):
		return self._age

	@age.setter
	def age(self, value):
		if not isinstance(value, int):
			raise TypeError(f'Expected age to be an int, got "{value}"')
		if value < 0:
			raise ValueError(f'People must be at least 0 years old')
		if value > 150:
			raise ValueError(f'People can\'t be older than 150')
		self._age = value
```

- Demo improved code

### Issues
- Lots of boilerplate
- Imagine having multiple positive integer fields

- How can we simplify this?
- We want (enforced) type checking _AND_ value checking

## Solution 5
- Descriptors

- Properties are implemented with descriptors
```python
class Descriptor:
	def __get__(self, instance, cls):
		...

	def __set__(self, instance, value):
		...

	def __delete__(self, instance, value):
		...

class MyClass:
	x = Descriptor()
```

```python
>>> c = MyClass()
>>> c.x          # x.__get__(c, MyClass)
>>> c.x = value  # x.__set__(c, value)
>>> del c.x      # x.__delete__(c)
```

### A Simple Descriptor
```python
class Descriptor:
	def __init__(self, name=None):
		self.name = name

	def __get__(self, instance, cls):
		if instance is None:
			return self
		return instance.__dict__[self.name]

	def __set__(self, instance, value):
		instance.__dict__[self.name] = value

	def __delete__(self, instance):
		del instance.__dict__[self.name]
```

- If `__get__` simply returns the value from `instance.__dict__`, we don't need to provide it

```python
class Descriptor:
	def __init__(self, name=None):
		self.name = name

	def __set__(self, instance, value):
		instance.__dict__[self.name] = value

	def __delete__(self, instance):
		raise AttributeError(f'Can\'t delete {self.name}')
```

### Usage
```python
class Person(Structure):
	__fields__ = ['name', 'age', 'friends']
	name = Descriptor('name')
	age = Descriptor('age')
	friends = Descriptor('friends')
```

### Type Checking
- We can now start to build type checking

- Descriptor class `Typed`, extends `Descriptor`
	- Class variable `typ = object`
	- Override `__set__`
		- Checks the new value is an instance of `self.typ`
		- If the check passes, call `super().__set__(instance, value)`
- Specialised subclasses of `Typed`, overriding `typ`

| `Typed`   | `type`  | 
| --------- | ------- |
| `Integer` | `int`   |
| `Float`   | `float` |
| `String`  | `str`   |
| `List`    | `list`  |

### Usage
```python
class Person(Structure):
	__fields__ = ['name', 'age', 'friends']
	name = String('name')
	age = Integer('age')
	friends = List('friends')
```

### Value Checking
```python
class Positive(Descriptor):
	def __set__(self, instance, value):
		if value < 0:
			raise ValueError('Expected value >= 0, got "{value}"')
		super().__set__(instance, value)
```

- We can then use this as a mixin class

|     |     |     |
| --- | --- | --- |
| `PositiveInteger` | `Integer` | `Positive` |
| `PositiveFloat` | `Float` | `Positive` |

- Order matters
	- We want first to check the type, then that `value` is positive

# Method Resolution Order

```python
class PositiveInteger(Integer, Positive):
	pass
```

```python
>>> PositiveInteger.__mro__
(
	<class 'PositiveInteger'>,
	<class 'Integer'>,
	<class 'Typed'>,
	<class 'Positive'>,
	<class 'Descriptor'>,
	<class 'object'>
)
```

- When trying to access a member of `PositiveInteger` (or one of it's instances), Python looks at the `__mro__` attribute and looks at the items in order.
- The `__mro__` attribute is readonly

# Structures (cont.)
## Length Checking
```python
class Sized(Descriptor):
	def __init__(self, *args, maxlen, **kwargs):
		self.maxlen = maxlen
		super().__init__(*args, **kwargs)

	def __set__(self, instance, value):
		...  # implement properly
```

- Implement `SizedString`
- Reimplement `Person` with `name` being a `SizedString('name', maxlen=12)`
- Demo creating a person with an appropriately sized name and trying to set it to too long of a name

## Pattern Matching
- Class `Regex` inherits from `Descriptor`, takes `pat` as a keyword argument, which it passes to `re.compile` before storing
- `__set__` fails if `not self.pattern.match(value)`

- New desciptors to make:
	- `RegexString`
	- `SizedRegexString`

- Update `Person.name` to be a `SizedRegexString('name', maxlen=12, pat=r'[A-Za-z]+$')`
- Demo that `Person.name` can't be set to an invalid string

## Issues
- Still lots of repetition
- Signatures and type/value checking not unified

# Mixin Classes
- How do mixin classes with different signatures work?
	- Keyword-only args
	- We isolate the ones we need and pass the rest on
	- We could also pass on our own keyword arguments in case some else needs them

# Structures (cont.)
## Solution 6
```python
from collections import OrderedDict

class StructMeta(type):
	@classmethod
	def __prepare__(cls, name, bases):
		# We use OrderedDict to preserve the definition order
		return OrderedDict()

	def __new__(mcs, name, bases, clsdict):
		fields = [k for k, v in clsdict.items() if isinstance(v, Descriptor)]
		for name in fields:
			clsdict[name].name = name

		cls = super().__new__(mcs, name, bases, dict(clsdict))
		cls.__signature__ = make_signature(fields)
		cls.__fields__ = fields
		return cls

class Person(Structure):
	name = SizedRegexString(maxlen=12, pat=r'[A-Za-z]+$')
	age = PositiveInteger()
	friends = List()
```

- We could create a subclass of `OrderedDict` which raises an error if the given key already exists, and use this in place of `OrderedDict`
- This would prevent duplicate definitions in the class

# Some Tests
## Option 1
```python
class Person:
	def __init__(self, name, age, friends):
		self.name = name
		self.age = age
		self.friends = friends
```

## Option 2
```python
class Person(Structure):
	name = SizedRegexString(maxlen=12, pat=r'[A-Za-z]+$')
	age = PositiveInteger()
	friends = List()
```

## Test results
#TODO Populate test results

| Test | Simple | Meta |
| --- | --- | --- |
| Instance creation `p = Person('Fred', 21, [])` | | |
| Attribute lookup `p.age` | | |
| Attribute assignment `p.age = 22` | | |
| Attribute assignment `p.name = 'Gertrude'` | | |

- Display results on graph

## Reflection
#TODO Update this section when test results are in
- Large bottlenecks
	- Signature enforcement
	- Multiple inheritance in descriptors

# Code Generation
## Instance Creation
```python
def _make_init(fields):
	code = 'def __init__(self, {}):\n'.format(', '.join(fields))
	for name in fields:
		code += f'    self.{name} = {name}\n'
	return code
```

```python
class StructMeta(type):
	...

	def __new__(mcs, name, bases, clsdict):
		fields = [k for k, v in clsdict.items() if isinstance(v, Descriptor)]
		for name in fields:
			clsdict[name].name = name
		if fields:
			exec(_make_init(fields), globals(), clsdict)
		cls = super().__new__(cls, name, bases, dict(clsdict))
		cls.__fields__ = fields
		return cls

class Structure(metaclass=StructMeta):
	pass
```

#TODO  Add timings

| Structure type             | Time |
| -------------------------- | ---- |
| Simple                     |      |
| Old Metaclass (signatures) |      |
| New Metaclass (exec)       |      |

- Display results on graph

## Setters
- Could we combine the checks in the `__set__` method of the descriptors instead of chaining calls with `super()`?

- Create a new metaclass `DescriptorMeta`
- Add a static method, `set_code`, to `Descriptor`
	- Returns a list of lines of code in the current setter

```python
class Descriptor(metaclass=DescriptorMeta):
	...

	@staticmethod
	def set_code():
		return [
			'instance.__dict__[self.name] = value',
		]

class Typed(Descriptor):
	typ = object

	@staticmethod
	def set_code():
		return [
			'if not isinstance(value, self.typ):',
			'    raise TypeError(f"Expected an item of type {self.typ}, got \"{value}\"")',
		]

class Positive(Descriptor):
	@staticmethod
	def set_code():
		return [
			'if value < 0:',
			'    raise ValueError(f"Expected a value >= 0, got \"{value}\"")',
		]
```

- Similar reformulation for the other top-level descriptors

```python
def _make_setter(descriptor_cls):
	code = 'def __set__(self, instance, value):\n'
	for cls in descriptor_cls.__mro__:
		if 'set_code' in cls.__dict__:
			for line in cls.set_code():
				code += '    ' + line + '\n'
	return code
```

```python
>>> print(_make_setter(Descriptor))
...
>>> print(_make_setter(PositiveInteger))
...
```

```python
class DescriptorMeta(type):
	def __init__(self, clsname, bases, clsdict):
		if '__set__' in clsdict:
			raise TypeError('Descriptors must not implement `__set__`')
		code = _make_setter(self)
		exec(code, globals(), clsdict)
		self.__set__ = clsdict['__set__']
```

- User code doesn't need to change - this code generation is an implementation detail of descriptors

#TODO Populate test results

| Test                                           | Simple | Meta | Exec |
| ---------------------------------------------- | ------ | ---- | ---- |
| Instance creation `p = Person('Fred', 21, [])` |        |      |      |
| Attribute lookup `p.age`                       |        |      |      |
| Attribute assignment `p.age = 22`              |        |      |      |
| Attribute assignment `p.name = 'Gertrude'`     |        |      |      |

- Display results on graph

- Advice is often given to avoid using `exec` as it can be dangerous
- Given the limeted scope (and the fact that `dataclass` uses it for similar purposes) we are probably okay to use it here

- Can we make this a bit more abstract?
- This will lead into future opportunities

# XML
- The goal
```xml
<structures>
	<structure name="Person">
		<field type="SizedRegexString" maxlen="8" pat="[A-Za-z]+$">name</field>
		<field type="PositiveInteger">age</field>
		<field type="List">friends</field>
	</structure>

	<structure name="Point">
		<field type="Float">x</field>
		<field type="Float">y</field>
	</structure>

	<structure name="Address">
		<field type="String">hostname</field>
		<field type="PositiveInteger">port</field>
	</structure>
</structures>
```

- XML parsing
	- Need to implement
		- `_xml_to_code`
			- parse the xml file to an `ElementTree`
			- start `code` with necessary imports
			- for each `<structure>` node, call `_xml_struct_code` and append that to `code`
			- `return code`
		- `_xml_struct_code`
			- get the name of the structure
			- start `code` with the beginnings of a class with the given name which extends `Structure`
			- for each field in the structure
				- get the name from the element text
				- get the type of the field
				- get the keyword arguments, format them like `$key=$val` and join with commas
				- append a new line to `code` which adds a new field `$name = $type($kwargs)`
				- `return code`
- We can then use this as follows
```python
>>> code = _xml_to_code('data.xml')
>>> print(code)
...
```

- This introduces some boilerplate from needing to manually load the xml file as code
- Wouldn't it be great if we could just 'import' the xml file?

# Import hooks
- `sys.meta_path`

- A little experiment:
```python
class MyImporter:
	def find_module(self, fullname, path=None):
		print('*** Looking for', fullname)
		return None
```

```python
>>> sys.meta_path.append(MyImporter())
>>> import foo
*** Looking for foo
...
```

## Structure Importer
#TODO  Update this code to modernise it and properly handle the whole of `fullname`
```python
import imp

class StructImporter:
	def __init__(self, path):
		self._path = path

	def find_module(self, fullname, path=None):
		name = fullname.rpartition('.')[-1]
		if path is None:
			path = self._path
		for dn in path:
			filename = os.path.join(dn, name + '.xml')
			if os.path.exists(filename):
				return StructXMLLoader(filename)
		return None

class StructXMLLoader:
	def __init__(self, filename):
		self._filename = filename

	def load_module(self, fullname):
		mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
		mod.__file__ = self._filename
		mod.__loader__ = self
		code = _xml_to_code(self._filename)
		exec(code, mod.__dict__, mod.__dict__)
		return mod
```

- Add `StructImporter()` to `sys.meta_path`
	- The `path` argument is a list of locations in which to search for modules
	- `sys.path` is a suitable default for `path`
- `*.xml` files will now import
- We may want to use a different file extension (e.g. `*.struct`) to differentiate between different XML-like files.

- We can use `inspect.getsource` to view the source code of the module


# Summary
- Look at all we just did
- Descriptors
- Hiding details like signatures
- Dynamic code generation
- Customising import

- These are all useful parts of library development

- But is the hacked together?
	- Python 3 is designed to do these things
		- More advanced metaclasses (e.g., using `__prepare__`)
		- Signatures
		- Import hooks
- No hacks were required to work around language limitations

There's even more features we haven't used:
- Function annotations
```python
def add(x: int, y: int) -> int:
	return x + y
```

- Non-local variables
```python
def outer():
	x = 0

	def inner():
		nonlocal x
		x = newvalue
```

- Context managers
```python
with context_manager():
	...
```

- Parsing/AST-manipulation

## Should you
- Metaprogramming isn't for normal coding
- Frameworks and libraries are not normal coding
- If you've used a framework like Django, you've probably be using these features without knowing it
- Keeping things simple is still a good idea
	- As a library author, our focus is first simplicity for the developer using the library