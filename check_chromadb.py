"""ChromaDB 내용 확인을 위한 스크립트."""

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv(".env")


def connect_to_chromadb():
    """ChromaDB에 연결합니다.

    Returns:
        Chroma: 연결된 ChromaDB 벡터 저장소 객체.
    """
    print("=== 1. ChromaDB 연결 ===")
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma(
        embedding_function=embeddings,
        collection_name="iiac_poc",
        persist_directory="./chroma_langchain_db",
    )
    return vectorstore


def fetch_all_data(vectorstore):
    """전체 데이터를 가져와 확인합니다.

    Args:
        vectorstore (Chroma): 확인할 ChromaDB 벡터 저장소 객체.
    """
    print("\n=== 2. 전체 데이터 확인 ===")
    try:
        all_data = vectorstore.get()
        print(f"✅ 총 문서 수: {len(all_data['documents'])}")
        print(f"✅ 총 메타데이터 수: {len(all_data['metadatas'])}")
        print(f"✅ 총 ID 수: {len(all_data['ids'])}")

        # 첫 5개 문서 미리보기
        print("\n--- 문서 미리보기 (첫 5개) ---")
        for i in range(min(5, len(all_data["documents"]))):
            print(f"\n📄 문서 {i+1}:")
            print(f"ID: {all_data['ids'][i]}")
            print(f"내용: {all_data['documents'][i][:200]}...")  # 처음 200자만
            print(f"메타데이터: {all_data['metadatas'][i]}")
            print("-" * 50)

    except Exception as e:
        print(f"❌ 데이터 조회 중 오류: {e}")


def search_sample(vectorstore, query="국외 출장"):
    """Query 파라미터로 샘플 검색을 수행합니다.

    Args:
        vectorstore (Chroma): 검색을 수행할 ChromaDB 벡터 저장소 객체.
        query (str, optional): 검색할 키워드. 기본값은 "국외 출장".
    """
    print(f"\n=== 3. 샘플 검색 테스트 ('{query}') ===")
    try:
        results = vectorstore.similarity_search(query, k=3)
        print(f"🔍 검색 결과: {len(results)}개 문서")

        for i, doc in enumerate(results):
            print(f"\n📋 검색 결과 {i+1}:")
            print(f"내용: {doc.page_content[:150]}...")
            print(f"메타데이터: {doc.metadata}")

    except Exception as e:
        print(f"❌ 검색 중 오류: {e}")


if __name__ == "__main__":
    vector_db = connect_to_chromadb()
    fetch_all_data(vector_db)
    search_sample(vector_db)
