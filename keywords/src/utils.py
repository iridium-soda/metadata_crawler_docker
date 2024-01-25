"""
To serve the request to the FlareSolverr
"""
import requests
from keywords.src.global_logger import logger
import json
URLtemplate = "https://hub.docker.com/search?type=image&q="


def send_request(url, query):
    """
    Send request to the FlareSolverr
    :param url: url of the FlareSolverr
    :param query: the query word will be searched in DockerHub
    :return: response
    """

    url = "http://localhost:8191/v1"
    headers = {"Content-Type": "application/json"}

    data = {"cmd": "request.get", "url": URLtemplate + query, "maxTimeout": 60000}

    # 发送POST请求
    response = requests.post(url, json=data, headers=headers)

    # 解析响应内容
    print("Response:", response.text)
    resp=json.loads(response.text)
    try:
        status_code=resp['headers']['status']
        logger.info(f"Got {status_code} for URL {URLtemplate + query}")
        
