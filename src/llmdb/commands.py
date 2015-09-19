import re

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

def isNum(number):
  start = number[:2]
  rest = number[2:]
  base = None

  if start in ['0i', '0I', '0b', '0B']:
    base = 2
  elif start in ['0o', '0O']:
    base = 8
  elif start in ['0t', '0T']:
    base = 10
  elif start in ['0x', '0X']:
    base = 16

  return (base, rest)

def parseNum(number):
  (base, value) = isNum(number)
  if base:
    return int(value, base)
  else:
    ## TODO XXX resolve symbol?
    return int(number, 16)

EXPRESSION_RE = '([/\\=?])'
VALID_EXPRESSION = '(0[ibxt])*[0-9a-f]+,?' + EXPRESSION_RE + '*'

def evalExpression(debugger, process, target, expression):
  args = re.split(EXPRESSION_RE, expression, 1)

  if len(args) == 0:
    yield None

  if len(args) > 0:
    addr = args[0]
  else:
    addr = None

  if ',' in addr:
    (addr, repeat) = addr.split(',')
    repeat = parseNum(repeat)
  else:
    repeat = 1

  addr = parseNum(addr)

  if len(args) > 1:
    op = args[1]
  else:
    op = None

  if len(args) > 2:
    fmt = args[2]
  else:
    fmt = None

  ## TODO XXX shift dot by format length
  fmtlength = target.addr_size

  for i in range(0, repeat * fmtlength, fmtlength):
    v = (addr + i)
    yield v

    #if op is '/':
    #  value = target.ResolveLoadAddress(addr)
    #elif op is '\\':
    #  ## TODO XXX physical address?
    #  pass
    #elif op is '=':
    #  pass
    #elif op is '?':
    #  pass
    #else:
    #  pass

def isExpression(expression):
  ret = re.match(VALID_EXPRESSION, expression)
  return ret != None
