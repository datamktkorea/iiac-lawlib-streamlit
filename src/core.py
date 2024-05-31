import os
from typing import Any, Dict, List

import openai
from dotenv import load_dotenv
from langchain.chains import ConversationalRetrievalChain, LLMChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.vectorstores import Milvus

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def redefine_context(vector_db, query):
    raw_context = vector_db.similarity_search(query=query)
    raw_context = "\n".join([x.page_content for x in raw_context])

    template = """
        아래 정보를 500자 이내로 요약해줘.
        정보: {context}
    """
    prompt = PromptTemplate(template=template, input_variables=["context"])

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    return llm_chain.run(raw_context)


def run_llm_conversation(question: str, chat_history: List[Dict[str, Any]] = []):
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    embeddings = OpenAIEmbeddings()

    vector_db = Milvus(
        embedding_function=embeddings,
        collection_name="iiac_poc",
        connection_args={
            "uri": os.getenv("ZILLIZ_CLOUD_URI"),
            "token": os.getenv("ZILLIZ_CLOUD_API_KEY"),
            "secure": True,
        },
    )

    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_db.as_retriever(),
    )
    return qa({"question": question, "chat_history": chat_history})


def run_llm(query: str):
    llm = ChatOpenAI(temperature=0, model_name="gpt-4o")
    embeddings = OpenAIEmbeddings()

    vector_db = Milvus(
        embedding_function=embeddings,
        collection_name="iiac_poc",
        connection_args={
            "uri": os.getenv("ZILLIZ_CLOUD_URI"),
            "token": os.getenv("ZILLIZ_CLOUD_API_KEY"),
            "secure": True,
        },
    )

    QA_CHAIN_PROMPT = PromptTemplate.from_template(
        """
        당신은 이제부터 인천국제공항공사에 대한 모든 정보를 파악하고 있는 전문가 어시스턴트로 활동하게 됩니다.
        아래 제시된 정보를 바탕으로 마지막에 주어진 질문에 대해 답변해주세요.
        만약 답을 모르는 경우, 정직하게 모른다고 답변해주세요. 답변을 지어내려고 하지 마세요.
        정확하고 심도 있는 답변을 제공하며, 질문의 본질을 꿰뚫어 보는 전문가적인 시각에서 최대한 세부적이고 명확하게 답변해주시길 바랍니다.
        가능한 경우, 답변을 뒷받침할 수 있는 구체적인 예시나 사례를 함께 제시해주세요. 이는 답변의 신뢰성과 이해도를 높이는 데 도움이 됩니다.
        답변을 제공할 때는 해당 분야의 기본 용어나 개념을 명확하게 설명하여, 질문에 대한 깊이 있는 분석과 함께 전문성을 드러내주세요.

        {context}

        질문: {question}
        
        도움이 되는 답변:
        """
    )

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        # retriever=vector_db.as_retriever(search_kwargs={"k": 1}),
        retriever=vector_db.as_retriever(),
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT},
    )

    return qa({"query": query})


if __name__ == "__main__":
    result = run_llm(query="정책실명제에 대해서 설명해줘.")
    print(result)
