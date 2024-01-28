import sys
import time
import requests
import os
from global_logger import logger

prefix = str(os.getenv("PREFIX", "-1"))
if prefix == "-1":
    logger.critical("Please set PREFIX env variable!")
    sys.exit(1)

# Path to save the result
result_path = f"/result/all_images_{prefix}.list"


def get_images_url(keyword, url):
    if url == "":
        return ""

    # payload={}
    headers = {
        "Connection": "keep-alive",
        "sec-ch-ua": '" Not;A Brand";v="99", "Google Chrome";v="97", "Chromium";v="97"',
        "sec-ch-ua-mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
        "Content-Type": "application/json",
        "Search-Version": "v3",
        "Accept": "application/json",
        "X-DOCKER-API-CLIENT": "docker-hub/1280.0.0",
        "sec-ch-ua-platform": '"macOS"',
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://hub.docker.com/search?q={}&type=image".format(keyword),
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }

    # response = requests.request("GET", url, headers=headers, data=payload)

    try:
        content = requests.get(url, headers=headers)
        while content.status_code == 429:  # 429 means too many requests to get response
            logger.warning("Wait for 429!")
            time.sleep(60)
            content = requests.get(url, headers=headers)

        if content.status_code == 200:
            return content
        else:
            logger.warning(f"Unexcepted status code {content.status_code}")
            return ""
    except Exception as e:
        logger.warning(f"Unexcepted 429:{e}")
        return ""


def search_images_with_keyword(keyword) -> dict:
    # Get metadata of images for single keywords
    url = "https://hub.docker.com/api/content/v1/products/search?page_size=100&q={}&type=image".format(
        keyword
    )
    images = dict()
    while url != "":
        content = get_images_url(keyword, url)
        if content == "":
            break
        content = content.json()
        url = content["next"]
        for image in content["summaries"]:
            try:
                image_name = str(image["name"])
                created = str(image["created_at"])
                updated = str(image["updated_at"])
                if image_name not in images:
                    images[image_name] = image_name + "," + created + "," + updated
                    logger.info(f"Add image:{image_name} for keyword {keyword}")
                    logger.debug(f"Raw data:{images[image_name]}")

            except Exception as e:
                logger.warning(f"Raw data:{image} has an exception:{e}")
                continue

    return images


def main():
    global prefix
    keywords = {}
    filepath = f"/data/keyWordList-{prefix}.txt"
    if not os.path.exists(filepath):
        logger.critical(f"File {filepath} not exists!")
        sys.exit(0)
    with open(filepath, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line not in keywords:
                keywords[line] = 1

    index = 0
    total = str(len(keywords))

    logger.info(f"Prefix is {prefix}")
    for keyword in keywords:
        index += 1
        logger.info(f"[{str(index)}/{total}] Start crawling {keyword}")
        imgs = search_images_with_keyword(keyword)
        save_data(imgs)
        logger.info(f"[SUCCESS] {keyword} Saved Finished!")
    logger.info(f"[SUCCESS] {prefix} Finished!")


# Collect all data in /result/all_images.list
def save_data(images: dict):
    with open(result_path, "a+") as f:
        for img in images:
            logger.debug(f"Save {images[img]}")
            f.write(f"{images[img]}\n")


def delete_file_if_exists(file_path):
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            logger.info(f"The old result file '{file_path}' deleted successfully.")
        except Exception as e:
            logger.warning(f"Error deleting the old result file '{file_path}': {e}")
    else:
        logger.file(f"The old result file '{file_path}' does not exist.")


if __name__ == "__main__":
    # Cleanup the old result file
    delete_file_if_exists(result_path)
    main()
