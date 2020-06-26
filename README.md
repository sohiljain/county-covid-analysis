# Covid County Analysis

This git repository contains the code for covid analysis of USA counties. 
We have an etl script which loads data every day and an exposed api that provides details at zipcode and day level 

## Environment
- Python version used is 3.7
- Pipenv is used for python package management
- Python Packages required our specified in Pipfile

## Running Instructions -
#### Running ETL for current load
`python etl.py`

#### Running ETL for historical load
`python etl.py history`

#### Running api
`python covid_api.py `

## Test cases
#### Test Case 1 - one_to_one_mapping:
    We find an exact match to county mapping and zip belongs to only one county. Observe that esitmated cases is
    less than cases in counties because it is divided by number of zipcodes in the county to estimte zipcode level data
#### Test Case 2 - test_unsuccessfull_county_match:
    We find no match to county mapping and cannot find the populatin and therefore rate is null. Zip belongs to only one county. Observe that esitmated cases is
    less than cases in counties because it is divided by number of zipcodes in the county to estimte zipcode level data
#### Test Case 3 - no_mapping:
    When we find no mapping, estimated cases and rate values are null
#### Test Case 4 - multiple_counties_zip:
    When we find a zip lies in multiple counties, we multiply and sum over the tot_ration to get estimated counts

