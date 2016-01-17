from llmdb.commands import register, walkers

@register(name = 'walkers')
def list_walkers(context, addr, *args):
  for name, walker in walkers.iteritems():
    firstline = '<undocumented>'
    doc = walker.__doc__
    if doc is not None and len(doc):
      firstline = doc.split('\n')[0]
    yield '\t%s - %s' % (name, firstline)

@register
def walk(context, addr, name, *args):
  if name not in walkers:
    print '%s is not a valid walker' % name

  value = walkers[name]

  for v in value(context, addr, *args):
    yield v
