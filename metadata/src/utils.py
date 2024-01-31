"""
This is for doing crawling
"""
import time
import requests
from global_logger import logger
from proxy import Proxy_pool

host = "127.0.0.1"

proxy_pool = Proxy_pool()


def get_url_with_proxy(url: str):
    """
    Get resp of the given URL WITH proxy
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36"
    }
    try:
        # Get a proxy from local proxy server
        proxy_IP = request_proxy()

        pdict = {"http": "http://" + proxy_IP}  # NOTE: HTTP only
        logger.debug(f"[Connection] Requesting {url} with proxy {proxy_IP}")
        # Send request
        content = requests.get(url, headers=headers, proxies=pdict)

        # If got 200?
        if content.status_code == 200:
            return content.json()
        elif content.status_code == 404:
            logger.warning(f"[Connection] {url} got 404")
            return None
        else:
            logger.warning(
                f"[Connection] Wait for {content.status_code}, retrying for proxy {proxy_IP}"
            )
            # Send to the proxy pool with a 429 event
            proxy_pool.update()
            time.sleep(2)
            return get_url_with_proxy(url)

    except Exception as e:
        logger.exception("[Connection] Unexcepted 429", e)
        return get_url_with_proxy(url)


def request_proxy() -> str:
    """
    Send a request to local proxy server to get an avaliable proxy
    Return raw ip:port string
    """
    proxy = proxy_pool.proxy
    proxy_pool.life_span_count -= 1
    if proxy_pool.life_span_count <= 0:
        # The proxy has been expired
        logger.warning(f"[Connection] Proxy {proxy} has expired; ready to re-fetch")
        proxy_pool.update()
        proxy = proxy_pool.proxy
    return proxy
