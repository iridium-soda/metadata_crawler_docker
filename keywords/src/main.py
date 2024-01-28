from treelib import Tree, Node
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as Wait
from selenium.webdriver.support import expected_conditions as Expect
from selenium.webdriver.firefox.service import Service
import string
from global_logger import logger
import os


# from selenium.webdriver.common.proxy import Proxy, ProxyType
import sys

options = Options()
options.add_argument("-headless")
browser = webdriver.Firefox(options=options)

divison = -1  # Decide which Trees will be selected and built
timeout_sec = 10

wordDict = [c for c in string.ascii_lowercase + string.digits + "-_"]


keywordsFile = ""
dictTree = Tree()
root = Node(data="")
dictTree.add_node(root)
parents = []


def init_tree():
    logger.info("Initing trees")

    for firstWord in wordDict[divison]:  # For each char
        node1layer = Node(data=firstWord)
        dictTree.add_node(node1layer, parent=root)
        parents.append(node1layer)

        for secWord in wordDict:
            node2layer = Node(data=secWord)
            dictTree.add_node(node2layer, parent=node1layer)


def add_leaf_node(root):
    for word in wordDict:
        node = Node(data=word)
        dictTree.add_node(node, parent=root)


def cut_accepted_leaves(leaves):
    global parents

    flag = 1
    for node in dictTree.leaves():
        if node not in leaves or node in parents:
            dictTree.remove_node(node.identifier)
            flag = 0

    if flag == 0:
        cut_accepted_leaves(leaves)


def traversal_paths_to_leaf():
    leaves = dictTree.leaves()
    for path in dictTree.paths_to_leaves():
        keyWord = ""
        for node in path:
            keyWord = keyWord + dictTree[node].data

        leaf = dictTree[path[-1]]

        status = check_keyword_search_results(keyWord)
        if status == 1:
            dictTree.remove_node(leaf.identifier)
            cut_accepted_leaves(leaves)
            with open(keywordsFile, "a+") as keyword_list:
                keyword_list.write(keyWord + "\n")  # Adding to vaild words.
        elif status == -2:
            dictTree.remove_node(leaf.identifier)
            cut_accepted_leaves(leaves)
        # If it can't, add a new character behind this keyword
        elif status == -1:
            return
        else:
            # status==0
            add_leaf_node(leaf)
            flag = 0

    if print_trees():  # This function shows if the tree is empty
        traversal_paths_to_leaf()


def check_number(number):
    num = int(number.replace(",", ""))

    # num over 10,000 or no result
    if num >= 10000 or num == 0:
        return 0
    else:
        return 1


def check_keyword_search_results(keyWord):
    # root node is ""
    if keyWord == "":
        return -1

    logger.info(f"Check the Keywords {str(keyWord)}")

    url = "https://hub.docker.com/search?q={}&type=image".format(keyWord)
    for _ in range(5):
        try:
            browser.get(url)
            break
        except Exception as e:
            logger.warning("retry...")
            continue
    try:
        element = Wait(browser, timeout_sec).until(
            Expect.presence_of_element_located(
                (By.CLASS_NAME, "MuiTypography-root MuiTypography-h3 css-lhhh1d")
            )
        )
        if "No results" in element.text:
            logger.warning("There doesn't have search results...")
            return -2
        """
        NOTE: in fact we cannot capture 'No result' here but we must wait for some secs.
        """
    except Exception as e:
        pass  # Ignore the exception
    soup = BeautifulSoup(browser.page_source, "html.parser")
    links = soup.find_all(
        "div", class_="MuiBox-root css-r29exk"
    )  # Vaild comfirmed until 2024/01/24
    if not links:
        logger.warning("No links located. Retry")
        return check_keyword_search_results(keyWord=keyWord)
    for link in links:
        logger.info(f"Raw text is:{link.div.text}")
        if "-" in link.div.text and "of" in link.div.text:
            num = link.div.text.split()[4]
            imageNum = check_number(num)
            logger.info(
                f"{keyWord}: got {num}, means {'Go' if imageNum==0 else 'Stop'}"
            )
            return imageNum
        elif link.div.text == "images":
            # Patch: no result here
            logger.warning("No result here")
            return -2
    return 0


def print_trees():
    res = []
    for path in dictTree.paths_to_leaves():
        res.append("".join([dictTree[w].data for w in path]))
    return res


def main():
    init_tree()
    traversal_paths_to_leaf()
    browser.quit()
    logger.info("Keyword Gen Finished!")


if __name__ == "__main__":
    logger.info("Start to crawl keywords")
    for index in range(len(wordDict)):
        keywordsFile = "./data/keyWordList-" + wordDict[divison] + ".txt"
        logger.info(f"Start to crawl keywords with {wordDict[index]}")
        if os.path.exists(keywordsFile):
            with open(keywordsFile, "r") as f:
                f.seek(-2, os.SEEK_END)
                # 循环向前搜索换行符
                while f.read(1) != b"\n":
                    f.seek(-2, os.SEEK_CUR)
                # 读取最后一行
                last_line = f.readline().strip()
            if last_line == "[EOF]":
                # 标记该前缀已经爬取完毕
                logger.info(f"Skip {wordDict[index]}")
                continue
        divison = index  # 0~37
        main()
        # Add [EOF] to the end of the file
        with open(keywordsFile, "a+") as f:
            f.write("[EOF]\n")
        logger.info(f"Finished {wordDict[index]}")
