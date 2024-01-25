import requests
import json

url = "http://localhost:8191/v1"
url_r = "https://hub.docker.com/search?q=ag"
headers = {"Content-Type": "application/json"}
data = {
    "cmd": "request.get",
    "url": "https://hub.docker.com/search?q=ag",
    "maxTimeout": 60000,
    "returnOnlyCookies": True,
}

response = requests.post(url, headers=headers, json=data)
# print(response.text)
# retrieve the entire JSON response from FlareSolverr
response_data = json.loads(response.content)

# Extract the cookies from the FlareSolverr response
cookies = response_data["solution"]["cookies"]

# Clean the cookies
cookies = {cookie["name"]: cookie["value"] for cookie in cookies}

# Extract the user agent from the FlareSolverr response
user_agent = response_data["solution"]["userAgent"]

response = requests.get(url_r, cookies=cookies, headers={"User-Agent": user_agent})
print(response.content)
