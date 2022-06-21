.PHONY: all build clean
PACKAGE:=tdx
SRCS_DIR:=src/ph$(PACKAGE)
SRCS:=$(shell find $(SRCS_DIR) -type f)
# TODO: Add this line back
# TAG_FILES:=$(addprefix $(SRCS_DIR)/, $(PACKAGE).json __init__.py)
TAG_FILES:=$(addprefix $(SRCS_DIR)/, __init__.py)
VENV_PYTHON:=venv/bin/python
VENV_REQS:=.requirements.venv

ifeq (tag, $(GITHUB_REF_TYPE))
	TAG?=$(GITHUB_REF_NAME)
else
	TAG?=0.0.0
endif

all: build

build: $(PACKAGE).tgz

$(PACKAGE).tgz: .tag $(SRCS)
	tar zcvf $@ -C src .

version: .tag
.tag: $(TAG_FILES)
	echo version $(TAG)
	sed -i s/GITHUB_TAG/$(TAG)/ $^
	touch $@

deploy: $(PACKAGE).tgz
	python deploy.py

venv: requirements-test.txt
	rm -rf $@
	python -m venv $@
	$(VENV_PYTHON) -m pip install wheel
	$(VENV_PYTHON) -m pip install -r requirements-test.txt

requirements-test.txt: export SOAR_CONNECTOR_FORK=git+ssh://git@github.com/edthedev/pytest-splunk-soar-connectors.git@d05e170c5c3f7592d33110e148f4ccbaa6425eeb
requirements-test.txt: requirements-test.in
	rm -rf $(VENV_REQS)
	python -m venv $(VENV_REQS)
	$(VENV_REQS)/bin/python -m pip install -r $^
	$(VENV_REQS)/bin/python -m pip freeze -qqq > $@
	#REMOVE once pytest-splunk-soar-connectors is on pypi
	sed -i "s;^pytest-splunk-soar-connectors==.*;$(SOAR_CONNECTOR_FORK);" $@

test: venv
	$(VENV_PYTHON) -m pytest
	
clean:
	rm -rf venv $(VENV_REQS)
	rm -f $(PACKAGE).tgz .tag
	-find src -type d -name __pycache__ -exec rm -fr "{}" \;
	git checkout -- $(TAG_FILES)

force-clean: clean
	rm -f requirements-test.txt
