import streamlit as st
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

from app.core import gemini, openai

options = ("OpenAI", "Gemini")

# ==================================================================================
msgs_map = {}
for opt in options:
    msgs_map[opt.lower()] = StreamlitChatMessageHistory(
        key=f"chat_messages_{opt.lower()}"
    )

for k, v in msgs_map.items():
    if len(v.messages) == 0:
        v.add_ai_message("무엇을 도와드릴까요?")

avatar_map = {"ai": "app/assets/mdr-logo-180x180.png", "human": "👨‍💻"}

chain_map = {"openai": openai.get_chain, "gemini": gemini.get_chain}

# ==================================================================================
st.set_page_config(
    page_title="인천국제공항공사 | 생성형 AI",
    page_icon="airplane",
)

st.header("인천국제공항공사 AI 비서")

option = st.selectbox(
    "사용할 LLM 모델을 선택해주세요.", options, label_visibility="collapsed", index=0
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

if question := st.chat_input("질문을 입력해주세요"):
    config = {"configurable": {"session_id": "any"}}
    response = chain_map[option.lower()](msgs_map[option.lower()]).invoke(
        {"question": question}, config
    )

for msg in msgs_map[option.lower()].messages:
    message = st.chat_message(msg.type, avatar=avatar_map.get(msg.type))
    message.write(msg.content)

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
