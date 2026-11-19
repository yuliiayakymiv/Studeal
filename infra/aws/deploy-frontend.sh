#!/usr/bin/env bash
set -euo pipefail
export MSYS_NO_PATHCONV=1

STATE_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.state"
[[ -f "$STATE_FILE" ]] && source "$STATE_FILE"

S3_BUCKET="${S3_BUCKET:-}"
CLOUDFRONT_DISTRIBUTION_ID="${CLOUDFRONT_DISTRIBUTION_ID:-${CF_DIST_ID:-}}"
: "${S3_BUCKET:?set S3_BUCKET or run 05-frontend.sh first}"
: "${CLOUDFRONT_DISTRIBUTION_ID:?set CLOUDFRONT_DISTRIBUTION_ID or run 05-frontend.sh first}"

VITE_API_URL="${VITE_API_URL:-}"
AUTH_STACK="${AUTH_STACK:-studeal-auth}"
output() {
  aws cloudformation describe-stacks --stack-name "$AUTH_STACK" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text 2>/dev/null | tr -d '\r'
}
if aws cloudformation describe-stacks --stack-name "$AUTH_STACK" >/dev/null 2>&1; then
  VITE_COGNITO_ISSUER=$(output Authority)
  VITE_COGNITO_CLIENT_ID=$(output UserPoolClientId)
  VITE_COGNITO_DOMAIN=$(output CognitoDomain)
  echo "==> Sign-in: $VITE_COGNITO_DOMAIN (client $VITE_COGNITO_CLIENT_ID)"
else
  echo "==> Stack $AUTH_STACK not found: building without sign-in"
fi

echo "==> Building frontend (VITE_API_URL=${VITE_API_URL:-<same origin>})"
(cd frontend && npm ci && VITE_API_URL="$VITE_API_URL" \
  VITE_COGNITO_ISSUER="${VITE_COGNITO_ISSUER:-}" \
  VITE_COGNITO_AUTHORITY="${VITE_COGNITO_ISSUER:-}" \
  VITE_COGNITO_CLIENT_ID="${VITE_COGNITO_CLIENT_ID:-}" \
  VITE_COGNITO_DOMAIN="${VITE_COGNITO_DOMAIN:-}" npm run build)

echo "==> Uploading to s3://$S3_BUCKET"
# Only Vite's hashed files (assets/*) may be cached forever; favicon.svg and other files from
# frontend/public keep their names, so browsers must check them for changes.
aws s3 sync frontend/dist "s3://$S3_BUCKET" --delete --exclude "*" --include "assets/*" \
  --cache-control "public,max-age=31536000,immutable"
aws s3 sync frontend/dist "s3://$S3_BUCKET" --delete --exclude "assets/*" --exclude index.html \
  --cache-control "no-cache"
aws s3 cp frontend/dist/index.html "s3://$S3_BUCKET/index.html" --cache-control "no-cache"

echo "==> Invalidating CloudFront cache"
aws cloudfront create-invalidation --distribution-id "$CLOUDFRONT_DISTRIBUTION_ID" \
  --paths "/*" --query Invalidation.Id --output text
