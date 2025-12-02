"""OpenAI API를 사용한 RAG(Retrieval-Augmented Generation) 체인 구현.

이 모듈은 인천국제공항공사의 정보를 담은 벡터 데이터베이스를 활용하여
OpenAI와 Gemini 모델 기반의 질의응답 체인을 구축합니다.
"""

import os

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import GoogleGenerativeAI
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv(".env")

# API Key 확인
for key in ["OPENAI_API_KEY", "GOOGLE_API_KEY"]:
    if not os.environ.get(key):
        raise ValueError(f"환경 변수 '{key}'가 설정되지 않았습니다.")


contextualize_q_system_prompt = """
    채팅 기록과 사용자가 최근에 한 질문이 제공되었습니다.
    이 질문은 채팅 기록 속의 맥락을 참고할 가능성이 있습니다.
    사용자의 질문을 채팅 기록 없이도 독립적으로 이해할 수 있는 형태로 재구성해 주세요.
    질문에 직접 답변을 제공하지는 말고, 필요하다면 질문을 명확하고 이해하기 쉬운 방식으로 다시 표현해주세요.
    만약 재구성할 필요가 없다면 원래의 질문을 그대로 유지해 주세요.
    """

qa_system_prompt = """
    당신은 이제부터 인천국제공항공사에 대한 모든 정보를 파악하고 있는 전문가 어시스턴트로 활동하게 됩니다.
    아래 제시된 정보를 바탕으로 마지막에 주어진 질문에 대해 답변해주세요.
    만약 답을 모르는 경우, 정직하게 모른다고 답변해주세요. 답변을 지어내려고 하지 마세요.
    정확하고 심도 있는 답변을 제공하며, 질문의 본질을 꿰뚫어 보는 전문가적인 시각에서 최대한 세부적이고 명확하게 답변해주시길 바랍니다.
    가능한 경우, 답변을 뒷받침할 수 있는 구체적인 예시나 사례를 함께 제시해주세요. 이는 답변의 신뢰성과 이해도를 높이는 데 도움이 됩니다.
    답변을 제공할 때는 해당 분야의 기본 용어나 개념을 명확하게 설명하여, 질문에 대한 깊이 있는 분석과 함께 전문성을 드러내주세요.

    {context}
    """


class RAGChainBuilder:
    """RAG 체인을 구축하고 관리하는 클래스."""

    def __init__(self, llm_type: str, version_option: str):
        """Args:
        llm_type (str): 사용할 LLM 타입 ("OpenAI" 또는 "Gemini").
        version_option (str): 사용할 모델 버전.
        """
        self.llm = self._create_llm(llm_type, version_option)
        self.retriever = self._create_retriever()

    def _create_llm(self, llm_type: str, version_option: str):
        """LLM 인스턴스를 생성합니다."""
        match llm_type:
            case "OpenAI":
                return ChatOpenAI(model_name=version_option, temperature=0)
            case "Gemini":
                return GoogleGenerativeAI(
                    model=version_option, google_api_key=os.getenv("GOOGLE_API_KEY")
                )
            case _:
                raise ValueError(f"지원하지 않는 LLM 타입입니다: {llm_type}")

    def _create_retriever(self):
        """ChromaDB 검색기를 설정합니다."""
        embeddings = OpenAIEmbeddings()
        vector_db = Chroma(
            embedding_function=embeddings,
            collection_name="iiac_poc",
            persist_directory="./chroma_langchain_db",
        )
        return vector_db.as_retriever(search_type="similarity", search_kwargs={"k": 6})

    def build(self, messages):
        """메시지 히스토리가 포함된 실행 가능한 체인을 반환합니다.

        Args:
            messages: 채팅 메시지 히스토리 객체.

        Returns:
            RunnableWithMessageHistory: 메시지 히스토리가 포함된 실행 가능한 체인.
        """
        # 1. 질문 재구성 체인
        contextualize_q_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )
        contextualize_chain = contextualize_q_prompt | self.llm | StrOutputParser()

        def contextualized_question(input: dict):
            if input.get("chat_history"):
                return contextualize_chain.invoke(input)
            else:
                return input["question"]

        # 2. 답변 생성 체인
        qa_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", qa_system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{question}"),
            ]
        )
        qa_chain = qa_prompt | self.llm | StrOutputParser()

        # 3. 전체 체인 조립
        chain_from_docs = (
            RunnablePassthrough.assign(
                context=(lambda x: "\n\n".join(doc.page_content for doc in x["context"]))
            )
            | qa_chain
        )

        chain_with_source = RunnableParallel(
            {
                "context": contextualized_question | self.retriever,
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


def build_chain(llm_type: str, version_option: str, messages):
    """기존 호환성을 위한 래퍼 함수.

    Args:
        llm_type (str): 사용할 LLM 타입 ("OpenAI" 또는 "Gemini").
        version_option (str): 사용할 모델 버전.
        messages: 채팅 메시지 히스토리 객체.

    Returns:
        RunnableWithMessageHistory: 메시지 히스토리가 포함된 실행 가능한 체인.
    """
    builder = RAGChainBuilder(llm_type, version_option)
    return builder.build(messages)
