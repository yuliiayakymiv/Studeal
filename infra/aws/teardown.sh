#!/usr/bin/env bash
source "$(dirname "$0")/env.sh"
read -r -p "Delete ALL Studeal resources in $AWS_REGION (account $ACCOUNT_ID)? Type 'delete': " ok
[[ "$ok" == "delete" ]] || { echo "Cancelled."; exit 1; }
try() { "$@" >/dev/null 2>&1 && echo "   ok: $*" || echo "   skip: $*"; }

step "Cognito auth stack (user pool, app client, domain)"
try aws cloudformation delete-stack --stack-name "${AUTH_STACK:-studeal-auth}"
try aws iam delete-role-policy --role-name "$DEPLOY_ROLE" --policy-name read-studeal-auth
step "ECS service and cluster"
try aws ecs update-service --cluster "$ECS_CLUSTER" --service "$ECS_SERVICE" --desired-count 0
try aws ecs delete-service --cluster "$ECS_CLUSTER" --service "$ECS_SERVICE" --force
step "Load balancer and target group"
[[ -n "${ALB_ARN:-}" ]] && try aws elbv2 delete-load-balancer --load-balancer-arn "$ALB_ARN"
sleep 20
[[ -n "${TG_ARN:-}" ]] && try aws elbv2 delete-target-group --target-group-arn "$TG_ARN"
try aws ecs delete-cluster --cluster "$ECS_CLUSTER"
step "Database (no final snapshot)"
try aws rds delete-db-instance --db-instance-identifier "$DB_INSTANCE" --skip-final-snapshot --delete-automated-backups
step "ECR repository and S3 bucket"
try aws ecr delete-repository --repository-name "$ECR_REPOSITORY" --force
[[ -n "${S3_BUCKET:-}" ]] && try aws s3 rb "s3://$S3_BUCKET" --force
step "SSM parameters, log group"
try aws ssm delete-parameters --names /studeal/DATABASE_URL /studeal/DB_PASSWORD /studeal/SMTP_PASSWORD
try aws logs delete-log-group --log-group-name "/ecs/$ECS_SERVICE"
step "IAM roles"
try aws iam delete-role-policy --role-name "$DEPLOY_ROLE" --policy-name deploy-studeal
try aws iam delete-role --role-name "$DEPLOY_ROLE"
try aws iam delete-role-policy --role-name "$EXEC_ROLE" --policy-name read-studeal-ssm
try aws iam detach-role-policy --role-name "$EXEC_ROLE" --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
try aws iam delete-role --role-name "$EXEC_ROLE"
cat <<TXT

Left for you to do by hand (they can't be deleted instantly):
 - CloudFront ${CF_DIST_ID:-}: console → CloudFront → Disable → wait ~10 min → Delete
 - CloudFront Function studeal-spa-routes: delete after the distribution is gone
 - Security groups studeal-alb / studeal-ecs / studeal-rds: EC2 → Security Groups → delete
   (after the database has finished deleting, ~10 min)
TXT
