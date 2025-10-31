# Create the main CloudWatch Dashboard for the project
resource "aws_cloudwatch_dashboard" "project_2_dashboard" {
  dashboard_name = "project-2-dashboard"

  # JSON definition of the dashboard widgets
  dashboard_body = jsonencode({
    start = "-PT3H" # Last 3 hours
    widgets = [
      # 1. Widget: Execution metrics for all 4 Lambda functions
      {
        type   = "metric",
        height = 6,
        width  = 12,
        y      = 0,
        x      = 0,
        properties = {
          title = "Lambda Ingestion Successes (Count)",
          view  = "timeSeries",
          stacked = false,
          metrics = [
            ["AWS/Lambda", "Invocations", "FunctionName", "project2-who-lambda", { "label": "WHO" }],
            ["AWS/Lambda", "Invocations", "FunctionName", "project2-eurostat-lambda", { "label": "Eurostat" }],
            ["AWS/Lambda", "Invocations", "FunctionName", "project2-ecdc-lambda", { "label": "ECDC" }],
            ["AWS/Lambda", "Invocations", "FunctionName", "project2-openaq-lambda", { "label": "OpenAQ" }]
          ],
          region = "eu-central-1"
        }
      },
      # 2. Widget: Execution duration for Glue Jobs
      {
        type   = "metric",
        height = 6,
        width  = 12,
        y      = 0,
        x      = 12,
        properties = {
          title = "Glue Job Run Time (Max)",
          view  = "timeSeries",
          stacked = false,
          metrics = [
            ["AWS/Glue", "Duration", "JobName", "project-2-who-job", { "stat": "Maximum", "label": "WHO Job" }],
            ["AWS/Glue", "Duration", "JobName", "project-2-ecdc-job", { "stat": "Maximum", "label": "ECDC Job" }],
            ["AWS/Glue", "Duration", "JobName", "project-2-eurostat-job", { "stat": "Maximum", "label": "Eurostat Job" }],
            ["AWS/Glue", "Duration", "JobName", "project-2-openaq-job", { "stat": "Maximum", "label": "OpenAQ Job" }]
          ],
          region = "eu-central-1",
          period = 300 # 5 minutes
        }
      },
      # 3. Widget: Lambda function errors
      {
        type   = "metric",
        height = 6,
        width  = 12,
        y      = 6,
        x      = 0,
        properties = {
          title = "Lambda Errors (Sum)",
          view  = "timeSeries",
          stacked = true,
          metrics = [
            ["AWS/Lambda", "Errors", "FunctionName", "project2-who-lambda", { "label": "WHO", "stat": "Sum" }],
            ["AWS/Lambda", "Errors", "FunctionName", "project2-eurostat-lambda", { "label": "Eurostat", "stat": "Sum" }],
            ["AWS/Lambda", "Errors", "FunctionName", "project2-ecdc-lambda", { "label": "ECDC", "stat": "Sum" }],
            ["AWS/Lambda", "Errors", "FunctionName", "project2-openaq-lambda", { "label": "OpenAQ", "stat": "Sum" }]
          ],
          region = "eu-central-1"
        }
      },
      # 4. Widget: Glue Job execution status (Failed Runs)
      {
        type   = "metric",
        height = 6,
        width  = 12,
        y      = 6,
        x      = 12,
        properties = {
          title = "Glue Job Failures (Count)",
          view  = "timeSeries",
          stacked = true,
          metrics = [
            ["AWS/Glue", "FailedRuns", "JobName", "project-2-who-job", { "label": "WHO Job", "stat": "Sum" }],
            ["AWS/Glue", "FailedRuns", "JobName", "project-2-ecdc-job", { "label": "ECDC Job", "stat": "Sum" }],
            ["AWS/Glue", "FailedRuns", "JobName", "project-2-eurostat-job", { "label": "Eurostat Job", "stat": "Sum" }],
            ["AWS/Glue", "FailedRuns", "JobName", "project-2-openaq-job", { "label": "OpenAQ Job", "stat": "Sum" }]
          ],
          region = "eu-central-1",
          period = 300
        }
      },
      # 5. Widget: Table with the status of the last Crawler run
      {
        type   = "metric",
        height = 3,
        width  = 24,
        y      = 12,
        x      = 0,
        properties = {
          title = "Glue Crawler Status (Last Run)",
          view  = "table",
          metrics = [
            ["AWS/Glue", "LastCrawlDuration", "CrawlerName", "crawler-who-silver", { "stat": "Maximum", "label": "WHO Crawler" }],
            ["AWS/Glue", "LastCrawlDuration", "CrawlerName", "crawler-ecdc-silver", { "stat": "Maximum", "label": "ECDC Crawler" }],
            ["AWS/Glue", "LastCrawlDuration", "CrawlerName", "crawler-eurostat-silver", { "stat": "Maximum", "label": "Eurostat Crawler" }],
            ["AWS/Glue", "LastCrawlDuration", "CrawlerName", "crawler-openaq-silver", { "stat": "Maximum", "label": "OpenAQ Crawler" }]
          ],
          region = "eu-central-1",
          period = 86400 # 1 day
        }
      }
    ]
  })
}