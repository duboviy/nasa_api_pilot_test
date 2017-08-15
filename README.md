# nasa_api_pilot_test
Pilot test framework for testing NASA's open API (https://api.nasa.gov/index.html#getting-started). The purpose of the test is to check images which are made by Curiosity.


## Command to install dependencies/prerequisites

```bash
pip install -r requirements.txt
```


## How to run tests

```
python -m unittest -v main
```

or simply:

```bash
python main.py
```


## CI

[![Build Status](https://travis-ci.org/duboviy/nasa_api_pilot_test.svg?branch=master)](https://travis-ci.org/duboviy/nasa_api_pilot_test)

Expected that TravisCI build should be failed. That's because 3 / 7 test cases are failing due to real issues.


## Supported python versions

  * 3.6
  * 2.7
