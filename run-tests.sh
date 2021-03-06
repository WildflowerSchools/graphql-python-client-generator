#!/usr/bin/env bash

BASE_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PACKAGE_NAME="gqlpycgen"

with_rednose='--rednose --force-color'
with_coverage="--cover-html-dir=${BASE_DIR}/htmlcov --with-coverage --cover-html --cover-package=${PACKAGE_NAME} --cover-erase --cover-branches"
with_doctest='--with-doctest'

test -z $1 || dotests="--tests=${1}"

exec nosetests ${with_rednose} -s -v ${with_doctest} ${with_coverage} --where ${BASE_DIR}/tests ${dotests}

# py.test --cov-report term-missing --cov-report html --cov=$PACKAGE_NAME tests
