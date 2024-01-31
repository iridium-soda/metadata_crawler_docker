"""
Here saves worker functions for crawling metadata of images

NOTE: Only crawl the latest 100 tags
"""
from global_logger import logger
import utils
from dao import *
import json
import sys

db = None


def do_crawling(image_list_path: str, prefix: str):
    """
    Main function to crawl metadatas with multi-threads.
    """
    global db

    db = database(prefix)
    logger.info("Start crawling")
    try:
        with open(image_list_path, "r") as fd:
            images = fd.readlines()
    except FileNotFoundError:
        logger.exception("Images list not found ")
        sys.exit(1)
    except PermissionError:
        logger.exception("Permission denied to read ", image_list_path)
        sys.exit(1)
    except Exception as e:
        logger.exception("An exception occurs:", e)
        sys.exit(1)

    num_images = len(images)

    logger.info(f"Get input info:Prefix={prefix}, num_images={num_images}")

    for index, raw_image in enumerate(images):
        worker(raw_image, index, num_images)

    """
    ==deprecated multi-process pool==
    # 使用线程池并发处理
    with CustomThreadPoolExecutor(max_workers=int(num_workers)) as executor:
        futures = [
            executor.submit(worker, raw_image, index, num_images)
            for index, raw_image in enumerate(images)
        ]
        # Here raw_image is the original string like 779425102/python27_36_centos7_bad_flask_spider,
        # 2022-04-20T16:30:56.296814Z, 2022-05-04T15:57:33.318458Z

        # 等待所有线程完成
        for future in concurrent.futures.as_completed(futures):
            _, _ = future.result()  # 这里index是传进去的index，即当前镜像是文件中第几个
            # NOTE: 不要碰这个函数的输入输出，除非已经充分理解了这里的逻辑
    """

    logger.info(f"{prefix} Crawling finished")

    db.export_and_del()  # Cleanup


def worker(raw_image: str, index: int, num_images: int) -> list:
    """
    Main worker functions to crawl metadata of a SINGLE image by raw_image string
    input:779425102/python27_36_centos7_bad_flask_spider, 2022-04-20T16:30:56.296814Z, 2022-05-04T15:57:33.318458Z
    """
    global content
    global db
    logger.info(f"[{index + 1}/{num_images}] {raw_image}")
    result = dict()
    image_name_full, created, updated = raw_image.split(",")
    image_name_full, created, updated = (
        image_name_full.strip(),
        created.strip(),
        updated.strip(),
    )

    # to get the current thread position to allocate proxy
    if "/" not in image_name_full and not image_name_full.startswith(
        "/"
    ):  # namespace/author
        logger.warning(
            f"[{index + 1}/{num_images}] {image_name_full} has no namespace,skip."
        )
        logger.info(f"[{index + 1}/{num_images}] {image_name_full} processed")
        return [0, -1]

    namespace, image = image_name_full.split("/")
    if namespace is None:
        # Official images
        namespace = "library"

    # Check if existed
    if db.if_exist(namespace, image):
        logger.info(
            f"[{index + 1}/{num_images}] Image {namespace}/{image} already existed. Pass."
        )
        return [index, raw_image]
    result["namespace"], result["image_name"], result["created"], _ = (
        namespace,
        image,
        created,
        updated,
    )
    result["has_tags_over_100"] = False  # Set default flag for the image

    # getting update date in the overview
    logger.info(f"[{index + 1}/{num_images}] {namespace}/{image} record created")
    logger.debug(f"[{index + 1}/{num_images}] {namespace}/{image}: {result}")

    # Start doing crawling by image name

    # Get overview
    retry, max_retries = 0, 5

    while retry < max_retries:
        try:
            content = utils.get_url_with_proxy(
                f"https://hub.docker.com/v2/repositories/{namespace}/{image}/"
            )
            logger.debug(
                f"[{index + 1}/{num_images}] {namespace}/{image}'s content is {content}"
            )
            if content is None:
                logger.info(
                    f"[{index + 1}/{num_images}] {namespace}/{image} has been deleted"
                )
                result["status"] = "deleted"
                db.insert_unexisted(
                    result,
                    index + 1,
                    num_images,
                )
                logger.info(f"[{index + 1}/{num_images}] {image_name_full} processed")

                return [index, raw_image]

            result["description"] = content["description"]
            try:  # NOTE: Occasionally, when an image has a very brief description, it may not have a
                # 'full_description' field.
                result["full_description"] = content[
                    "full_description"
                ]  # 这里不保证full_description存在
            except:
                result["full_description"] = result["description"]
            result["updated"] = content["last_updated"]
            result["pull_count"] = content["pull_count"]

            break
        except:
            if retry == max_retries:
                logger.exception(
                    f"[{index + 1}/{num_images}] {image_name_full} get wrong resp while getting description; stop retrying {retry}"
                )

                break
            logger.warning(
                f"[{index + 1}/{num_images}] {image_name_full} get wrong resp while getting description; retrying {retry}: URL is https://hub.docker.com/v2/repositories/{namespace}/{image}/"
            )
            logger.debug(content)
            retry += 1

    # get tags
    result["tags"] = fetch_tags(namespace, image, index, num_images)
    if result["tags"] == []:
        # The image has no avaliable tag
        logger.warning(f"[{index + 1}/{num_images}] {image_name_full} has no tag")
        result["status"] = "empty"
        db.insert_unexisted(
            result,
            index + 1,
            num_images,
        )
        logger.info(f"[{index + 1}/{num_images}] {image_name_full} processed")
        return [index, raw_image]
    elif len(result["tags"]) > 100:
        result["has_tags_over_100"] = True
        result["tags"] = result["tags"][:100]  # Turncate tags
        logger.info(
            f"[{index + 1}/{num_images}] {image_name_full} has tags more than 100, turncate."
        )
    # get update date, layer size, build history, etc. for each digest
    # by https://hub.docker.com/v2/repositories/library/ubuntu/tags/18.04/images
    result["images"] = {}  # group by tag
    for tag in result["tags"]:
        result["images"][tag] = fetch_images_by_tag(
            namespace, image, tag, index + 1, num_images
        )

    # write results to database
    logger.debug(f"[{index + 1}/{num_images}]Result is {json.dumps(result)}")

    db.insert_single(result, index + 1, num_images)

    logger.info(f"[{index + 1}/{num_images}] {image_name_full} processed")

    return [index, raw_image]


