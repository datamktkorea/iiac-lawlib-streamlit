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

chain_maps = {"openai": openai.get_chain, "gemini": gemini.get_chain}

# ==================================================================================
st.set_page_config(layout="wide")

question = st.chat_input("질문을 입력해주세요...")

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

with col2:
    option2 = st.selectbox(
        "사용할 LLM 모델을 선택해주세요.", options, key="option2", index=1
    )

    if question and option1 != option2:
        config = {"configurable": {"session_id": "any"}}
        response = chain_maps[option2.lower()](msgs_map[option2.lower()]).invoke(
            {"question": question}, config
        )

    for msg in msgs_map[option2.lower()].messages:
        message = st.chat_message(msg.type)
        message.write(msg.content)

# python3 -m streamlit run app/main.py
