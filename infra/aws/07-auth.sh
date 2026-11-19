#!/usr/bin/env bash
# Sign-in with Cognito (Lab 4): email + password and "Continue with Google", Studeal look.
# Needs in the repo-root .env (git-ignored, never committed):
#   GOOGLE_CLIENT_ID=…   GOOGLE_CLIENT_SECRET=…   (optional: COGNITO_DOMAIN_PREFIX=…)
# The sign-in page look lives in infra/branding/ (edit there, then: python infra/branding/render.py).
source "$(dirname "$0")/env.sh"
cd "$(dirname "$0")/../.."
: "${CF_DIST_ID:?run 05-frontend.sh first}" "${CF_DOMAIN:?run 05-frontend.sh first}"

envval() { grep -E "^$1=" .env 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '\r"' || true; }
PREFIX="${COGNITO_DOMAIN_PREFIX:-$(envval COGNITO_DOMAIN_PREFIX)}"
if [[ -z "$PREFIX" ]]; then
  PREFIX="studeal-$ACCOUNT_ID"
fi
GID="${GOOGLE_CLIENT_ID:-$(envval GOOGLE_CLIENT_ID)}"
GSECRET="${GOOGLE_CLIENT_SECRET:-$(envval GOOGLE_CLIENT_SECRET)}"
: "${GID:?set GOOGLE_CLIENT_ID in .env (see infra/README.md, Google sign-in)}" \
  "${GSECRET:?set GOOGLE_CLIENT_SECRET in .env}"
AUTH_STACK="${AUTH_STACK:-studeal-auth}"
SITE_URL="https://$CF_DOMAIN"

step "CloudFormation stack $AUTH_STACK (user pool, Google IdP, app client, domain $PREFIX, branding)"
aws cloudformation deploy --stack-name "$AUTH_STACK" --template-file infra/auth.yml \
  --no-fail-on-empty-changeset --tags PROJECT_NAME=studeal \
  --parameter-overrides DomainPrefix="$PREFIX" SiteUrl="$SITE_URL" \
    GoogleClientId="$GID" GoogleClientSecret="$GSECRET"
save AUTH_STACK "$AUTH_STACK"

step "CloudFront Function: SPA routes (/catalog, /events, /saved, /deal/*) -> /index.html"
FN=studeal-spa-routes
cat > fn.rendered.js <<'JS'
function handler(event) {
  var request = event.request;
  if (request.uri.indexOf('.') === -1) request.uri = '/index.html';
  return request;
}
JS
FN_CONFIG="Comment=Studeal SPA routes,Runtime=cloudfront-js-2.0"
if ETAG=$(t aws cloudfront describe-function --name "$FN" --query ETag --output text 2>/dev/null); then
  ETAG=$(t aws cloudfront update-function --name "$FN" --if-match "$ETAG" \
    --function-config "$FN_CONFIG" --function-code fileb://fn.rendered.js --query ETag --output text)
else
  ETAG=$(t aws cloudfront create-function --name "$FN" \
    --function-config "$FN_CONFIG" --function-code fileb://fn.rendered.js --query ETag --output text)
fi
rm -f fn.rendered.js
aws cloudfront publish-function --name "$FN" --if-match "$ETAG" >/dev/null
FN_ARN=$(t aws cloudfront describe-function --name "$FN" --stage LIVE \
  --query FunctionSummary.FunctionMetadata.FunctionARN --output text)

step "Attach it to the default (S3) behaviour of $CF_DIST_ID — /api/* is left alone"
DIST_ETAG=$(t aws cloudfront get-distribution-config --id "$CF_DIST_ID" --query ETag --output text)
aws cloudfront get-distribution-config --id "$CF_DIST_ID" --query DistributionConfig --output json \
  | tr -d '\r' \
  | jq --arg arn "$FN_ARN" '.DefaultCacheBehavior.FunctionAssociations =
      {Quantity: 1, Items: [{EventType: "viewer-request", FunctionARN: $arn}]}' > dist.rendered.json
aws cloudfront update-distribution --id "$CF_DIST_ID" --if-match "$DIST_ETAG" \
  --distribution-config file://dist.rendered.json --query Distribution.Status --output text
rm -f dist.rendered.json

step "Deploy role may read the auth stack outputs (CI builds the frontend with them)"
if aws iam get-role --role-name "$DEPLOY_ROLE" >/dev/null 2>&1; then
  aws iam put-role-policy --role-name "$DEPLOY_ROLE" --policy-name read-studeal-auth --policy-document \
    "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":\"cloudformation:DescribeStacks\",\"Resource\":\"arn:aws:cloudformation:$AWS_REGION:$ACCOUNT_ID:stack/$AUTH_STACK/*\"}]}"
fi

step "Rebuild the frontend with the Cognito settings"
S3_BUCKET="$S3_BUCKET" CLOUDFRONT_DISTRIBUTION_ID="$CF_DIST_ID" AUTH_STACK="$AUTH_STACK" \
  bash infra/aws/deploy-frontend.sh

out() {
  t aws cloudformation describe-stacks --stack-name "$AUTH_STACK" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text
}
POOL_ID=$(out UserPoolId)
CLIENT_ID=$(out UserPoolClientId)
ISSUER=$(out Authority)
COGNITO_DOMAIN=$(out CognitoDomain)
GOOGLE_REDIRECT=$(out GoogleRedirectUri)

cat <<TXT

===========================================================================
A3. Cognito values for your teammates:

For Person 2 (Frontend — frontend/.env):
  VITE_COGNITO_ISSUER=$ISSUER
  VITE_COGNITO_CLIENT_ID=$CLIENT_ID
  VITE_COGNITO_DOMAIN=$COGNITO_DOMAIN

For Person 1 (Backend — .env):
  User Pool ID:      $POOL_ID
  COGNITO_ISSUER=$ISSUER
  COGNITO_CLIENT_ID=$CLIENT_ID
===========================================================================

Google OAuth client must have (Google Cloud console → Clients → your Web client):
  Authorised JavaScript origin:  $COGNITO_DOMAIN
  Authorised redirect URI:       $GOOGLE_REDIRECT
Consent screen: External, scopes openid/email/profile only, status "In production".

Site URL:  $SITE_URL
Next:      bash infra/aws/08-api-auth.sh (or make deploy-api-auth)
TXT
