"""인천국제공항공사 AI 비서 메인 애플리케이션.

이 모듈은 Streamlit을 사용하여 OpenAI와 Gemini 모델을 선택할 수 있는
채팅 인터페이스를 제공합니다.
"""

import os

import streamlit as st
from core.rag_chain import build_chain
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from streamlit.runtime.secrets import secrets_singleton
from streamlit_utils import login_screen, stream_generator

options = ("OpenAI", "Gemini")
openai_versions = (
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-5",
)
gemini_versions = ("gemini-2.5-flash", "gemini-2.5-pro", "gemini-3-pro-preview")

# ==================================================================================
# Streamlit Secrets 설정 (secrets.toml 파일을 대체)
secrets_singleton._secrets = {
    "auth": {
        "redirect_uri": os.getenv("STREAMLIT_REDIRECT_URI"),
        "cookie_secret": os.getenv("STREAMLIT_COOKIE_SECRET"),
        "client_id": os.getenv("STREAMLIT_CLIENT_ID"),
        "client_secret": os.getenv("STREAMLIT_CLIENT_SECRET"),
        "server_metadata_url": os.getenv("STREAMLIT_SERVER_METADATA_URL"),
    }
}

# ==================================================================================
msgs_map = {}
for opt in options:
    msgs_map[opt.lower()] = StreamlitChatMessageHistory(key=f"chat_messages_{opt.lower()}")

for k, v in msgs_map.items():
    if len(v.messages) == 0:
        v.add_ai_message("무엇을 도와드릴까요?")

avatar_map = {"ai": "app/assets/mdr-logo-180x180.png", "human": "👨‍💻"}


# ==================================================================================
st.set_page_config(
    page_title="인천국제공항공사 | 생성형 AI",
    page_icon="airplane",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    button[kind="header"] svg {
        stroke: #ffffff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

login_screen()
# ==================================================================================
# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []


# Sidebar 설정
with st.sidebar:
    st.header("사용자 정보")
    st.write(f"환영합니다, {st.user.name}님!")
    st.button("Logout", on_click=st.logout)
# ==================================================================================
# 메인 화면 설정

col1, col2, col3 = st.columns([3, 1, 1])  # 헤더, LLM 모델 선택, 모델 버전 선택

with col1:
    st.header("인천국제공항공사 AI 비서")

# open ai / gemini 분기
with col2:
    st.write("")  # 헤더와 라인 맞추기 위한 여백
    option = st.selectbox(
        "사용할 LLM 모델을 선택해주세요.",
        options,
        label_visibility="collapsed",
        index=0,  # index = 0: 디폴트가 index 0 (open ai) 선택
    )


with col3:
    st.write("")  # 헤더와 라인 맞추기 위한 여백
    version_candidates = openai_versions if option == "OpenAI" else gemini_versions
    version_option = st.selectbox(
        "모델 버전을 선택해주세요.",
        version_candidates,
        label_visibility="collapsed",
        index=0,
    )


st.write(
    """
    :gray[현재 버전은 :blue[PoC용]이며, 답변 생성에는 :red[최소 30초에서 최대 3분]이 소요됩니다.]
    
    :gray[예시 질문:]
    - :gray[국외 출장 절차는 어떻게 진행되나요?]
    - :gray[해외 파견 시 고려해야 할 사항은 어떤 것이 있나요?]
    - :gray[인천공항공사의 운동 선수단 정보를 알려주세요.]
    """
)

# 1. 기존 메시지 먼저 출력
for msg in msgs_map[option.lower()].messages:
    message = st.chat_message(msg.type, avatar=avatar_map.get(msg.type))
    message.write(msg.content)

# 2. 사용자 입력 처리
if question := st.chat_input("질문을 입력해주세요"):
    # 사용자 메시지 즉시 표시
    with st.chat_message("human", avatar=avatar_map.get("human")):
        st.write(question)

    # AI 응답 처리 (스피너 표시)
    with st.chat_message("ai", avatar=avatar_map.get("ai")):
        with st.spinner("답변을 생성하고 있습니다..."):
            config = {"configurable": {"session_id": "any"}}
            chain = build_chain(option, version_option, msgs_map[option.lower()])
            st.write_stream(stream_generator(chain, question, config))


# ==================================================================================
# 로고 배치
st.markdown(
    """<style> .logo-img { z-index: 999999; position: fixed; top: 12px; width: auto; } .logo-datatogo { left: 24px; height: 40px; } .logo-iiac { right: 24px; height: 50px; }""",
    unsafe_allow_html=True,
)

st.markdown(
    """<img src="https://dmk-mdr-backend-beta.s3.ap-northeast-2.amazonaws.com/media/etc/datatogo-logo.png" class="logo-img logo-datatogo">""",
    unsafe_allow_html=True,
)

st.markdown(
    """<img src="https://dmk-mdr-backend-beta.s3.ap-northeast-2.amazonaws.com/media/etc/iiac-logo.png" class="logo-img logo-iiac">""",
    unsafe_allow_html=True,
)


# NOTE: python3 -m streamlit run app/main.py
