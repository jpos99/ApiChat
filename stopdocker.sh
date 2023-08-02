#!/bin/sh

PID=$(sudo docker inspect --format '{{.State.Pid}}' fastapi)

sudo kill -9 $PID
sudo docker container prune || exit
