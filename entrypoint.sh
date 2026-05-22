#!/bin/sh
# Inject runtime env vars into the frontend config before nginx starts
cat > /usr/share/nginx/html/config.js <<EOF
window.__CONFIG__ = {
  RECEPTIONIST_NAME: "${RECEPTIONIST_NAME:-Priya}",
  CLINIC_NAME: "${CLINIC_NAME:-Demo Clinic}"
};
EOF

exec /usr/bin/supervisord -c /etc/supervisor/supervisord.conf
