#!/usr/bin/env python

import cmd, shlex

from llmdb.commands import available
from llmdb.pipeline import Step, Pipeline

import llmdb.builtins

import lldb

builtins = [
  'EOF',
]

class LLMDB(cmd.Cmd):
  def setDebugger(self, debugger, target, process):
    self.debugger = debugger
    self.target = target
    self.process = process

  def do_EOF(self, line):
    """use ^D to exit"""
    return True

  def precmd(self, line):
    raw_args = shlex.split(line)

    arguments = []
    cur = []

    for a in raw_args:
      if a == '|':
        arguments.append(cur)
        cur = []
        continue
      cur.append(a)

    if len(cur) > 0:
      arguments.append(cur)

    steps = []
    stepsCount = len(arguments)
    inputArgs = None

    for (index, args) in enumerate(arguments):
      if '::' in args[0]:
        (inargs, commandName) = args[0].split('::')
      else:
        inargs = []
        commandName = args[0]

      if commandName not in available:
        if commandName in builtins:
          return line
        else:
          print 'unknown command %s' % (commandName)

      piped_into = False
      piped_outof = False

      if index == 0:
        inputArgs = [inargs]

      if index > 0:
        piped_into = True

      if piped_outof < stepsCount:
        piped_outof = True

      f = Step(available[commandName], args[1:], piped_into, piped_outof)
      f.setDebugger(self.debugger, self.target, self.process)
      steps.append(f)

    if inputArgs is None:
      inputArgs = []

    if len(steps) == 0:
      return line

    pipeline = Pipeline(steps)

    for results in pipeline(inputArgs):
      print results

    return 'default'

  def default(self, line):
    pass

if __name__ == '__main__':
  repl = LLMDB()
  repl.prompt = '> '

  debugger = lldb.SBDebugger.Create()
  debugger.SetAsync(False)
  target = debugger.CreateTargetWithFileAndArch(sys.argv[1], lldb.LLDB_ARCH_DEFAULT)
  process = target.LoadCore(sys.argv[2])

  repl.setDebugger(debugger, target, process)

  try:
    repl.cmdloop()
  finally:
    debugger.Terminate()

  print
