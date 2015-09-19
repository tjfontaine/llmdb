import functools, inspect
from functools import wraps

available = {}
walkers = {}

class AlreadyRegistered(Exception):
  pass

COMMAND=object()
WALKER=object()

def decorator(func):
    ''' Allow to use decorator either with arguments or not. '''

    def isFuncArg(*args, **kw):
        return len(args) == 1 and len(kw) == 0 and (
            inspect.isfunction(args[0]) or isinstance(args[0], type))

    if isinstance(func, type):
        def class_wrapper(*args, **kw):
            if isFuncArg(*args, **kw):
                return func()(*args, **kw) # create class before usage
            return func(*args, **kw)
        class_wrapper.__name__ = func.__name__
        class_wrapper.__module__ = func.__module__
        return class_wrapper

    @functools.wraps(func)
    def func_wrapper(*args, **kw):
        if isFuncArg(*args, **kw):
            return func(*args, **kw)

        def functor(userFunc):
            return func(userFunc, *args, **kw)

        return functor

    return func_wrapper

@decorator
def register(func, cmdType=COMMAND, name=None):
  if not name:
    name = func.__name__

  if cmdType is COMMAND:
    dest = available
  elif cmdType is WALKER:
    dest = walkers
  else:
    raise Exception("Unknown command type")

  if name in dest:
    raise AlreadyRegistered('%s already registered' % (name))

  @wraps(func)
  def wrapper(*args, **kwargs):
    return func(*args, **kwargs)

  dest[name] = wrapper

  return wrapper
