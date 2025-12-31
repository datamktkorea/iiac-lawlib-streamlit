#!/usr/bin/env sh
set -eu

# Streamlit이 secrets를 찾는 위치는 "현재 작업 디렉토리/.streamlit" 또는 "~/.streamlit"이므로
# 안전하게 둘 다 만들어주거나, 적어도 CWD 기준 위치를 확실히 맞춥니다.
mkdir -p .streamlit

cat > .streamlit/secrets.toml <<EOF
[auth]
redirect_uri = "${redirect_uri}"
cookie_secret = "${cookie_secret}"
client_id = "${client_id}"
client_secret = "${client_secret}"
server_metadata_url = "${server_metadata_url}"
EOF
