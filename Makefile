# systems this Makefile has been tested against
# macOS 14, M1 Mac, brew installed python and node
# Ubuntu 20, M1 Mac, apt installed python3.11-venv, make, node, npm

EXECUTABLES = python3 pip3 npx npm 
K := $(foreach exec,$(EXECUTABLES), $(if $(shell which $(exec)),some string,$(error "No $(exec) in PATH")))

#
# by default we do everything to set up for running any of the backends
#

all: build-front-end setup-python-back-end

setup: setup-python-back-end setup-front-end

setup-front-end: front-end/node_modules

setup-python-back-end: .venv/lib

build-front-end: setup-front-end front-end/build/index.html

.PHONY: all build setup setup-front-end setup-python-back-end build-front-end

#
# the actual targets that should be targeted for running the various back-ends
#

run-python-back-end: build-front-end setup-python-back-end
	. .venv/bin/activate; cd back-end/python; python3 server.py

# WIP
# run-typescript-back-end: build-front-end setup-typescript-back-end
#	npm i

.PHONY: run-python-back-end

#
# clean up working folders
#

clean: clean-python-back-end clean-front-end

clean-front-end:
	cd front-end; rm -rf node_modules/ build/

clean-python-back-end:
	cd back-end/python; find . -type f -name '*.py[co]' -delete -o -type d -name __pycache__ -delete
	rm -rf .venv/

.PHONY: clean clean-front-end clean-python-back-end

# actual rules that create files/folders and build things

front-end/build/index.html: $(wildcard front-end/src/**/*) $(wildcard front-end/*.json) $(wildcard front-end/*.ts) front-end/index.html
	cd front-end; npx tsc && npx vite build --mode development

front-end/node_modules: front-end/package.json front-end/package-lock.json
	cd front-end; npm install; touch node_modules

.venv/lib: back-end/python/requirements.txt
	python3 -m venv .venv; . .venv/bin/activate; touch .venv/lib; cd back-end/python; pip3 install -r requirements.txt;

