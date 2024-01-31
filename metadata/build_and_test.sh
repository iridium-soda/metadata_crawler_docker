#!/bin/bash


# Clean env
sudo docker stop metadata_1
sudo docker rm metadata_1
sudo docker rmi metadata:latest

# Build the image
sudo docker build -t metadata:latest .

# Run & Test

sudo docker run -d \
--name metadata_1 \
--network meta \
-e PREFIX="1" \
-e API_URL="http://api.proxy.ip2world.com/getProxyIp?num=1&lb=4&return_type=txt&protocol=http" \
-e MONGO_PORT=27017 \
-v $(pwd)/../docker_images/data:/data \
metadata:latest 

sudo docker logs -f metadata_1