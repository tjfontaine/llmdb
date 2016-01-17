CC ?= clang
CFLAGS := -g -Wall -Werror

OBJS := $(patsubst %.c, %.test, $(wildcard *.c))

all: run

%.test: %.c
	$(CC) $(CFLAGS) $^ -o $@

clean:
	rm -rf *.test *.dSYM

run: $(OBJS)
	./test-runner.sh
