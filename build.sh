#!/bin/bash
URL=
IMAGE=
docker build . -t $URL/$IMAGE:latest
docker push $URL/$IMAGE:latest
