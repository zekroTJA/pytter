#### EXECUTABLES ###########################

PYTHON_WIN = py
PYTHON_UNX = python3

FLAKE8 = flake8
PDOC   = pdoc

#### OTHER VARS ############################

DOCS_LOCATION = $(CURDIR)/docs

############################################

ifeq ($(OS),Windows_NT)
	PY = $(PYTHON_WIN)
else
	PY = $(PYTHON_UNX)
endif

.PHONY: _make install deps test docs lint help

_make: deps install

install:
	$(PY) -m pip install -e .

deps:
	$(PY) -m pip install -r $(CURDIR)/requirements.txt

test:
	[ "$(CASE)" != "" ] &&\
		$(PY) -m unittest -v tests.$(CASE)
	[ "$(CASE)" != "" ] ||\
		$(PY) -m unittest -v tests/*.py

docs:
	rm -r $(DOCS_LOCATION)/* || true
	$(PDOC) \
		--html \
		--html-dir $(DOCS_LOCATION) \
		--overwrite \
		--external-links \
			pytter
	mv $(DOCS_LOCATION)/pytter/* $(DOCS_LOCATION)/
	rm -r $(DOCS_LOCATION)/pytter

lint:
	$(FLAKE8) $(CURDIR)

help:
	@echo "Avaliable make recipes:"
	@echo "  *          Ensure local dependencies and install package"
	@echo "  deps       Ensure local pip dependencies"
	@echo "  docs       Create or update code documentation"
	@echo "  install    Install package locally from source"
	@echo "  lint       Run flake8 over the project source"
	@echo "  test       Execute tests"