"""인천국제공항공사 법률 사이트에서 PDF 문서를 수집하고 벡터화하는 헬퍼 모듈.

이 모듈은 웹 스크래핑을 통해 PDF 파일을 다운로드하고, 이를 처리하여
ChromaDB 벡터 데이터베이스에 저장하는 기능을 제공합니다.
"""

import json
import os
import random
import re
import time
from typing import List
from urllib.parse import parse_qs, urlparse

import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# (2) splitter로 문서 분할
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

# (1) 문서 로딩
# langchain 1.0 이상부터 langchain_community로 로더들 이동
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings  # (3) embedding
from pykospacing import (
    Spacing,  # pypi 공식 레지스트리에서 내려감. # github에서 import시 모듈 오류로 로컬 패키지 (packages/local-pykospacing)로 분리해 코드 수정 후 사용함.
)

from constants import HEADERS

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def extract_links(url: str, page: int, result: List[str]):
    """웹사이트에서 페이지별로 링크를 재귀적으로 추출.

    Args:
        url (str): 기본 URL 주소.
        page (int): 추출할 페이지 번호.
        result (List[str]): 추출된 링크들을 저장할 리스트.

    Returns:
        List[str] or None: 추출된 링크 리스트 또는 더 이상 링크가 없을 경우 None.
    """
    response = requests.get(url=url + "/current", params={"page": page}, headers=HEADERS)
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
    """추출된 링크들에서 PDF 파일의 제목과 URL을 추출.

    Args:
        url (str): 기본 URL 주소.
        links (List[str]): PDF가 포함된 페이지 링크들.

    Returns:
        List[Dict[str, str]]: 제목과 URL이 포함된 딕셔너리들의 리스트.
    """
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
    """JSON 파일에 저장된 PDF URL 정보를 사용하여 PDF 파일들을 다운로드.

    Args:
        path: PDF URL 정보가 저장된 JSON 파일의 경로.
    """
    with open(path) as f:
        items = json.load(f)

    for item in items:
        response = requests.get(url=item["url"], headers=HEADERS, stream=True)

        file_path = os.path.join(os.getcwd(), "pdf", item["title"])
        with open(file_path, "wb") as f:
            f.write(response.content)


def insert_pdf_file(path, link_map):
    """PDF 파일을 처리하여 ChromaDB 벡터 데이터베이스에 삽입.

    PDF 파일을 로드하고, 텍스트를 분할한 후, 한국어 띄어쓰기를 교정하여
    벡터 데이터베이스에 저장합니다.

    Args:
        path: 처리할 PDF 파일의 경로.
        link_map: PDF 파일과 원본 링크 매핑 정보.

    Returns:
        None
    """
    spacing = Spacing()
    embeddings = OpenAIEmbeddings()  # (3) embedding

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
    print(f"[DEBUG] {path} 문서 분할 후 {len(documents)}개 chunk 생성됨")
    if len(documents) > 0:
        print(f"[DEBUG] 첫 번째 chunk 내용 샘플:\n{documents[0].page_content[:200]}")
    else:
        print("[DEBUG] 문서 chunk가 없습니다.")

    for document in documents:
        document.page_content = re.sub("[\n\s]", "", document.page_content)
        document.page_content = spacing(document.page_content)

    Chroma.from_documents(
        documents, embeddings, collection_name="iiac_poc", persist_directory="./chroma_langchain_db"
    )

    os.replace(path, "dump/" + path[4:])

    return None


if __name__ == "__main__":
    print("Hello IIAC!")

    target_links = []

    base_page = 1
    base_url = "https://www.iiaclaw.kr"

    extract_links(base_url, base_page, target_links)
    pdf_urls = extract_pdf_urls(base_url, target_links)

    os.makedirs("json", exist_ok=True)
    os.makedirs("pdf", exist_ok=True)
    os.makedirs("dump", exist_ok=True)

    with open("json/iiaclaw.json", "w") as f:
        f.write(json.dumps(pdf_urls, ensure_ascii=False, indent=4))

    download_pdf_files("json/iiaclaw.json")

    with open("json/iiaclaw.json") as f:
        link_map = json.load(f)

    files = os.listdir("pdf")
    for idx, file in enumerate(files):
        print(f"{idx+1}/{len(files)}: {file}")
        insert_pdf_file(os.path.join("pdf", file), link_map)
