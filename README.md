# Directory tree

<a href="https://github.com/andamound/endpoints-coding-challenge/actions/workflows/test.yml">
    <img src="https://github.com/andamound/endpoints-coding-challenge/actions/workflows/test.yml/badge.svg" alt="Test"/>
</a>

<a href="https://codecov.io/gh/andamound/endpoints-coding-challenge">
    <img src="https://codecov.io/gh/andamound/endpoints-coding-challenge/branch/main/graph/badge.svg?token=CUCPT5N04G" alt="Coverage"/>
</a>


Application for simple directories management.

The key features are:
- Create, delete and move directories
- Print directory list
- Working with console input and files
- Reusable "Explorer" class
- Simple run
- 100% test coverage
- 100% type annotated codebase

## Requirements
Python 3.5+

## Example

For run with console input:

    python directories.py

For run with txt file:

    python directories.py example.txt

# Testing

For run tests:

    python -m pip install -U -r requirements.txt
    pytest --cov=directories --cov-report term-missing
