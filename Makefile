PY = python3

all: build

build:
	$(PY) setup.py build

install:
	$(PY) setup.py install

develop:
	$(PY) setup.py develop

clean:
	$(PY) setup.py clean
	rm -rf dist/ build/ dns_spoofer.egg-info