def fetch_tags(namespace, image, index, num_images):
    """
    To fetch tags of the given image
    Return a TUPLE includes (the list of tags(only the latest 100))
    """
    page = 1
    tags = list()

    flip_flag = True  # to determine if it's still needs to flip pages
    url = f"https://hub.docker.com/v2/namespaces/{namespace}/repositories/{image}/tags?page={page}"
    while flip_flag:
        try:
            content = utils.get_url_with_proxy(url)
            for result in content["results"]:
                tags.append(result["name"])
            if len(tags) >= 100:
                logger.info(
                    f"[{index + 1}/{num_images}] {namespace}/{image} has tags more than 100, turncate."
                )
                flip_flag = False
                tags = tags[:100]  # Truncate
                break
            if content["next"]:  # the next page exists
                url = content["next"]
            else:
                flip_flag = False
        except:
            logger.warning(
                f"[{index + 1}/{num_images}] {namespace}/{image} get wrong resp while getting tags; URL is "
                f"https://hub.docker.com/v2/namespaces/{namespace}/repositories/{image}/tags?page={page}"
            )
            flip_flag = False  # Break the loop

    logger.info(f"[{index + 1}/{num_images}] {namespace}/{image} has {len(tags)} tags")
    return tags


def fetch_images_by_tag(namespace, image, tag, index, image_nums):
    """
    To obtain information on each layer of an image with a specified tag
    by https://hub.docker.com/v2/repositories/library/ubuntu/tags/18.04/images
    """
    url = (
        f"https://hub.docker.com/v2/repositories/{namespace}/{image}/tags/{tag}/images"
    )
    max_retries, retry = 5, 0
    while retry < max_retries:
        try:
            content = utils.get_url_with_proxy(url)
            result = list()
            for image_obj in content:
                # For each image with this tag
                logger.debug(
                    f"[{index}/{image_nums}]{namespace}/{image}:{tag} has content {image_obj}"
                )

                tmp = {}
                tmp["overall_size"] = image_obj["size"]
                tmp["last_pushed"] = image_obj["last_pulled"]
                tmp["last_pulled"] = image_obj["last_pulled"]
                tmp["architecture"] = image_obj["architecture"]
                tmp["variant"] = image_obj["variant"]
                if "digest" not in image_obj:
                    logger.info(
                        f"[{index}/{image_nums}] {namespace}/{image}:{tag} is empty"
                    )
                    tmp["digest"] = None
                else:
                    tmp["digest"] = image_obj["digest"]
                if "os" not in image_obj:
                    logger.info(
                        f"[{index}/{image_nums}] {namespace}/{image}:{tag} has no os"
                    )
                    tmp["os"] = None
                else:
                    tmp["os"] = image_obj["os"]
                if "layers" not in image_obj:
                    tmp["layers"] = []
                    logger.warning(
                        f"[{index}/{image_nums}] {namespace}/{image}:{tag}:{tmp['digest']} has no avaliable layers"
                    )
                else:
                    tmp["layers"] = image_obj["layers"]
                result.append(tmp)
            break
        except:
            if retry == max_retries:
                logger.exception(
                    f"[{index}/{image_nums}] {namespace}/{image}:{tag} get wrong resp while getting building history; retrying {retry}"
                )
                break
            logger.warning(
                f"[{index}/{image_nums}] {namespace}/{image}:{tag} get wrong resp while getting building history; retrying {retry}; URL is https://hub.docker.com/v2/repositories/{namespace}/{image}/tags/{tag}/images"
            )
            retry += 1
    return result
