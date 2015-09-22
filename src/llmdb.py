#!/usr/bin/env python

import os
import cmd, shlex
import pipes
import re

from subprocess import Popen, PIPE

from llmdb.commands import available, parseNum, evalExpression, isExpression, fqlist
from llmdb.pipeline import Step, Pipeline

import llmdb.builtins

import lldb

class LLMDB(cmd.Cmd):
  def setDebugger(self, debugger, target, process):
    self.debugger = debugger
    self.target = target
    self.process = process

  def do_EOF(self, line):
    """use ^D to exit"""
    return True

  def precmd(self, line):
    if line == 'EOF':
      return line

    raw_args = shlex.split(line)

    arguments = []
    cur = []
    shell_arguments = None

    for arg in raw_args:
      ## shlex.split doesn't handle unspaced pipes, but will preserve spaces in
      ## args, so assume that foo!bar|bash -c "grep foo|sed|awk"
      ## TODO XXX bash -c "noarg|noarg2" wouldn't be handled either.
      if re.search('\s', arg) is not None:
        dargs = [arg]
      else:
        dargs = re.split('([|!])', arg)

      for a in dargs:
        if not a:
          continue
        if shell_arguments is None and a == '|':
          arguments.append(cur)
          cur = []
        elif shell_arguments is None and a == '!':
          if len(cur) > 0:
            arguments.append(cur)
          shell_arguments = []
          cur = []
        else:
          cur.append(a)

    if len(cur) > 0:
      if shell_arguments is not None:
        shell_arguments.extend(cur)
      else:
        arguments.append(cur)

    steps = []
    stepsCount = len(arguments)
    inputArgs = None

    for (index, args) in enumerate(arguments):
      if '::' in args[0]:
        (inargs, commandName) = args[0].split('::')
      else:
        inargs = None
        commandName = args[0]

      if index == 0 and not inargs and isExpression(commandName):
        for value in evalExpression(self.debugger,
                                    self.process,
                                    self.target,
                                    commandName):
          print value
        break
      elif index == 0:
        if not inargs:
          inputArgs = []
        else:
          inputArgs = evalExpression(self.debugger,
                                     self.process,
                                     self.target,
                                     inargs)

      func = available.get(commandName)

      if not func and '`' in commandName:
        (moduleName, commandName) = commandName.split('`')
        module = fqlist.get(moduleName, {})
        func = module.get(commandName)

      if not func:
        print 'unknown command %s' % (commandName)
        break

      piped_into = False
      piped_outof = False

      if index > 0:
        piped_into = True

      if piped_outof < stepsCount:
        piped_outof = True

      f = Step(available[commandName], args[1:], piped_into, piped_outof)
      f.setDebugger(self.debugger, self.target, self.process)
      steps.append(f)

    ## probably evalExpression should return dot
    ## or an addr decorator should resolve dot
    if inputArgs is None or (isinstance(inputArgs, list) and len(inputArgs) == 0):
      inputArgs = [None]

    if len(steps) == 0:
      return line

    pipeline = Pipeline(steps)

    ## TODO XXX only page on ttys
    ## TODO XXX respect $PAGER
    if shell_arguments is None:
      shell_arguments = ['less', '-F', '-R', '-S', '-X', '-K']
      use_shell = False
    else:
      use_shell = True
      sargs = []
      for s in shell_arguments:
        if s is not '|':
          sargs.append(pipes.quote(s))
        else:
          sargs.append(s)
      shell_arguments = ' '.join(sargs)

    pager = Popen(shell_arguments,
                  shell=use_shell,
                  stdin=PIPE,
                  stdout=sys.stdout,
                  stderr=sys.stderr)

    for results in pipeline(inputArgs):
      if isinstance(results, (int, long)):
        msg ='0x%x' % results
      else:
        msg = results

      try:
        ret = pager.stdin.write(msg + os.linesep)
      except IOError, e:
        pager.kill()

      if pager.returncode is not None:
        break

    ## pager is still alive and expecting input
    ## we should close stdin to let it know nothing
    ## more is coming.
    if pager.returncode is None:
      pager.stdin.close()

    ## Wait for the graceful exit
    while pager.returncode is not None:
      pager.poll()

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
