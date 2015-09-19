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
