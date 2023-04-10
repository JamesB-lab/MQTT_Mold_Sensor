#!/bin/bash
aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin 714533746634.dkr.ecr.eu-west-2.amazonaws.com

docker build -t 714533746634.dkr.ecr.eu-west-2.amazonaws.com/mold-detector-mqtt-data-logger -f data-logger.Dockerfile .
docker push 714533746634.dkr.ecr.eu-west-2.amazonaws.com/mold-detector-mqtt-data-logger

docker build -t 714533746634.dkr.ecr.eu-west-2.amazonaws.com/mold-detector-mqtt-data-aggregator -f data-aggregator.Dockerfile .
docker push 714533746634.dkr.ecr.eu-west-2.amazonaws.com/mold-detector-mqtt-data-aggregator

docker build -t 714533746634.dkr.ecr.eu-west-2.amazonaws.com/mold-detector-mqtt-push-notifications -f push-notifications.Dockerfile .
docker push 714533746634.dkr.ecr.eu-west-2.amazonaws.com/mold-detector-mqtt-push-notifications

docker build -t 714533746634.dkr.ecr.eu-west-2.amazonaws.com/mold-detector-mqtt-dashboard -f dashboard.Dockerfile .
docker push 714533746634.dkr.ecr.eu-west-2.amazonaws.com/mold-detector-mqtt-dashboard
