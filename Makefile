SHELL := /bin/bash
VIRTUALENV_ROOT := $(shell [ -z $$VIRTUAL_ENV ] && echo $$(pwd)/venv || echo $$VIRTUAL_ENV)

run_all: requirements frontend_build run_app

run_app: show_environment virtualenv
	python application.py runserver

virtualenv:
	[ -z $$VIRTUAL_ENV ] && [ ! -d venv ] && virtualenv venv || true

requirements: virtualenv requirements.txt
	${VIRTUALENV_ROOT}/bin/pip install -r requirements.txt

requirements_for_test: virtualenv requirements_for_test.txt
	${VIRTUALENV_ROOT}/bin/pip install -r requirements_for_test.txt

requirements_freeze:
	${VIRTUALENV_ROOT}/bin/pip install --upgrade pip
	${VIRTUALENV_ROOT}/bin/pip install --upgrade -r requirements_for_test.txt
	${VIRTUALENV_ROOT}/bin/pip freeze | grep -v admin-frontend > requirements.txt
	sed '/^-e /s/$$/==whatever/' -i requirements.txt
	sed '/^-e /s/-e //' -i requirements.txt

frontend_build:
	npm run --silent frontend-build:production

test: show_environment test_pep8 test_python

test_pep8: virtualenv
	${VIRTUALENV_ROOT}/bin/pep8 .

test_python: virtualenv
	${VIRTUALENV_ROOT}/bin/py.test ${PYTEST_ARGS}

show_environment:
	@echo "Environment variables in use:"
	@env | grep DM_ || true

docker:
	docker build -t dto-admin-frontend .
docker-run:
	docker run -it --rm -p 8000:8000 -t dto-admin-frontend

.PHONY: run_all run_app virtualenv requirements requirements_for_test frontend_build test test_pep8 test_python show_environment
