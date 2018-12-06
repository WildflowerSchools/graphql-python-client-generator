import os
from setuptools import setup, find_packages

BASEDIR = os.path.dirname(os.path.abspath(__file__))
VERSION = open(os.path.join(BASEDIR, 'VERSION')).read().strip()
REQUIREMENTS = []
DEPENDENCY_LINKS = []


with open(os.path.join(BASEDIR, 'requirements.pip')) as fp:
    lines = fp.readlines()
    for line in lines:
        line = line.strip()
        if ("http://" in line or "https://" in line or "ssh://" in line) and "#egg=" in line:
            parts = line.split("#egg=")
            REQUIREMENTS.append(parts[-1])
            DEPENDENCY_LINKS.append(line)
        elif len(line) and line[0] != "#" and line[0] != "-":
            REQUIREMENTS.append(line)

# allow setup.py to be run from any path
os.chdir(os.path.normpath(BASEDIR))


setup(
    name='gqlpycgen',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    description='GraphQL Python CLient Generator',
    long_description='Reads a GQL schema and turns it into a python library.',
    url='https://github.com/Wildflowerschools/graphql-python-client-generator',
    author='optimuspaul',
    author_email='paul.decoursey@wildflowerschools.org',
    install_requires=REQUIREMENTS,
    dependency_links=DEPENDENCY_LINKS,
    entry_points={
        'console_scripts': [
            'gqlpycgen=gqlpycgencli:cli',
        ],
    }
)
