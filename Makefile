.PHONY: setup-venv setup-tests setup-docs build package docs test unit-test modinput-test run help

APP_NAME := $$(cat globalConfig.json | jq -r '.meta.name')

PYTHON_PATH := $(shell which python3.9 || pyenv which python3.9 2>/dev/null || which python3)
VENV_COMMAND := $(PYTHON_PATH) -m venv

VENV := .venv
UCC_GEN := $(VENV)/bin/ucc-gen

OUTPUT_PATH := output
OUTPUT_BUILD_PATH := $(OUTPUT_PATH)/$(APP_NAME)

SPLUNK_HOST ?= localhost
SPLUNK_HEC_TOKEN ?= 00000000-0000-0000-0000-000000000000
SPLUNK_USER ?= admin
SPLUNK_PASSWORD ?= Chang3d!

MODINPUT_TEST_PREPARE ?= true
RUN_PREPARE ?= true

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

help:
	@cat $(MAKEFILE_LIST) | python3 -c "$$PRINT_HELP_PYSCRIPT"

# ── Environment Setup ──────────────────────────

setup-venv: ## Create Python virtual environment
	$(VENV_COMMAND) $(VENV)
	. $(VENV)/bin/activate && pip install --upgrade splunk-add-on-ucc-framework

setup-tests: ## Setup tests virtual environment
	$(VENV_COMMAND) $(VENV)
	. $(VENV)/bin/activate && pip install -r tests/test-requirements.txt

setup-docs: ## Setup docs virtual environment
	$(VENV_COMMAND) $(VENV)
	. $(VENV)/bin/activate && \
	pip install mkdocs==1.6.0 mkdocs-material==9.5.32 mkdocs-print-site-plugin==2.6.0

# ── Build ──────────────────────────

build: setup-venv ## Build with UCC
	$(UCC_GEN) build --ta-version=$(APP_VERSION);

package: build ## Build and package with UCC
	mkdir -p dist
	$(UCC_GEN) package --path $(OUTPUT_BUILD_PATH) -o dist

docs: setup-docs ## Build docs with mkdocs
	mkdocs serve

# ── Docker Development ─────────────────────────

run: ## Run add-on in docker container
	$(RUN_PREPARE)
	@if [ -d "docker-compose.yml" ]; then \
		( \
			export SPLUNK_APP_ID=$(APP_NAME); \
			export SPLUNK_APP_PACKAGE=$(OUTPUT_BUILD_PATH); \
			export SPLUNK_HEC_TOKEN=$(SPLUNK_HEC_TOKEN); \
			export SPLUNK_USER=$(SPLUNK_USER); \
			export SPLUNK_PASSWORD=$(SPLUNK_PASSWORD); \
			docker compose up -d; \
			echo "Waiting for Splunk to be ready..."; \
			until docker compose logs splunk 2>&1 | grep -q "Ansible playbook complete"; do sleep 1; printf "."; done; \
			echo " SPLUNK READY"; \
		)
	else \
		echo "Skipping: docker-compose.yml file not found"; \
	fi

# ── Tests ─────────────────────────

test: unit-test ## Run default test suite (unit tests)

unit-test: setup-tests ## Run unit tests
	@if [ -d "tests/unit" ]; then \
		( . $(VENV)/bin/activate; pytest -v tests/unit ); \
	else \
		echo "Skipping: tests/unit directory not found"; \
	fi

modinput-test: setup-tests ## Run modinput functional tests
	$(MODINPUT_TEST_PREPARE)
	@if [ -d "tests/modinput_functional" ]; then \
		( . $(VENV)/bin/activate; \
		pytest -vvv -n 1 \
			--splunk-type=external \
			--splunk-hec-token="$(SPLUNK_HEC_TOKEN)" \
			--splunk-user=$(SPLUNK_USER) \
			--splunk-password=$(SPLUNK_PASSWORD) \
			--password=$(SPLUNK_PASSWORD) \
			--splunk-web-scheme=https \
			--splunk-host=$(SPLUNK_HOST) \
			tests/modinput_functional ); \
	else \
		echo "Skipping: tests/modinput_functional directory not found"; \
	fi
