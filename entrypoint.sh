#!/usr/bin/env sh
set -eu

required_vars="redirect_uri cookie_secret client_id client_secret server_metadata_url"
for v in $required_vars; do
  eval "val=\${$v-}"
  if [ -z "$val" ]; then
    eval "val=\${STREAMLIT_${v^^}-}"
  fi
  if [ -z "$val" ]; then
    echo "[entrypoint] ERROR: env var '$v' or 'STREAMLIT_${v^^}' is missing or empty" >&2
    exit 1
  fi
done

redirect_uri="${redirect_uri:-${STREAMLIT_REDIRECT_URI-}}"
cookie_secret="${cookie_secret:-${STREAMLIT_COOKIE_SECRET-}}"
client_id="${client_id:-${STREAMLIT_CLIENT_ID-}}"
client_secret="${client_secret:-${STREAMLIT_CLIENT_SECRET-}}"
server_metadata_url="${server_metadata_url:-${STREAMLIT_SERVER_METADATA_URL-}}"

mkdir -p .streamlit
cat > .streamlit/secrets.toml <<EOF
[auth]
redirect_uri = "${redirect_uri}"
cookie_secret = "${cookie_secret}"
client_id = "${client_id}"
client_secret = "${client_secret}"
server_metadata_url = "${server_metadata_url}"
EOF

if [ "$#" -eq 0 ]; then
  exec streamlit run app/main.py --server.port=8501 --server.address=0.0.0.0
else
  exec "$@"
fi
