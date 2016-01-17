#!/bin/bash

ulimit -c unlimited

for f in $(ls *.test); do
  ./$f 2> /dev/null > /dev/null &
  PID=$!
  wait $PID
  mv -f /cores/core.$PID $f.core
done
