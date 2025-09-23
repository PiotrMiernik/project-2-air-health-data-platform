# OpenAQ monthly
resource "aws_cloudwatch_event_rule" "openaq_schedule" {
  name                = "openaq-monthly"
  schedule_expression = "cron(0 0 4 * ? *)" # 4st day of each month
}

resource "aws_cloudwatch_event_target" "openaq_target" {
  rule      = aws_cloudwatch_event_rule.openaq_schedule.name
  target_id = "OpenAQTarget"
  arn       = aws_sfn_state_machine.orchestration.arn
  role_arn  = aws_iam_role.eventbridge_invoke_stepfn_role.arn
}

# WHO yearly
resource "aws_cloudwatch_event_rule" "who_schedule" {
  name                = "who-yearly"
  schedule_expression = "cron(0 0 5 1 ? *)" # 5th Jan each year
}

resource "aws_cloudwatch_event_target" "who_target" {
  rule      = aws_cloudwatch_event_rule.who_schedule.name
  target_id = "WHOTarget"
  arn       = aws_sfn_state_machine.orchestration.arn
  role_arn  = aws_iam_role.eventbridge_invoke_stepfn_role.arn
}

# Eurostat yearly
resource "aws_cloudwatch_event_rule" "eurostat_schedule" {
  name                = "eurostat-yearly"
  schedule_expression = "cron(0 0 5 1 ? *)"
}

resource "aws_cloudwatch_event_target" "eurostat_target" {
  rule      = aws_cloudwatch_event_rule.eurostat_schedule.name
  target_id = "EurostatTarget"
  arn       = aws_sfn_state_machine.orchestration.arn
  role_arn  = aws_iam_role.eventbridge_invoke_stepfn_role.arn
}

# ECDC monthly
resource "aws_cloudwatch_event_rule" "ecdc_schedule" {
  name                = "ecdc-monthly"
  schedule_expression = "cron(0 0 6 * ? *)" # 6th of each month
}

resource "aws_cloudwatch_event_target" "ecdc_target" {
  rule      = aws_cloudwatch_event_rule.ecdc_schedule.name
  target_id = "ECDCTarget"
  arn       = aws_sfn_state_machine.orchestration.arn
  role_arn  = aws_iam_role.eventbridge_invoke_stepfn_role.arn
}
