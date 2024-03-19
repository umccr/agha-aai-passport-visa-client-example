# systems this Makefile has been tested against
# macOS 14, M1 Mac, brew installed python and node


.PHONY: setup setup-front-end setup-python-back-end clean

# meta tasks that bring together more language specific rules

build: build-front-end

setup: setup-python-back-end setup-front-end

# specific setup that bring in the actual build rules

setup-front-end: front-end/node_modules

setup-python-back-end: .venv/lib

build-front-end: setup-front-end front-end/build/index.html

# to run our Python we need both the front-end built, and Python setup and ready to go

run-python-back-end: build-front-end setup-python-back-end
	source .venv/bin/activate; cd back-end/python; python server.py

# to run our Typescript we need both the front-end built, and NodeJs back-end setup and ready to go

# WIP
# run-typescript-back-end: build-front-end setup-typescript-back-end
#	npm i


# clean up working folders

clean: clean-python-back-end clean-front-end

clean-front-end:
	cd front-end; rm -rf node_modules/ build/

clean-python-back-end:
	rm -rf .venv/

# actual perform rules that create files/folders

front-end/build/index.html: $(wildcard front-end/src/**/*) $(wildcard front-end/*.json) $(wildcard front-end/*.ts) front-end/index.html
	cd front-end; npx tsc && npx vite build --mode development

front-end/node_modules: front-end/package.json front-end/package-lock.json
	cd front-end; npm install; touch node_modules

.venv/lib: back-end/python/requirements.txt
	python3 -m venv .venv; source .venv/bin/activate; touch .venv/lib; cd back-end/python; pip install -r requirements.txt;
