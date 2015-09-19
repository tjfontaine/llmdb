from llmdb.commands import register

import lldb

@register()
def dump(context, addr, *args):
  bytesize = context.target.GetAddressByteSize()

  msg = ''

  if 'FIRST' not in context.state:
    context.state['FIRST'] = True
    for i in range(bytesize * 2):
      msg += ' '
    msg += '    0 1 2 3  4 5 6 7 \/ 9 a b  c d e f  01234567v9abcdef\n'

  if instanceof(addr, str):
    addr = int(addr, 16)

  fmt = '%%0%dx' % (bytesize * 2)
  msg += (fmt % (addr)) + ':  '

  error = lldb.SBError()

  fmt = '%%0%dx' % (bytesize)
  hexes = []
  for i in range(0, 16, 4):
    mem = context.process.ReadUnsignedFromMemory(addr + i, 4, error)

    if not error.Success():
      raise Exception('unable to read from memory: %s' % (error))

    hexes.append(fmt % (mem))

  msg += ' '.join(hexes)
  yield msg
