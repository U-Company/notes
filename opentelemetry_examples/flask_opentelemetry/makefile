PYTHONPATH=.
CMD_PATH=./
SCRIPTS_PATH=scripts/
TESTS=tests/
LOG_PATH=.log/

ifndef PYTHON
	PYTHON=python
endif
ifndef PYTEST
	PYTEST=pytest
endif
ifndef PIP
	PIP=pip
endif
ifndef TEST_SUBFOLDER
	TEST_SUBFOLDER=./
endif
ifndef VAULT_ENV
	VAULT_ENV=LOCAL
endif


ENVS=PYTHONPATH=${PYTHONPATH} VAULT_ENV=${VAULT_ENV}

run:
	$(info $(ENVS))
	$(ENVS) $(PYTHON) app.py

test:
	$(info $(ENVS))
	$(info ${TESTS}${TEST_SUBFOLDER})
	$(ENVS) $(PYTEST) -v -l --disable-warnings ${TESTS}${TEST_SUBFOLDER}

deps:
	$(info $(ENVS))
	$(PIP) install -r requirements
