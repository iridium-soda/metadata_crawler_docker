"""
Manage proxies string and handle proxy requests
"""
import os
import sys
import requests
from global_logger import logger
import json
import time

PROXY_LIFESPAN = 5  # to indicate the proxy is expired after 5 requests

"""
Lifespan: 5 normal requests or 1 429 response"""


class Proxy_pool(object):
    """
    A class for saving proxy address. Serving A proxy for each process
    """

    def __init__(self):
        self.api_url = os.getenv("API_URL", "")
        if self.api_url == "":
            logger.critical("API_URL is not set")
            sys.exit(1)
        logger.info(f"Fetching Proxy by URL {self.api_url}")
        self.proxy = ""
        self.life_span_count = PROXY_LIFESPAN
        self.get()  # Fetch a proxy from the API and update self.proxy

    def get(self):
        """
        To get a proxy from the API
        """
        try:
            resp = requests.get(self.api_url)
            if resp.status_code == 200:
                self.proxy = resp.text.strip()
                self.life_span_count = PROXY_LIFESPAN  # Reset the life_span_counts
                logger.info(
                    f"Got proxy {self.proxy} with lifespan {self.life_span_count}"
                )
            elif resp.status_code == 111:
                logger.warning("Too many requests to fetch proxy. Wait and retry.")
                time.sleep(5)
                self.get()
            else:
                logger.warning(
                    f"Failed to get proxy from {self.api_url}: unknown code {resp.status_code} with meg {resp.text}"
                )
                self.get()
        except Exception as e:
            logger.exception(e)

    def update(self):
        """
        Report the proxy is expired and fetch a new one
        """
        logger.info(f"Proxy {self.proxy} is expired. Fetching a new one")
        self.get()
