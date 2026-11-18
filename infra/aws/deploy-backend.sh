#!/usr/bin/env bash
set -euo pipefail
export MSYS_NO_PATHCONV=1

: "${AWS_REGION:?}" "${ECR_REPOSITORY:?}"
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse HEAD)}"

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text | tr -d '\r')
REGISTRY="$ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
IMAGE="$REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG"

echo "==> Staging docs/data/*.csv into backend/seed_data for image build"
rm -rf backend/seed_data
cp -r docs/data backend/seed_data
trap 'rm -rf backend/seed_data' EXIT

echo "==> Logging in to $REGISTRY"
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$REGISTRY"

echo "==> Building $IMAGE"
docker build --platform linux/amd64 --provenance=false -t "$IMAGE" backend

echo "==> Pushing $IMAGE"
docker push "$IMAGE"

IMAGE="$IMAGE" bash "$(dirname "$0")/release-backend.sh"
