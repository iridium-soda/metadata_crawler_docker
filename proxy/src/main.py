"""
An isolated module for all about proxy
"""

import json
import os
import socket
from flask_server import app
from global_logger import logger
from proxy_pool import Proxy_pool


def start_server(host: str, port: int):
    # 创建一个TCP套接字
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 绑定主机和端口
    server_socket.bind((host, port))

    # 开始监听
    server_socket.listen(1)
    logger.info(f"Server listening on {host}:{port}")

    while True:
        # 接受连接
        client_socket, client_address = server_socket.accept()
        logger.info(f"Accepted connection from {client_address[0]}:{client_address[1]}")

        # 接收数据
        rawstr = client_socket.recv(1024).decode("utf-8")
        logger.debug(rawstr)
        # logger.info(f"Received data: {data}")
        data = json.loads(rawstr)
        # data should be {type:"get_proxy",thread_index:<thread_index>}

        # 构造响应
        response = json.dumps(process_req(data=data))

        # 发送响应
        client_socket.send(response.encode("utf-8"))

        # 关闭连接
        client_socket.close()


def process_req(data: dict) -> dict:
    """
    To process requests from the proxy pool
    """
    res = {}
    try:
        if data["type"] == "get_proxy":
            res["proxy"] = proxy_pool.get_proxy(data["thread_index"])
            logger.info(f"Get {res['proxy']} for thread {data['thread_index']}")
            return res
        elif data["type"] == "report":
            # the crawler reports a 429 event and ask for the update
            logger.info(
                f"Thread {data['thread_index']} reports a 429 event. Update the proxy"
            )
            proxy_pool.update_proxy(data["thread_index"])
            return {"status": "OK"}
        else:
            logger.warning(f"Resp with wrong or NOT IMPLEMENTED: {data}")
            return {"proxy": None}
    except Exception as e:
        logger.exception(e)


if __name__ == "__main__":
    global proxy_pool
    # Init logger

    logger.info(f"Logger initialized!")

    # Read config from ENV and start the server

    server_port = str(os.getenv("PORT", "10756"))
    host = "127.0.0.1"
    logger.info(f"Server will start at {host}:{server_port}")
    # Start the Flask server
    app.run(host="0.0.0.0", port=server_port, debug=False)
    logger.info(f"Flask server started at the port {server_port}!")
