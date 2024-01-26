# Automatically build the image and run an instance for testing.

sudo docker build -t proxy .
sudo docker run -d -p 10756:10756 \
-e PROXY_URL="http://api.proxy.ip2world.com/getProxyIp?num=1&lb=4&return_type=txt&protocol=http" \
-e PORT=10756 \
-e NUM_WORKERS=1 \
proxy:latest 
