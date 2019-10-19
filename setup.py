import os
from setuptools import setup, find_packages

BASEDIR = os.path.dirname(os.path.abspath(__file__))
VERSION = open(os.path.join(BASEDIR, 'VERSION')).read().strip()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(BASEDIR))


setup(
    name='wf-gqlpycgen',
    version=VERSION,
    packages=find_packages(),
    include_package_data=True,
    description='GraphQL Python CLient Generator',
    long_description='Reads a GQL schema and turns it into a python library.',
    url='https://github.com/Wildflowerschools/graphql-python-client-generator',
    author='optimuspaul',
    author_email='paul.decoursey@wildflowerschools.org',
    install_requires=[
        'Jinja2==2.10',
        'click>=6.7',
        'requests==2.21.0'
    ],
    tests_require = [
        'coverage',
        'mock',
        'nose',
        'rednose'
    ]
    entry_points={
        'console_scripts': [
            'gqlpycgen=gqlpycgencli:cli',
        ],
    }
)
