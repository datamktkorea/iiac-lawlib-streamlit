"""ChromaDB 내용 확인을 위한 스크립트."""

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv(".env")


def check_chromadb():
    """ChromaDB의 내용을 확인합니다."""
    # embeddings 초기화
    embeddings = OpenAIEmbeddings()

    # vectorstore 연결
    vectorstore = Chroma(
        embedding_function=embeddings,
        collection_name="iiac_poc",
        persist_directory="./chroma_langchain_db",
    )

    print("=== ChromaDB 정보 확인 ===")

    # 1. 전체 데이터 가져오기
    try:
        all_data = vectorstore.get()
        print(f"✅ 총 문서 수: {len(all_data['documents'])}")
        print(f"✅ 총 메타데이터 수: {len(all_data['metadatas'])}")
        print(f"✅ 총 ID 수: {len(all_data['ids'])}")

        # 2. 첫 5개 문서 미리보기
        print("\n=== 문서 미리보기 (첫 5개) ===")
        for i in range(min(5, len(all_data["documents"]))):
            print(f"\n📄 문서 {i+1}:")
            print(f"ID: {all_data['ids'][i]}")
            print(f"내용: {all_data['documents'][i][:200]}...")  # 처음 200자만
            print(f"메타데이터: {all_data['metadatas'][i]}")
            print("-" * 50)

    except Exception as e:
        print(f"❌ 데이터 조회 중 오류: {e}")

    # 3. 샘플 검색 테스트
    print("\n=== 검색 테스트 ===")
    try:
        test_query = "국외 출장"
        results = vectorstore.similarity_search(test_query, k=3)
        print(f"🔍 '{test_query}' 검색 결과: {len(results)}개 문서")

        for i, doc in enumerate(results):
            print(f"\n📋 검색 결과 {i+1}:")
            print(f"내용: {doc.page_content[:150]}...")
            print(f"메타데이터: {doc.metadata}")

    except Exception as e:
        print(f"❌ 검색 중 오류: {e}")


if __name__ == "__main__":
    check_chromadb()
