import imp

import lldb

from llmdb.commands import register, available

@register
def help(context, addr, *args):
  """print help
  
  ::help [module]
  """
  name = None

  if len(args) > 0:
    name = args[0]

  if name is None:
    for key, value in available.iteritems():
      doc = value.__doc__
      firstLine = '<undocumented>'
      if doc is not None and len(doc):
        firstLine = doc.split('\n')[0]
      yield '\t%s: %s' % (key, firstLine)
  elif name in available:
    yield available[name].__doc__
  else:
    yield 'Command %s not registered' % (name)

@register(name='lldb')
def lldbcmd(context, addr, *args):
  cmd = ' '.join(args)
  ci = context.debugger.GetCommandInterpreter()
  res = lldb.SBCommandReturnObject()
  ci.HandleCommand(cmd, res)
  if res.Succeeded():
    yield res.GetOutput()
  else:
    yield res.GetError()

@register(name='print')
def do_print(context, addr, *args):
  if isinstance(addr, str):
    addr = int(addr, 16)

  ci = context.debugger.GetCommandInterpreter()
  res = lldb.SBCommandReturnObject()

  cmd = 'print ('

  if len(args) > 0:
    cmd += '(%s)' % (args[0])

  cmd += '0x%x)' % (addr)

  if len(args) > 1:
    cmd += args[1]

  ci.HandleCommand(cmd, res)

  yield res.GetOutput()

@register
def load(context, addr, fname):
  """load commands from file

  ::load <filename>
  """
  imp.load_source('cmd', fname)

@register
def nm(context, addr, *args):
  for module in context.target.modules:
    for symbol in module.symbols:
      yield '0x%08x\t0x%08x\t%s.%s' % (symbol.addr,
                                      int(symbol.end_addr) - int(symbol.addr),
                                      symbol.addr.section.name,
                                      symbol.name)

@register
def which(context, addr, name, *args):
  command = available.get(name)

  if command:
    yield '%s is a command from module %s' % (name, command.__fname__)

  walker  = walkers.get(name)

  if walker:
    yield '%s is a walker from module %s' % (name, command.__fname__)

@register
def mappings(context, *args):
  """Print a list of each mapping in the target's virtual address space

  TODO lldb doesn't currently expose anything useful in terms of figuring out
  the virtual address space mappings, or the modes of the sections we're
  looking at
  """

  first = False
  for module in context.target.module_iter():
    for section in module.section_iter():
      if not first:
        first = True
        yield '{:<16} {:<16} {:<16} {}'.format('Start', 'End', 'Size', 'File')
      yield '{:<16} {:<16} {:<16} {}'.format('{:#x}'.format(int(section.addr)),
                                             '{:#x}'.format(int(section.addr) + section.size),
                                             '{:#x}'.format(section.size),
                                             module.platform_file,
                                             section.type)
