from flask import Flask, request, jsonify
from proxy_pool import proxy_pool
from global_logger import logger

app = Flask(__name__)


@app.route("/", methods=["POST"])
def handle_post_request():
    """
    To handle the POST request from the crawler
    """
    data = request.get_json()
    # data should be {type:"get_proxy",thread_index:<thread_index>}
    res = {}
    try:
        if data["type"] == "get_proxy":
            proxystr = proxy_pool.get_proxy(data["thread_index"])
            logger.info(f"Get {proxystr} for thread {data['thread_index']}")
            res["proxy"] = proxystr

        elif data["type"] == "report":
            # the crawler reports a 429 event and ask for the update
            logger.info(
                f"Thread {data['thread_index']} reports a 429 event. Update the proxy"
            )
            proxy_pool.update_proxy(data["thread_index"])
            res["status"] = "OK"
        else:
            logger.warning(f"Unknown request type: {data['type']}")
            res["status"] = "Unknown request type"
    except Exception as e:
        logger.exception(e)

    # 构造响应
    response = jsonify(res)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST"
    response.headers["Access-Control-Allow-Headers"] = "x-requested-with,content-type"
    return response
