#!/usr/bin/env sh
set -eu

required_vars="STREAMLIT_REDIRECT_URI STREAMLIT_COOKIE_SECRET STREAMLIT_CLIENT_ID STREAMLIT_CLIENT_SECRET STREAMLIT_SERVER_METADATA_URL"
for v in $required_vars; do
  eval "val=\${$v-}"
  if [ -z "$val" ]; then
    echo "[entrypoint] ERROR: env var '$v' is missing or empty" >&2
    exit 1
  fi
done

mkdir -p .streamlit
cat > .streamlit/secrets.toml <<EOF
[auth]
redirect_uri = "${STREAMLIT_REDIRECT_URI}"
cookie_secret = "${STREAMLIT_COOKIE_SECRET}"
client_id = "${STREAMLIT_CLIENT_ID}"
client_secret = "${STREAMLIT_CLIENT_SECRET}"
server_metadata_url = "${STREAMLIT_SERVER_METADATA_URL}"
EOF

if [ "$#" -eq 0 ]; then
  exec streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0
else
  exec "$@"
fi
