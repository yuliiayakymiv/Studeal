#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
LOG="infra/aws/setup.log"
exec > >(tee -a "$LOG") 2>&1
echo "===== $(date) ====="

for s in 01-network 02-database 03-image 04-ecs 05-frontend 06-oidc 07-auth 08-api-auth; do
  echo; echo "############ $s ############"
  bash "infra/aws/$s.sh"
done
echo; echo "ALL DONE. Verify your CloudFront URL printed above."
