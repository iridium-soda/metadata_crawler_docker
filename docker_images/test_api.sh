curl -X GET \
  -H "Connection: keep-alive" \
  -H "sec-ch-ua: \" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"97\", \"Chromium\";v=\"97\"" \
  -H "sec-ch-ua-mobile: ?0" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36" \
  -H "Content-Type: application/json" \
  -H "Search-Version: v3" \
  -H "Accept: application/json" \
  -H "X-DOCKER-API-CLIENT: docker-hub/1280.0.0" \
  -H "sec-ch-ua-platform: \"macOS\"" \
  -H "Sec-Fetch-Site: same-origin" \
  -H "Sec-Fetch-Mode: cors" \
  -H "Sec-Fetch-Dest: empty" \
  -H "Referer: https://hub.docker.com/search?q=1a&type=image" \
  -H "Accept-Language: zh-CN,zh;q=0.9,en;q=0.8" \
    https://hub.docker.com/api/content/v1/products/search?page_size=100&q=1a&type=image
