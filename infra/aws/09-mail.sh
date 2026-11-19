#!/usr/bin/env bash
# Studeal+ emails: give the ECS task an SMTP account (Gmail by default) and roll the service.
# Needs in the repo-root .env (git-ignored, never committed):
#   SMTP_USER=studeal.lviv@gmail.com   SMTP_PASSWORD=<Gmail app password>   (optional: SMTP_HOST, SMTP_PORT)
# The password goes to SSM Parameter Store (/studeal/SMTP_PASSWORD, SecureString), not into the task definition.
source "$(dirname "$0")/env.sh"
cd "$(dirname "$0")/../.."

envval() { grep -E "^$1=" .env 2>/dev/null | tail -1 | cut -d= -f2- | tr -d '\r"' || true; }
SMTP_HOST="${SMTP_HOST:-$(envval SMTP_HOST)}"; SMTP_HOST="${SMTP_HOST:-smtp.gmail.com}"
SMTP_PORT="${SMTP_PORT:-$(envval SMTP_PORT)}"; SMTP_PORT="${SMTP_PORT:-587}"
SMTP_USER="${SMTP_USER:-$(envval SMTP_USER)}"
SMTP_PASSWORD="${SMTP_PASSWORD:-$(envval SMTP_PASSWORD)}"
: "${SMTP_USER:?set SMTP_USER in .env}" "${SMTP_PASSWORD:?set SMTP_PASSWORD in .env (Gmail app password)}"
SITE_URL="https://${CF_DOMAIN:?run 05-frontend.sh first}"

step "SSM: /studeal/SMTP_PASSWORD (SecureString)"
aws ssm put-parameter --name /studeal/SMTP_PASSWORD --type SecureString --overwrite \
  --value "$SMTP_PASSWORD" --query Version --output text

step "New task definition revision of $ECS_TASK_FAMILY with SMTP settings"
TMP="infra/aws/.taskdef.rendered.json"
PARAM_ARN="arn:aws:ssm:$AWS_REGION:$ACCOUNT_ID:parameter/studeal/SMTP_PASSWORD"
aws ecs describe-task-definition --task-definition "$ECS_TASK_FAMILY" --query taskDefinition --output json \
  | tr -d '\r' \
  | jq --arg NAME "$CONTAINER_NAME" --arg HOST "$SMTP_HOST" --arg PORT "$SMTP_PORT" \
       --arg USER "$SMTP_USER" --arg FROM "Studeal <$SMTP_USER>" --arg SITE "$SITE_URL" --arg PW "$PARAM_ARN" '
      def drop($names): [.[] | select(.name as $n | $names | index($n) | not)];
      .containerDefinitions |= map(if .name == $NAME then
          .environment = ((.environment // []) | drop(["SMTP_HOST","SMTP_PORT","SMTP_USER","MAIL_FROM","SITE_URL"]))
            + [{name: "SMTP_HOST", value: $HOST}, {name: "SMTP_PORT", value: $PORT},
               {name: "SMTP_USER", value: $USER}, {name: "MAIL_FROM", value: $FROM},
               {name: "SITE_URL", value: $SITE}]
          | .secrets = ((.secrets // []) | drop(["SMTP_PASSWORD"]))
            + [{name: "SMTP_PASSWORD", valueFrom: $PW}]
        else . end)
      | del(.taskDefinitionArn, .revision, .status, .requiresAttributes,
            .compatibilities, .registeredAt, .registeredBy)' > "$TMP"
ARN=$(t aws ecs register-task-definition --cli-input-json "file://$TMP" \
  --query taskDefinition.taskDefinitionArn --output text)
rm -f "$TMP"
echo "   $ARN"

step "Roll $ECS_SERVICE and wait until it is healthy (a few minutes)"
aws ecs update-service --cluster "$ECS_CLUSTER" --service "$ECS_SERVICE" \
  --task-definition "$ARN" --query service.serviceName --output text
aws ecs wait services-stable --cluster "$ECS_CLUSTER" --services "$ECS_SERVICE"

cat <<TXT

Studeal+ emails are on (from $SMTP_USER via $SMTP_HOST:$SMTP_PORT).
Check: on $SITE_URL/subscription pay (demo), add "Aroma" → an email arrives within a minute.
Errors: aws logs tail /ecs/studeal-backend --since 10m | grep -i mail
TXT
