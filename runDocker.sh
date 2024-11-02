#!/bin/bash

docker build -t customerapi .
docker run -dp 5000:5000 ./app:/app customerapi