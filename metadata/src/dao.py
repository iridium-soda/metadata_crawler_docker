"""
Here implements operations about mongodb backends
"""
import pymongo
from global_logger import logger
import os
import json


mongo_host = os.getenv("MONGO_HOST", "localhost")
mongo_port = int(os.getenv("MONGO_PORT", 27017))


class database(object):
    def __init__(self, prefix):
        logger.info(f"Connecting to mongodb by {mongo_host}:{mongo_port}")

        # Connect to db
        self.client = pymongo.MongoClient(mongo_host, mongo_port)

        # Check if database exist and create
        db_name = os.getenv("DB_NAME", "metadata")

        self.db = self.client[db_name]
        self.collection_path = "_".join(["metadatas", prefix])

        logger.info(f"MongoDB intialized:{db_name}/{self.collection_path}")

        self.collection = self.db[self.collection_path]

        self.insert_unexisted(
            {"namespace": "#####", "image_name": "$$$$$", "status": "dummy"}, -1, -1
        )  # Insert a single empty record to create the collection

        self.MAX_TAG_COUNT_PER_RECORD = 100  # How many tags for a single record

    def insert_unexisted(self, result: dict, index: int, image_nums: int) -> int:
        """
        To handle unexcepted empty(404) or empty tags
        """
        logger.info(
            f"[{index}/{image_nums}] Ready to insert {result['status']} image: {result['namespace']}/{result['image_name']}"
        )
        try:
            if result["status"] == "deleted":
                # The image has been deleted
                logger.debug(
                    f"[{index}/{image_nums}] The record of {result['namespace']}/{result['image_name']} has been deleted"
                )
                # The result should has 3 fields:
                # namespace;image_name;status
            elif result["status"] == "empty":
                # The image has no tag
                logger.debug(
                    f"[{index}/{image_nums}] The record of {result['namespace']}/{result['image_name']} has no tag"
                )
                # The result should has 3 fields:
                # namespace;image_name;status
            else:
                # Unexpected status
                logger.debug(
                    f"[{index}/{image_nums}] The record of {result['namespace']}/{result['image_name']} has other status {result['status']}"
                )

        except Exception as e:
            logger.exception("Incorrect paras:", e)
        try:
            resp = self.collection.insert_one(result)
        except Exception as e:
            logger.exception("Database IO exception: ", e)
        return resp.inserted_id

    def insert_single(self, result: dict, index: int, image_nums: int) -> int:
        """
        Insert single image without sharding
        """
        logger.info(
            f"[{index}/{image_nums}] The record of {result['namespace']}/{result['image_name']} are ready to insert"
        )
        try:
            resp = self.collection.insert_one(result)
        except Exception as e:
            logger.exception("Database IO exception: ", e)
        return resp.inserted_id

    def if_exist(self, namespace: str, image_name: str) -> bool:
        result = self.collection.find_one(
            {"namespace": namespace, "image_name": image_name}
        )
        if (
            result
        ):  # NOTE: I have no idea why not return the value directly... DONT change it anyway
            return True
        else:
            return False

    def export_and_del(self):
        """
        Export data of single image list to mounted /result with json format and then delete it
        """
        export_path = "/result/" + self.collection_path + ".json"
        cursor = self.collection.find({})
        documents = list(cursor)
        # 导出为JSON文件
        with open(export_path, "w") as file:
            json.dump(documents, file, default=str)  # 默认使用str序列化日期字段等非基本数据类型
        logger.info(
            f"Collection {self.collection_path} has been exported to {export_path}"
        )
        # 删除
        self.collection.drop()
        del self.collection  # delete the collection to prevent reuse
        logger.info(f"Collection {self.collection_path} has been deleted")
        # Disconnect
        self.client.close()
