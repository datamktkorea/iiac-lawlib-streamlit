import streamlit as st


def login_screen():
    """로그인 상태를 확인하고, 비로그인 시 로그인 화면을 표시합니다."""
    if not st.user.is_logged_in:
        st.image(
            "https://dmk-mdr-backend-beta.s3.ap-northeast-2.amazonaws.com/media/etc/iiac-logo.png",
            width=200,
        )
        st.header("인천국제공항공사 AI 비서 서비스")
        st.markdown(
            """
            <div style='color: white; margin-bottom: 10px;'>
            사내 규정, 지침, 매뉴얼 등 방대한 데이터를  
            AI가 빠르고 정확하게 찾아드립니다.
            </div>

            <div style='color: gray;'>
                <strong>주요 기능</strong>
                <ul style="padding-left: 20px; margin-top: 5px;">
                    <li style="margin-bottom: 8px;">📚 사내 규정 및 지침 검색</li>
                    <li style="margin-bottom: 8px;">✈️ 출장 및 파견 절차 안내</li>
                    <li style="margin-bottom: 8px;">💡 업무 관련 질의응답</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write("")  # 여백
        st.button("Microsoft 계정으로 로그인", on_click=st.login)
        st.stop()
