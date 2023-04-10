build:
    poetry build

publish: build
    poetry publish

format:
    black gqlpycgen

lint:
    pylint gqlpycgen

version:
    poetry version