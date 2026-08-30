PYTHON ?= python

.PHONY: install test

install:
	$(PYTHON) -m pip install -e .[test]

test:
	pytest tests/
