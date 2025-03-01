# DO NOT EDIT - All project-specific values belong in config.mk!

.PHONY: all build clean lint static wheels
include config.mk

MODULE:=app
TEST_APP_NAME:=Test $(PROD_APP_NAME)

PACKAGE:=app
SRCS_DIR:=src/$(MODULE)
TSCS_DIR:=tests
SOAR_SRCS:=$(shell find $(SRCS_DIR) -type f)
SRCS:=$(shell find $(SRCS_DIR) -name '*.py')
TSCS:=$(shell find $(TSCS_DIR) -name '*.py')
VERSIONED_FILES:=$(addprefix $(SRCS_DIR)/, $(PACKAGE).json *.py)
BUILD_TIME:=$(shell date -u +%FT%X.%6NZ)
VENV_PYTHON:=venv/bin/python
VENV_REQS:=.requirements.venv
UNAME:=$(shell uname -s)
WHEELS:=$(SRCS_DIR)/wheels

# BSD `sed` treats the `-i` option differently than Linux and others.
# Check for Mac OS X 'Darwin' and set our `-i` option accordingly.
ifeq ($(UNAME), Darwin) 
# macOS (BSD sed) 
	SED_INPLACE := -i '' 
else 
# Linux and others (GNU sed) 
	SED_INPLACE := -i 
endif 

ifeq (tag, $(GITHUB_REF_TYPE))
	TAG?=$(GITHUB_REF_NAME)
else
	TAG?=$(shell printf "0.0.%d" 0x$(shell git rev-parse --short=6 HEAD))
endif
GITHUB_SHA?=$(shell git rev-parse HEAD)

all: build

build: export APP_ID=$(PROD_APP_ID)
build: export APP_NAME=$(PROD_APP_NAME)
build: $(PACKAGE).tar

build-test: export APP_ID=$(TEST_APP_ID)
build-test: export APP_NAME=$(TEST_APP_NAME)
build-test: $(PACKAGE).tar

$(PACKAGE).tar: version $(SOAR_SRCS) wheels
	-find src -type d -name __pycache__ -exec rm -fr "{}" \;
	tar cvf $@ -C src $(MODULE)

version: .tag .commit .deployed $(SRCS_DIR)/$(PACKAGE).json
.tag: $(VERSIONED_FILES)
	echo version $(TAG)
	sed $(SED_INPLACE) "s/GITHUB_TAG/$(TAG)/" $^
	touch $@
.commit: $(VERSIONED_FILES)
	echo commit $(GITHUB_SHA)
	sed $(SED_INPLACE) "s/GITHUB_SHA/$(GITHUB_SHA)/" $^
	touch $@
.deployed: $(VERSIONED_FILES)
	echo deployed $(BUILD_TIME)
	sed $(SED_INPLACE) "s/BUILD_TIME/$(BUILD_TIME)/" $^
	touch $@
$(SRCS_DIR)/$(PACKAGE).json: $(WHEELS)
	echo appid: $(APP_ID)
	echo name:  $(APP_NAME)
	echo wheel: $(shell ls $(WHEELS))
	sed $(SED_INPLACE) "s/APP_ID/$(APP_ID)/" $@
	sed $(SED_INPLACE) "s/APP_NAME/$(APP_NAME)/" $@
	sed $(SED_INPLACE) "s/MODULE/$(MODULE)/" $@
	@echo "WHEELS: $(WHEELS)"
	sed $(SED_INPLACE) "s/WHEEL_TDX/$(shell ls $(WHEELS) | grep -E 'TDX.*\.whl')/" $@
	sed $(SED_INPLACE) "s/WHEEL_TOOLBOX/$(shell ls ./$(WHEELS) | grep -E 'phantom_toolbox.*\.whl')/" $@

deploy: $(PACKAGE).tar venv
	$(VENV_PYTHON) -m phtoolbox deploy --file $<

venv: requirements-test.txt requirements.in
	rm -rf $@
	python -m venv venv
	$(VENV_PYTHON) -m pip install -r requirements-test.txt
	$(VENV_PYTHON) -m pip install -r requirements.in

wheels: $(WHEELS)
$(WHEELS): requirements.in
	pip wheel --no-deps --wheel-dir=$@ -r $^

requirements-test.txt: export PYTEST_SOAR_REPO=git+https://github.com/splunk/pytest-splunk-soar-connectors.git
requirements-test.txt: export VCR_CLEANER_REPO=git+https://github.com/techservicesillinois/vcrpy-cleaner.git
requirements-test.txt: requirements.in requirements-test.in
	rm -rf $(VENV_REQS)
	python -m venv $(VENV_REQS)
	$(VENV_REQS)/bin/python -m pip install --upgrade pip
	$(VENV_REQS)/bin/python -m pip install -r requirements.in
	$(VENV_REQS)/bin/python -m pip install -r requirements-test.in
	$(VENV_REQS)/bin/python -m pip freeze -qqq > $@
	# REMOVE once pytest-splunk-soar-connectors is on pypi
	sed $(SED_INPLACE) "s;^pytest-splunk-soar-connectors==.*;$(PYTEST_SOAR_REPO);" $@
	sed $(SED_INPLACE) "s;^vcr-cleaner==.*;$(VCR_CLEANER_REPO);" $@

lint: venv .lint
.lint: $(SRCS) $(TSCS)
	$(VENV_PYTHON) -m flake8 $?
	touch $@

static: venv .static
.static: $(SRCS) $(TSCS)
	echo "Code: $(SRCS)"
	echo "Test: $(TSCS)"
	$(VENV_PYTHON) -m mypy $^
	touch $@

autopep8:
	autopep8 --in-place $(SRCS)

test: venv lint static
	$(VENV_PYTHON) -m pytest
	
clean:
	rm -rf venv $(VENV_REQS)
	rm -rf .lint .static
	rm -rf .mypy_cache
	rm -f $(PACKAGE).tar .tag .wheel .commit .deployed
	-find src -type d -name __pycache__ -exec rm -fr "{}" \;
	git checkout -- $(TAG_FILES)

force-clean: clean
	rm -f requirements-test.txt
