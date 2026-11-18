#!/usr/bin/env bash
# A1. Create a monthly AWS cost budget alert so you get an email before unexpected charges.
# Usage: bash infra/aws/00-budget.sh your-email@ucu.edu.ua [limit-usd]
source "$(dirname "$0")/env.sh"

EMAIL="${1:-${BUDGET_EMAIL:-}}"
LIMIT="${2:-${BUDGET_LIMIT_USD:-5}}"
if [[ -z "$EMAIL" ]]; then
  echo "Usage: bash infra/aws/00-budget.sh <your-email> [monthly-limit-usd]"
  exit 1
fi

BUDGET_NAME="studeal-monthly-budget"
step "Creating/updating monthly budget $BUDGET_NAME ($LIMIT USD) for $EMAIL"

if aws budgets describe-budget --account-id "$ACCOUNT_ID" --budget-name "$BUDGET_NAME" >/dev/null 2>&1; then
  echo "   (budget $BUDGET_NAME already exists)"
else
  aws budgets create-budget \
    --account-id "$ACCOUNT_ID" \
    --budget "{\"BudgetName\":\"$BUDGET_NAME\",\"BudgetLimit\":{\"Amount\":\"$LIMIT\",\"Unit\":\"USD\"},\"TimeUnit\":\"MONTHLY\",\"BudgetType\":\"COST\"}" \
    --notifications-with-subscribers "[
      {\"Notification\":{\"NotificationType\":\"ACTUAL\",\"ComparisonOperator\":\"GREATER_THAN\",\"Threshold\":80,\"ThresholdType\":\"PERCENTAGE\"},\"Subscribers\":[{\"SubscriptionType\":\"EMAIL\",\"Address\":\"$EMAIL\"}]},
      {\"Notification\":{\"NotificationType\":\"FORECASTED\",\"ComparisonOperator\":\"GREATER_THAN\",\"Threshold\":100,\"ThresholdType\":\"PERCENTAGE\"},\"Subscribers\":[{\"SubscriptionType\":\"EMAIL\",\"Address\":\"$EMAIL\"}]}
    ]"
  echo "Budget alert created ($LIMIT USD/month -> $EMAIL)."
fi
echo "Done. Next: bash infra/aws/01-network.sh"
