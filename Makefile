.PHONY: all build clean
PACKAGE:=TDX
SRCS_DIR:=src/ph$(PACKAGE)
SRCS:=$(shell find $(SRCS_DIR) -type f)
TAG_FILES:=$(addprefix $(SRCS_DIR)/, $(PACKAGE).json tdx_connector.py)
HASH_FILES:=$(addprefix $(SRCS_DIR)/, tdx_connector.py)
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

version: .tag .commit
.tag: $(TAG_FILES)
	echo version $(TAG)
	sed -i s/GITHUB_TAG/$(TAG)/ $^
	touch $@
.commit: $(HASH_FILES)
	echo commit $(GITHUB_SHA)
	sed -i s/GITHUB_SHA/$(GITHUB_SHA)/ $^
	touch $@

deploy: $(PACKAGE).tgz
	python deploy.py

venv: requirements-test.txt
	rm -rf $@
	python -m venv $@
	$(VENV_PYTHON) -m pip install -r requirements-test.txt

requirements-test.txt: export SOAR_CONNECTOR_FORK=git+ssh://git@github.com/splunk/pytest-splunk-soar-connectors.git@424aa098ce7bda5c16bf2c90555ef1f504b88b1f
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
