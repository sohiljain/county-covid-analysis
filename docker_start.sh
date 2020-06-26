#!/bin/bash

# Copyright (c) 2020 Databot Services Inc. All rights reserved.
# @author Sohil Jain

CONTAINER="covid_api"
echo "Starting Container $CONTAINER"

docker rm -vf $CONTAINER
docker build --rm=False -t $CONTAINER .
docker run  -t -v ${PWD}/submission/:/submission/ -p 5002:5002 --name $CONTAINER $CONTAINER "$@"

