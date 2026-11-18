#!/usr/bin/env bash
source "$(dirname "$0")/env.sh"
: "${SUBNETS_CSV:?run 01-network.sh first}" "${SG_ECS:?run 01-network.sh first}"

step "Running one-off ECS task on $ECS_CLUSTER to migrate and seed RDS"
TASK_ARN=$(t aws ecs run-task \
  --cluster "$ECS_CLUSTER" \
  --task-definition "$ECS_TASK_FAMILY" \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[$SUBNETS_CSV],securityGroups=[$SG_ECS],assignPublicIp=ENABLED}" \
  --overrides "{\"containerOverrides\":[{\"name\":\"$CONTAINER_NAME\",\"command\":[\"sh\",\"-c\",\"alembic upgrade head && python -m app.seed\"]}]}" \
  --query 'tasks[0].taskArn' --output text)

echo "   Task started: $TASK_ARN"
step "Waiting for seed task to complete…"
aws ecs wait tasks-stopped --cluster "$ECS_CLUSTER" --tasks "$TASK_ARN"
EXIT_CODE=$(t aws ecs describe-tasks --cluster "$ECS_CLUSTER" --tasks "$TASK_ARN" \
  --query 'tasks[0].containers[0].exitCode' --output text)
if [[ "$EXIT_CODE" != "0" ]]; then
  echo "Seed task failed with exit code $EXIT_CODE. Check CloudWatch logs /ecs/$ECS_SERVICE."
  exit 1
fi
echo "RDS migration and seed succeeded (exit code 0)."
