# My message in a bottle
[![Build Status](https://app.travis-ci.com/Team6ASE2021/MMIAB-PRIMER.svg?token=5PqFNKuWwdmknapJspK9&branch=main)](https://app.travis-ci.com/Team6ASE2021/MMIAB-PRIMER)

[![codecov](https://codecov.io/gh/Team6ASE2021/MMIAB-PRIMER/branch/main/graph/badge.svg?token=ZW8B5JQWYL)](https://codecov.io/gh/Team6ASE2021/MMIAB-PRIMER)


# Running the application
## Running on local
Install all the dependencies 
```bash
$ pip install -r requirements.txt
```
To test the application in your local machine you can execute the **run\.sh** script, or alternatively the **run_all.sh** script to test the celery workers as well.

## Running with docker-compose

Install docker and docker-compose, and then run
```bash
$ docker-compose up
```



# Testing
Install necessary tools
```bash
$ pip install -r requirements.txt 
$ pip install -r requirements-dev.txt
```
and then run 
```bash
$ pytest
```
or run tests using tox
```bash
$ tox
```
# Contributing

## Code style
We use pre-commit hooks to autoformat commits and remove unused imports and variables.


Using them is left optional for  simplicity, if you want to, install pre-commit with 
```bash
$ pip install pre-commit

```
and then run
```bash
$ pre-commit install
```
From the next commit they will run automatically.

You can also run them on specific files, orall files with:
```bash
$  pre-commit run --all-files
```
