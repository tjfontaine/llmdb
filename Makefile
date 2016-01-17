VENV ?= venv

all: install

clean:
	rm -rf venv

venv:
	virtualenv $(VENV)

install: venv
	$(VENV)/bin/python setup.py install

test:
	$(MAKE) -C tests
