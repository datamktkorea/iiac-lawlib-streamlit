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
    llm = ChatOpenAI(temperature=0, model_name="gpt-4")
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
        당신은 인천공항공사 직원들을 도와주는 최고의 안내직원입니다. 아래 정보를 고려해서 질문에 간결하고 친절하게 답변하기 바랍니다. 만약 정보가 질문에 정확하게 답변하기 어렵다면 죄송하다고 답변하기 바랍니다.

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
