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

# ==================================================================================
st.set_page_config(
    page_title="인천국제공항공사 | 생성형 AI",
    page_icon="airplane",
)

st.header("인천국제공항공사 AI 비서")

col1, col2 = st.columns(2)

with col1:
    option1 = st.selectbox(
        "사용할 LLM 모델을 선택해주세요.", options, key="option1", index=0
    )

    if question:
        config = {"configurable": {"session_id": "any"}}
        response = chain_maps[option1.lower()](msgs_map[option1.lower()]).invoke(
            {"question": question}, config
        )

    for msg in msgs_map[option1.lower()].messages:
        message = st.chat_message(msg.type)
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

# python3 -m streamlit run app/main.py
