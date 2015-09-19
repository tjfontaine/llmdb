from llmdb.commands import register, WALKER

@register(cmdType=WALKER)
def thread(context, addr, *args):
  for i in range(context.process.num_threads):
    yield i

@register
def stack(context, addr, *args):
  if 'FIRST' not in context.state:
    context.state['FIRST'] = True
    yield 'Thread #%d' % (addr + 1)
  thread = context.process.thread[addr]
  for frame in thread:
    yield str(frame)
