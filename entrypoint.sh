#!/usr/bin/env sh
set -eu

required_vars="redirect_uri cookie_secret client_id client_secret server_metadata_url"
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
redirect_uri = "${redirect_uri}"
cookie_secret = "${cookie_secret}"
client_id = "${client_id}"
client_secret = "${client_secret}"
server_metadata_url = "${server_metadata_url}"
EOF

exec "$@"
