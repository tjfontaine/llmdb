## Overview

llmdb is "mdb for lldb", in other words a modular shell pipeline approach to
debugging.

## Example

```shell
./llmdb ./test /cores/core.22702 
> ::walk thread | ::stack
Thread #1
frame #0: 0x00007fff8e3310ae libsystem_kernel.dylib`__pthread_kill + 10
frame #1: 0x00007fff8cce6500 libsystem_pthread.dylib`pthread_kill + 90
frame #2: 0x00007fff96b0737b libsystem_c.dylib`abort + 129
frame #3: 0x000000010a1ccf40 test`foobar(argv=0x00007fff55a33698) + 48 at t.c:6
frame #4: 0x000000010a1ccf58 test`main(argc=1, argv=0x00007fff55a33698) + 24 at t.c:10
frame #5: 0x00007fff9ba0e5ad libdyld.dylib`start + 1
frame #6: 0x00007fff9ba0e5ad libdyld.dylib`start + 1
> 
```

## Notes

True to how mdb works, llmdb interprets numbers as hex unless otherwise given an
explicit input format. The expression `1000,10` is equivalent to `0x1000,0x10`

Number formatting:

 * `['0i', '0I', '0b', '0B']` are interpreted as binary
 * `['0o', '0O']` are interpreted as octal
 * `['0t', '0T']` are interpreted as decimal
 * `['0x', '0X']` are interpreted as hexidecimal

## Works

 * defining commands and walkers
 * loading modules
 * paged output
 * repeat expressions
 * pipelined commands
 * bang operator (redirect output to shell pipeline)
  - `::nm ! grep foobar | less`

## Commands

  - `::dump` -- display arbitrary regions of mapped memory
   * missing ascii representation
   * still needs to align and dedupe memory it reads
  - `::walkers` -- list walkers
  - `::walk` -- execute given walker
  - `::which` -- describe which module a command comes from
  - `::stack` -- for a given thread id (0 based index) print backtrace
  - `::nm` -- list all symbols for the target
   * missing options to limit and search output
  - `::print` -- print the address contents
   * this is currently just a wrapper around lldb's `print` so passing type
     information is required
  - `::lldb` -- execute arbitrary lldb command
   * if you're missing functionality from llmdb but know how to do it in lldb

## Walkers

 * `::walk thread`

## TODO

 * semi-colon parsing
 * dot expressions
 * format expressions (i.e. `0xffffff/nap`)
 * as many commands as we can
 * getopt style decorator for command option parsing
 * non-tty interaction
 * aliases for `$` and `:` commands
 * unload module

## Known Issues

 * prompt not always immediately restored on output that doesn't fill paged
   window
