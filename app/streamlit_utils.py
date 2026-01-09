"""Streamlit 로그인 및 secrets.toml 파일 생성을 위한 유틸리티 함수들입니다."""

import os

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


def stream_generator(chain, question, config):
    """Stream answer chunks and remember the latest source metadata."""
    sources = []
    for chunk in chain.stream({"question": question}, config):
        if "output" in chunk:
            yield chunk["output"]
        if "source_documents" in chunk:
            documents = chunk["source_documents"]
            sources = [dict(metadata or {}) for metadata in documents]
    st.session_state["latest_sources"] = sources


def _get_env_value(primary: str, fallback: str) -> str | None:
    """Get environment variable value with a fallback option."""
    return os.getenv(primary) or os.getenv(fallback)


def ensure_secrets_toml() -> None:
    """Create .streamlit/secrets.toml from env if it does not exist."""
    secrets_path = os.path.join(".streamlit", "secrets.toml")
    if os.path.exists(secrets_path):
        return

    redirect_uri = _get_env_value("redirect_uri", "STREAMLIT_REDIRECT_URI")
    cookie_secret = _get_env_value("cookie_secret", "STREAMLIT_COOKIE_SECRET")
    client_id = _get_env_value("client_id", "STREAMLIT_CLIENT_ID")
    client_secret = _get_env_value("client_secret", "STREAMLIT_CLIENT_SECRET")
    server_metadata_url = _get_env_value("server_metadata_url", "STREAMLIT_SERVER_METADATA_URL")

    if not all([redirect_uri, cookie_secret, client_id, client_secret, server_metadata_url]):
        return

    os.makedirs(os.path.dirname(secrets_path), exist_ok=True)
    with open(secrets_path, "w", encoding="utf-8") as f:
        f.write(
            "[auth]\n"
            f'redirect_uri = "{redirect_uri}"\n'
            f'cookie_secret = "{cookie_secret}"\n'
            f'client_id = "{client_id}"\n'
            f'client_secret = "{client_secret}"\n'
            f'server_metadata_url = "{server_metadata_url}"\n'
        )


# ==================================================================================
def _render_reference_list(metadata_list):
    """RAG 답변의 출처 문서 목록을 렌더링합니다.

    :param metadata_list: 출처 문서 메타데이터 리스트
    """
    if not metadata_list:
        return
    st.markdown("##### 참고 문서:")
    grouped = {}
    for metadata in metadata_list:
        if not isinstance(metadata, dict):
            continue
        key = (metadata.get("source", "출처 미상"), metadata.get("link"))
        grouped.setdefault(key, []).append(metadata.get("page"))

    rendered_items = []
    for (name, link), pages in grouped.items():
        sorted_pages = sorted(
            (p for p in pages if p is not None),
            key=lambda p: (int(p) if str(p).isdigit() else p),
        )
        page_text = ", ".join(str(p) for p in sorted_pages) + " 페이지" if sorted_pages else ""
        if link:
            link_html = f"<a href='{link}' target='_blank'>{name}</a>"
        else:
            link_html = name

        rendered_items.append(f"<div style='margin-bottom:4px;'>- {link_html}: {page_text}</div>")

    st.markdown("\n".join(rendered_items), unsafe_allow_html=True)


# ==================================================================================
