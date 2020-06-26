#!/bin/bash

cd /submission || exit
pipenv run python3 "$@"