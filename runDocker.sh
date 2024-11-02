#!/bin/bash

docker build -t customerapi .
docker run -dp 5000:5000 -v ./app:/app customerapi