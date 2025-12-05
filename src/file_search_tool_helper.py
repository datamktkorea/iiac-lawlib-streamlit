import os
import time
import random
import json
import random
import re
import time
from typing import List
import openai
import requests
from bs4 import BeautifulSoup
from constants import HEADERS
from dotenv import load_dotenv
from urllib.parse import parse_qs, urlparse


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

        file_path = os.path.join(os.getcwd(), "pdf_urls", item["title"])
        with open(file_path, "wb") as f:
            f.write(response.content)


if __name__ == "__main__":
    print("Hello IIAC!")

    target_links = []

    base_page = 1
    base_url = "https://www.iiaclaw.kr"

    extract_links(base_url, base_page, target_links)
    pdf_urls = extract_pdf_urls(base_url, target_links)

    os.makedirs("pdf_urls", exist_ok=True)
    os.makedirs("original_pdf", exist_ok=True)
    
    with open("pdf_urls/pdf_urls.json", "w") as f:
        f.write(json.dumps(pdf_urls, ensure_ascii=False, indent=4))

    download_pdf_files("pdf_urls/pdf_urls.json")
