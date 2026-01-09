"""인천국제공항공사 AI 비서 메인 애플리케이션.

이 모듈은 Streamlit을 사용하여 OpenAI와 Gemini 모델을 선택할 수 있는
채팅 인터페이스를 제공합니다.
"""

import streamlit as st
from core.rag_chain import build_chain
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from streamlit_utils import (
    _render_reference_list,
    ensure_secrets_toml,
    login_screen,
    stream_generator,
)

ensure_secrets_toml()

options = ("OpenAI", "Gemini")
openai_versions = (
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-5",
)

gemini_versions = (
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash",
    "gemini-3-flash-preview",
)

msgs_map = {}
for opt in options:
    msgs_map[opt.lower()] = StreamlitChatMessageHistory(key=f"chat_messages_{opt.lower()}")

for k, v in msgs_map.items():
    if len(v.messages) == 0:
        v.add_ai_message("무엇을 도와드릴까요?")

avatar_map = {"ai": "app/assets/mdr-logo-180x180.png", "human": "👨‍💻"}

for opt in options:
    st.session_state.setdefault(f"sources_history_{opt.lower()}", {})


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
    st.header("환영합니다!")
    st.button("Logout", on_click=st.logout)

# ==================================================================================
# 메인 화면 설정
header_col, controls_col = st.columns([3, 3.5])  # 헤더, 모델 선택 영역

with header_col:
    st.markdown(
        "<h2 style='font-size:1.8rem;margin-top:3px;'>인천국제공항공사 AI 비서</h2>",
        unsafe_allow_html=True,
    )

# 모델 선택 컨트롤을 오른쪽 컬럼 내부에서 2분할
with controls_col:
    st.write("")
    col2, col3 = st.columns([1.0, 1.5])

    with col2:
        option = st.selectbox(
            "사용할 LLM 모델을 선택해주세요.",
            options,
            label_visibility="collapsed",
            index=0,  # index = 0: 디폴트가 index 0 (open ai) 선택
        )

    with col3:
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
current_history = msgs_map[option.lower()]
sources_history_key = f"sources_history_{option.lower()}"
sources_history = st.session_state.get(sources_history_key, {})

for idx, msg in enumerate(current_history.messages):
    with st.chat_message(msg.type, avatar=avatar_map.get(msg.type)):
        st.write(msg.content)
        if msg.type == "ai":
            _render_reference_list(sources_history.get(idx))

# 2. 사용자 입력 처리
if question := st.chat_input("질문을 입력해주세요"):
    # 사용자 메시지 즉시 표시
    with st.chat_message("human", avatar=avatar_map.get("human")):
        st.write(question)

    # AI 응답 처리 (스피너 표시)
    with st.chat_message("ai", avatar=avatar_map.get("ai")):
        with st.spinner("답변을 생성하고 있습니다..."):
            config = {"configurable": {"session_id": "any"}}
            chain = build_chain(option, version_option, current_history)
            st.session_state["latest_sources"] = []
            st.write_stream(stream_generator(chain, question, config))
            sources = st.session_state.get("latest_sources", [])
            if sources and current_history.messages:
                last_index = len(current_history.messages) - 1
                sources_history[last_index] = sources
                st.session_state[sources_history_key] = sources_history
                st.rerun()


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


# NOTE: uv run -m streamlit run app/main.py
