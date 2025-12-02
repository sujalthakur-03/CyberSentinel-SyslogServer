#!/bin/sh
# Runtime environment variable injection script
# This replaces placeholder values in the built React app with actual environment variables

# Create runtime env config
cat <<EOF > /usr/share/nginx/html/env-config.js
window.ENV = {
  REACT_APP_API_URL: "${REACT_APP_API_URL}"
};
EOF

echo "Environment configuration created:"
cat /usr/share/nginx/html/env-config.js

# Start nginx
exec nginx -g "daemon off;"
