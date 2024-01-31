"""
Getting image name, created date, update date, layers' history, layer size, short description, full description for each digest. Maybe docekrfile?
"""

import sys
import os

from global_logger import logger
from crawler import do_crawling

usage = """
Usage:
Getting image name, created date, update date, layers' history, layer size, short description, full description for each digest in .csv
metadata_crawler.py <path_to_images_list>
e.g. metadata_crawler.py results/all_images_a.list
"""


def main():
    prefix = str(os.getenv("PREFIX", -1))
    if prefix == -1:
        logger.exception("Please set PREFIX in env")
        sys.exit(1)

    logger.info(f"Get input info:{prefix}")
    filepath = f"/data/all_images_{prefix}.list"
    do_crawling(filepath, prefix)
    # NOTE:index is only for padding. It has been deprecated.
    logger.info(f"[SUCCESS] program for {prefix} exited")


if __name__ == "__main__":
    main()
