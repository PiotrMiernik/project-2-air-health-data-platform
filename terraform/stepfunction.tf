resource "aws_sfn_state_machine" "orchestration" {
  name     = "project2-orchestration"
  role_arn = aws_iam_role.stepfunction_exec_role.arn
  definition = file("${path.module}/../orchestration/step_function_definition.json")
}