#!/bin/bash


autoflake --remove-all-unused-imports --exclude=__init__.py -i -r .
black .
isort .