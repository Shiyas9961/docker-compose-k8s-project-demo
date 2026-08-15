#!/bin/sh

set -eu

TEMPLATE_FILE="/usr/share/nginx/html/env.template.js"
OUTPUT_FILE="/usr/share/nginx/html/env.js"

# Runtime default values
export API_URL="${API_URL:-http://localhost:8000}"
export APP_NAME="${APP_NAME:-React Application}"
export APP_ENV="${APP_ENV:-production}"

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: Runtime environment template not found:"
    echo "$TEMPLATE_FILE"
    exit 1
fi

echo "Generating runtime environment configuration..."

envsubst '${API_URL} ${APP_NAME} ${APP_ENV}' \
    < "$TEMPLATE_FILE" \
    > "$OUTPUT_FILE"

echo "Runtime configuration generated:"
cat "$OUTPUT_FILE"