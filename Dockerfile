# Copyright (c) 2020 Databot Inc. All rights reserved.
# @author Sohil Jain

FROM python:3.7-stretch
WORKDIR /submission
COPY submission/* /submission/
RUN apt-get update
RUN pip install pipenv
RUN pipenv install --skip-lock
ENV PYTHONPATH ${PYTONPATH}:/submission
RUN chmod -R 755 /submission/
EXPOSE 5002

ENTRYPOINT /submission/run.sh
