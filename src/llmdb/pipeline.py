import funcy

class Step(object):
  def __init__(self, func, args, piped_into=False, piped_outof=False):
    self.args = args
    self.func = func
    self.state = {}
    self.piped_into = piped_into
    self.piped_outof = piped_outof
    self.debugger = None
    self.target = None
    self.process = None

  def setDebugger(self, debugger, target, process):
    self.debugger = debugger
    self.target = target
    self.process = process

  def __call__(self, nextf):
    def generator():
      inputGeneration = None

      ## If nextf is a function, it's the next step and we must call to
      ## get its generator.
      if hasattr(nextf, '__call__'):
        l = nextf()
      else:
      ## If we're not callable then, then its likely the input list and
      ## we can iterate directly
        l = nextf

      for addr in l:
        try:
          ret = self.func(self, addr, *self.args)

          if ret is not None:
            for intermediate in ret:
              yield intermediate
        except Exception,e:
          print 'Failed to execute command: %s' % (self.func.__name__)
          print e

    generator.__name__ = '%s_generator' % (self.func.__name__)

    return generator
  

class Pipeline(object):
  def __init__(self, steps):
    self.steps = steps

  def __call__(self, addrs):
    pipeline = funcy.rcompose(*self.steps)
    return pipeline(addrs)()

if __name__ == '__main__':
  def stepA(context, addr):
    print 'stepA: %s' % (addr)
    for i in range(1, 10):
      yield i

  def stepB(context, addr):
    print 'stepB: %s' % (addr)
    yield 'stepB yield'

  def stepC(context, addr):
    print 'stepC: %s' % (addr)
    yield 'stepC yield'

  a = Step(stepA, [])
  b = Step(stepB, [])
  c = Step(stepC, [])

  pipeline = Pipeline([a, b, c])

  ret = pipeline(['DEADBEEF'])
  for r in ret:
    print 'step final yield: %s' % r
