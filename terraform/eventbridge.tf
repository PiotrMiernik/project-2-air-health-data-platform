# Yearly orchestration trigger for all sources
resource "aws_cloudwatch_event_rule" "air_health_platform_schedule" {
  name                = "air-health-platform-yearly"
  description         = "Trigger the Air Health Data Platform orchestration yearly on Jan 5th, every hour"
  schedule_expression = "cron(0 0 5 1 ? *)" 
}

resource "aws_cloudwatch_event_target" "air_health_platform_target" {
  rule      = aws_cloudwatch_event_rule.air_health_platform_schedule.name
  target_id = "AirHealthDataPlatformTarget"
  arn       = aws_sfn_state_machine.orchestration.arn
  role_arn  = aws_iam_role.eventbridge_invoke_stepfn_role.arn
}
