import os
import asyncio
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings
)

from dotenv import load_dotenv
load_dotenv(".env")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def _ensure_event_loop():
    '''
    NOTE: There is no current event loop in thread 
    'ScriptRunner.scriptThread'. 오류 해결 위한 함수.
    모듈 최상단에서 즉시 인스턴스를 생성하면, Streamlit이 이벤트 루프를 안 만든 상태이기 때문에
    이런 오류가 종종 발생한다고 함.
    역할 : 루프가 없을 때, 루프를 생성하는 역할.
    '''
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

_ensure_event_loop()


embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=GOOGLE_API_KEY,)
vectorstore = Chroma(
    embedding_function=embeddings, 
    collection_name="iiac_gemini",
    persist_directory="./chroma_langchain_db",
)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 6})


# ToDo : app/main.py에서 선택한 버전으로 변경
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, google_api_key=GOOGLE_API_KEY,)

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

contextualize_q_chain = contextualize_q_prompt | llm | StrOutputParser()


def contextualized_question(input_: dict):
    if input_.get("chat_history"):
        return contextualize_q_chain
    else:
        return input_["question"]


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


def get_chain(messages):
    return RunnableWithMessageHistory(
        chain_with_source,
        lambda session_id: messages,
        input_messages_key="question",
        history_messages_key="chat_history",
    )
