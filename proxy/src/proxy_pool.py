"""
Proxy_pool class. To handle the proxy pool.
- Fetch proxy string from the remote
- Update the proxy if reported invaild
- Provide proxy string to the client
"""

from global_logger import logger
import os
import requests
import json
import time

PROXY_MAX_LIFESPAN = 5


class Proxy_pool(object):
    """
    A class for saving proxy address. Serving A proxy for each process
    """

    def __init__(self, size: int):
        """
        Size is the size of the proxy pool. Equal to the number of processes
        """

        # Read ENV and get Proxy API
        self.proxy_url = os.getenv("PROXY_URL", "")
        if self.proxy_url == "":
            logger.error("PROXY_URL is not set in ENV")
            raise Exception("PROXY_URL is not set in ENV")

        # NOTE: self.proxy_url should only fetch ONE proxy
        logger.info(f"Fetching Proxy by URL {self.proxy_url}")
        """
        NOTE: URL should be like the following:
        http://api.proxy.ip2world.com/getProxyIp?num=1&lb=1&return_type=txt&protocol=http
        WARNING: this praser is only for IP2World API link. Check and change as you link before running
        """
        tces = self.proxy_url.split("?")  # Split the URL by '?'
        segs = tces[-1].split(
            "&"
        )  # To initialize proxy pool by fetch proxies in a batch

        for index, seg in enumerate(segs):
            if seg.startswith("num"):
                tmps = seg.split("=")
                assert len(tmps) == 2  # `seg` should be like num=1
                tmps[-1] = str(size)
                segs[index] = "=".join(tmps)
                break
        init_proxy_url = "?".join([tces[0], "&".join(segs)])  # Recombine the URL
        logger.info(f"Parse init fetching URL:{init_proxy_url}")

        # Start fetching initialize proxies
        self.proxy = []
        # self.proxy is like [["[proxy]",[life_span_count]]]; Each proxy corresponds to the thread number of the index to which the agent belongs (CPU Worker number)

        # fetch initial proxies
        proxies = self.fetch_proxies(init_proxy_url, 0)
        for proxy in proxies:
            self.proxy.append([proxy, PROXY_MAX_LIFESPAN])
        logger.info(f"Initialized proxies:{self.proxy}")

        # Initialize the IP address set to exclude duplicated IP address
        self.ipset = []
        for p in self.proxy:
            self.ipset.append(p[0].split(":")[0])  # To get the IP address part

    def fetch_proxies(self, url: str, thread_index: int) -> [str]:
        """
        To fetch single proxy or multi proxies
        Return a list of the proxy(proxies)
        thread_index is the index of the request process; 0 for initialize
        """
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # 读取响应内容
                data = response.text
                try:  # NOTE: 这里需要根据代理池的API文档响应格式修改
                    datadict = json.loads(response.text)
                    if datadict["code"] == 111:
                        logger.warning(
                            f"[Worker {thread_index}] Too many requests to fetch proxy. Wait."
                        )
                        time.sleep(5)
                        return self.fetch_proxies(url, thread_index)
                except:
                    pass
                result = data.strip().split("\n")  # NOTE: Must be split by \n
                logger.info(f"[Worker {thread_index}] Fetching new ip proxy: {result}")
                return result
            else:
                logger.warning(
                    f"[Worker {thread_index}] Fetching new ip proxy failed:{response.status_code}. Retry"
                )
                time.sleep(5)
                return self.fetch_proxies(url, thread_index)  # Retry
        except requests.exceptions.RequestException as e:
            logger.exception(e)

    def get_proxy(self, thread_index: int) -> str:
        """
        To response the request from the given process and return its proxy
        """
        self.proxy[thread_index - 1][1] -= 1  # NOTE: ignore requesting failed situation
        proxy = self.proxy[thread_index - 1][0]  # NOTE: thread_index starts with 1
        # NOTE: lifespan has been deprecated
        """
        if lifespan <= 0:
            # the life of the proxy has been expired
            logger.warning(
                f"[Worker:{thread_index}] Proxy {proxy} has expired; ready to re-fetch"
            )
            self.update_proxy(thread_index=thread_index)
        """
        return proxy

    def update_proxy(self, thread_index: int):
        """
        Update the expired proxy
        """
        proxy_new = self.fetch_proxies(self.proxy_url, thread_index)[0]
        # Verify if the new proxy shares the same expired proxy address in the pool
        # Fetch multi proxies in ONE request
        proxies = self.fetch_proxies(self.proxy_url, thread_index)
        for p in proxies:
            if p.split(":") in self.ipset:
                logger.info(
                    f"[Worker:{thread_index}] Proxy {p} has the expired IP address."
                )
            else:
                self.proxy[thread_index - 1] = [
                    p,
                    PROXY_MAX_LIFESPAN,
                ]  # Renew the proxy
                logger.info(
                    f"[Worker:{thread_index}] Proxy has been updated:{self.proxy[thread_index-1][0]}"
                )
                # Reset ipset
                self.ipset = []
                for p in self.proxy:
                    self.ipset.append(p[0].split(":")[0])  # To get the IP address part
                return

        # No vaild proxy; refetch it
        logger.warning(f"All proxies fetched are not brand new; refetch it.")
        self.update_proxy(thread_index)


num_workers = os.getenv("NUM_WORKERS", "10")  # 10 as default
# Initialize proxy pool
proxy_pool = Proxy_pool(num_workers)
