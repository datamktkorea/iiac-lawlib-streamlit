"""OpenAI API를 사용한 RAG(Retrieval-Augmented Generation) 체인 구현.

이 모듈은 인천국제공항공사의 정보를 담은 벡터 데이터베이스를 활용하여
OpenAI 모델 기반의 질의응답 체인을 구축합니다.
"""

import getpass
import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv(".env")

if not os.environ.get("OPENAI_API_KEY"):  # .env 읽어오지 못했을 경우 수동 입력
    os.environ["OPENAI_API_KEY"] = getpass.getpass("Enter API key for Open AI: ")


embeddings = OpenAIEmbeddings()

vectorstore = Chroma(
    embedding_function=embeddings,
    collection_name="iiac_poc",
    persist_directory="./chroma_langchain_db",
)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})


def build_chain(version_option: str, messages):
    """지정된 OpenAI 모델 버전으로 RAG 체인을 구축.

    Args:
        version_option (str): 사용할 OpenAI 모델 버전.
        messages: 채팅 메시지 히스토리 객체.

    Returns:
        RunnableWithMessageHistory: 메시지 히스토리가 포함된 실행 가능한 체인.
    """
    llm = ChatOpenAI(model_name=version_option, temperature=0)

    contextualize_q_system_prompt = """
    채팅 기록과 사용자가 최근에 한 질문이 제공되었습니다.
    이 질문은 채팅 기록 속의 맥락을 참고할 가능성이 있습니다.
    사용자의 질문을 채팅 기록 없이도 독립적으로 이해할 수 있는 형태로 재구성해 주세요.
    질문에 직접 답변을 제공하지는 말고, 필요하다면 질문을 명확하고 이해하기 쉬운 방식으로 다시 표현해주세요.
    만약 재구성할 필요가 없다면 원래의 질문을 그대로 유지해 주세요.
    """

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    def contextualize_q_chain():
        """질문을 맥락화하는 체인을 생성.

        Returns:
            Chain: 질문을 독립적으로 이해할 수 있게 재구성하는 체인.
        """
        return contextualize_q_prompt | llm | StrOutputParser()

    def contextualized_question(input: dict):
        """채팅 히스토리를 고려하여 질문을 맥락화.

        Args:
            input (dict): 질문과 채팅 히스토리가 포함된 입력 딕셔너리.

        Returns:
            str: 맥락화된 질문 또는 원본 질문.
        """
        if input.get("chat_history"):
            return contextualize_q_chain().invoke(input)
        else:
            return input["question"]

    qa_system_prompt = """
    당신은 이제부터 인천국제공항공사에 대한 모든 정보를 파악하고 있는 전문가 어시스턴트로 활동하게 됩니다.
    아래 제시된 정보를 바탕으로 마지막에 주어진 질문에 대해 답변해주세요.
    만약 답을 모르는 경우, 정직하게 모른다고 답변해주세요. 답변을 지어내려고 하지 마세요.
    정확하고 심도 있는 답변을 제공하며, 질문의 본질을 꿰뚫어 보는 전문가적인 시각에서 최대한 세부적이고 명확하게 답변해주시길 바랍니다.
    가능한 경우, 답변을 뒷받침할 수 있는 구체적인 예시나 사례를 함께 제시해주세요. 이는 답변의 신뢰성과 이해도를 높이는 데 도움이 됩니다.
    답변을 제공할 때는 해당 분야의 기본 용어나 개념을 명확하게 설명하여, 질문에 대한 깊이 있는 분석과 함께 전문성을 드러내주세요.

    {context}
    """

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", qa_system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{question}"),
        ]
    )

    def format_docs(docs):
        """검색된 문서들을 하나의 텍스트로 포맷팅.

        Args:
            docs (list): 검색된 문서 객체들의 리스트.

        Returns:
            str: 줄바꿈으로 구분된 문서 내용 텍스트.
        """
        return "\n\n".join(doc.page_content for doc in docs)

    chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | qa_prompt
        | llm
        | StrOutputParser()
    )

    chain_with_source = RunnableParallel(
        {
            "context": contextualized_question | retriever,
            "question": RunnablePassthrough(),
            "chat_history": lambda x: x.get("chat_history"),
        }
    ).assign(output=chain_from_docs)

    return RunnableWithMessageHistory(
        chain_with_source,
        lambda session_id: messages,
        input_messages_key="question",
        history_messages_key="chat_history",
    )


# 임포트 필요

# 컬렉션에서 모든 데이터를 가져와봅니다
all_data = vectorstore.get()

# 전체 문서 수 확인
print(f"총 문서 수: {len(all_data['documents'])}")

# 일부 미리보기
for i in range(min(5, len(all_data["documents"]))):
    print(f"ID: {all_data['ids'][i]}")
    print(f"Document: {all_data['documents'][i]}")
    print(f"Metadata: {all_data['metadatas'][i]}")
    print("-" * 40)
