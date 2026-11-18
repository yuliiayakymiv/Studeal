#!/usr/bin/env bash
# Shared settings for the one-time setup scripts 00-…08-. Sourced, not run.
set -euo pipefail
export MSYS_NO_PATHCONV=1
export AWS_PAGER=""
export AWS_REGION="${AWS_REGION:-eu-central-1}"
export AWS_DEFAULT_REGION="$AWS_REGION"

export GITHUB_REPO="${GITHUB_REPO:-yuliiayakymiv/Studeal}"
export ECR_REPOSITORY=studeal-backend ECS_CLUSTER=studeal ECS_SERVICE=studeal-backend
export ECS_TASK_FAMILY=studeal-backend CONTAINER_NAME=studeal-backend
export DB_INSTANCE=studeal-db DB_NAME=studeal DB_USER=studeal
export EXEC_ROLE=studeal-ecs-task-execution DEPLOY_ROLE=studeal-github-deploy
export AUTH_STACK="${AUTH_STACK:-studeal-auth}"

STATE_FILE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.state"
[[ -f "$STATE_FILE" ]] && source "$STATE_FILE"

t() { "$@" | tr -d '\r'; }

save() {
  touch "$STATE_FILE"
  grep -v "^$1=" "$STATE_FILE" > "$STATE_FILE.tmp" || true
  printf '%s="%s"\n' "$1" "$2" >> "$STATE_FILE.tmp"
  mv "$STATE_FILE.tmp" "$STATE_FILE"
  export "$1=$2"
}

step() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }

ACCOUNT_ID=$(t aws sts get-caller-identity --query Account --output text)
export ACCOUNT_ID
export REGISTRY="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
echo "AWS account $ACCOUNT_ID, region $AWS_REGION"
