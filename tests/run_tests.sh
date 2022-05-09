#!/bin/bash


MARKERS1="helpers or logging or api_pytest or client or reporting or validations or batch_generation"

pipenv run pytest -n 5 --dist=loadfile --cov apiautomationtools/ --cov-report term-missing tests/ -m "${MARKERS1}"