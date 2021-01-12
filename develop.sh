#!/bin/bash

export ENVIRONMENT=local

docker run -d -it --rm --name redis-dto-admin-frontend redis 

docker run --rm -it \
    --env REDIS_HOST \
    --link redis-dto-admin-frontend:redis \
    -p 5004:5004 \
    dto-admin-frontend
docker stop redis-dto-admin-frontend