#!/bin/bash

# Clean env
sudo docker stop imagename_crawler
sudo docker rm imagename_crawler
sudo docker rmi images

# Build the image
sudo docker build -t images .

# Run & Test
sudo docker run -d --name imagename_crawler -v $(pwd)/data:/result -v $(pwd)/../keywords/data:/data -e PREFIX=1 images
sudo docker logs -f imagename_crawler
