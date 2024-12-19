#!/bin/bash

# Build the docker image
docker build -t predig .

# Push the image to docker hub as :version
docker tag predig predig:latest

# Push the image to docker hub as :version
docker push predig:latest
