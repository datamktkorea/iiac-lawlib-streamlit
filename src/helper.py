import json
import os
import random
import re
import time
from typing import List
from urllib.parse import parse_qs, urlparse
from langchain_chroma import Chroma
import openai
import requests
from bs4 import BeautifulSoup
from constants import HEADERS
from dotenv import load_dotenv

# (1) 문서 로딩
# langchain 1.0 이상부터 langchain_community로 로더들 이동
from langchain_community.document_loaders import PyPDFLoader

# (2) splitter로 문서 분할
from langchain.text_splitter import RecursiveCharacterTextSplitter
from pykospacing import Spacing  # pypi 공식 레지스트리에서 내려감. github 사용
from langchain_openai import OpenAIEmbeddings # (3) embedding
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def extract_links(url: str, page: int, result: List[str]):
    response = requests.get(
        url=url + "/current", params={"page": page}, headers=HEADERS
    )
    soup = BeautifulSoup(response.text, "html.parser")

    links = soup.select("div[class*='MenuListItemTypeDate__MenuListItem'] > a")

    if len(links) == 0:
        return None
    else:
        result.extend(links)
        time.sleep(random.randint(1, 3))
        extract_links(url, page + 1, result)

    return result


def extract_pdf_urls(url: str, links: List[str]):
    result = []

    for link in links:
        response = requests.get(url=url + link.get("href"), headers=HEADERS)
        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.select_one("h1").text

        parsed_url = urlparse(soup.select_one("iframe#viewer").get("src"))
        pdf_url = parse_qs(parsed_url.query)["path"][0]

        result.append({"title": title, "url": pdf_url})

        # time.sleep(random.randint(1, 3))

    return result


def download_pdf_files(path):
    with open(path) as f:
        items = json.load(f)

    for item in items:
        response = requests.get(url=item["url"], headers=HEADERS, stream=True)

        file_path = os.path.join(os.getcwd(), "pdf", item["title"])
        with open(file_path, "wb") as f:
            f.write(response.content)


def insert_pdf_file(path, link_map): # (2) splitter로 문서 분할
    spacing = Spacing()
    embeddings = OpenAIEmbeddings() # (3) embedding

    loader = PyPDFLoader(path) 
    raw_documents = loader.load()

    link = ""
    for x in link_map:
        if x["title"] == path[4:]:
            link = x["url"]
            break

    for raw_doc in raw_documents:
        raw_doc.page_content = re.sub(r"\-\s?\d*\s?\-", "", raw_doc.page_content)

        raw_doc.metadata.update({"source": raw_doc.metadata.get("source")[4:-4]})
        raw_doc.metadata.update({"page": raw_doc.metadata.get("page") + 1})
        raw_doc.metadata.update({"link": link})

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=0)
    documents = text_splitter.split_documents(raw_documents)

    for document in documents:
        document.page_content = re.sub("[\n\s]", "", document.page_content)
        document.page_content = spacing(document.page_content)

    Chroma.from_documents(
        documents,
        embeddings,
        collection_name="iiac_poc"
    )

    os.replace(path, "dump/" + path[4:])

    return None


if __name__ == "__main__":
    print("Hello IIAC!")

    # target_links = []

    # base_page = 1
    # base_url = "https://www.iiaclaw.kr"

    # extract_links(base_url, base_page, target_links)
    # pdf_urls = extract_pdf_urls(base_url, target_links)

    # with open("iiaclaw.json", "w") as f:
    #     f.write(json.dumps(pdf_urls, ensure_ascii=False, indent=4))

    # download_pdf_files("json/iiaclaw.json")

    with open("json/iiaclaw.json") as f: 
        link_map = json.load(f)

    files = os.listdir("pdf")
    for idx, file in enumerate(files):
        print(f"{idx+1}/{len(files)}: {file}")
        insert_pdf_file(os.path.join("pdf", file), link_map)
