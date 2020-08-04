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
	$(ENVS) $(PYTHON) server_fa1.py &
	$(ENVS) $(PYTHON) server_fa2.py &

client_test1:
	$(info $(ENVS))
	$(ENVS) $(PYTHON) client.py testing

client_test2:
	$(info $(ENVS))
	$(ENVS) $(PYTHON) client.py test

client_test3:
	$(info $(ENVS))
	$(ENVS) $(PYTHON) client.py test_error

test:
	$(info $(ENVS))
	$(info ${TESTS}${TEST_SUBFOLDER})
	$(ENVS) $(PYTEST) -v -l --disable-warnings ${TESTS}${TEST_SUBFOLDER}

deps:
	$(info $(ENVS))
	$(PIP) install -r requirements
