from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings()

# 실제 사용하는 DB 경로
PERSIST_PATH = "/home/moon/dmk/iiac-lawlib-streamlit/chroma_langchain_db/73409af8-1da2-4208-ba38-faff2e02880f"

# 클라이언트 객체 직접 접근
from chromadb import PersistentClient
client = PersistentClient(path=PERSIST_PATH)

print("✅ 현재 존재하는 컬렉션 목록:")
collections = client.list_collections()
for col in collections:
    print(f" - {col.name}")
