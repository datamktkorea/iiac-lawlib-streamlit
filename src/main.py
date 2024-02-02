import os
import time
from datetime import datetime

import streamlit as st
from core import run_llm

os.makedirs("./.logs", exist_ok=True)

st.set_page_config(
    page_title="인천국제공항공사 | 생성형 AI",
    page_icon="airplane",
)

st.image(os.path.join(os.getcwd(), "src", "assets", "logo.png"), width=140)
st.header("인천공항공사 사규 검색 도우미")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": """
            안녕하세요. 현재 버전은 :blue[**PoC용**]이며, 답변 생성에는 :red[**최소 1분에서 최대 5분**]이 소요됩니다.
            
            :gray[예시 질문:]
            - :gray[국외 출장 절차는 어떻게 진행되나요?]
            - :gray[인천공항공사의 운동 선수단 정보를 알려주세요.]
            - :gray[계약직 채용에 관한 정보를 알려주세요.]
            - :gray[해외 파견 시 고려해야 할 사항은 어떤 것이 있나요?]
            - :gray[TF팀 구성 시 보고해야 할 위치는 어디인가요?]
            """,
        }
    ]


for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("궁금한 사항을 입력해주세요..."):
    start_time = time.time()
    timestamp = datetime.strftime(datetime.now(), "%Y.%m.%d.%H:%M:%S:%f")

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("답변을 준비중입니다..."):
            generated_response = run_llm(query=prompt)

        content = generated_response["result"]
        source_documents = generated_response["source_documents"]

        st.markdown("##### 답변:")
        st.markdown(content)

        st.markdown("##### 참고 문서:")
        for source_document in source_documents:
            metadata = source_document.metadata
            st.markdown(
                f"- [{metadata.get('source')}]({metadata.get('link')}) - {metadata.get('page')} 페이지"
            )

        with open(f".logs/{timestamp}.txt", "w") as file:
            file.write(f"[질문]:\n{prompt}\n\n")

        with open(f".logs/{timestamp}.txt", "a") as file:
            file.write(f"[답변]:\n{content}\n\n")

        with open(f".logs/{timestamp}.txt", "a") as file:
            file.write("[참고자료]:\n")

            for source_document in source_documents:
                metadata = source_document.metadata
                file.write(
                    f"- {metadata.get('source')}, {metadata.get('link')}, {metadata.get('page')} 페이지\n"
                )

        with open(f".logs/{timestamp}.txt", "a") as file:
            file.write(f"\n[소요시간]:\n{time.time() - start_time}")

    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.messages.append({"role": "assistant", "content": content})
