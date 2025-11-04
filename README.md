# Project 2 – Air Quality and Health Data Platform


![Tests](https://github.com/PiotrMiernik/project-2-air-health-data-platform/actions/workflows/run-tests.yml/badge.svg)

![dbt build](https://github.com/PiotrMiernik/project-2-air-health-data-platform/actions/workflows/dbt-build.yml/badge.svg)

![Lambda
Deploy](https://github.com/PiotrMiernik/project-2-air-health-data-platform/actions/workflows/deploy-lambda.yml/badge.svg)

This project is an **end-to-end data pipeline** built around a modern **data lakehouse architecture** on AWS (S3, Glue, Athena) using dbt and Python. It integrates air quality and public health data from multiple trusted sources and transforms them into structured, queryable datasets ready for analysis and sharing.

---

## Project Overview

The main goal is to design and implement a complete data platform that:

- Collects air quality and disease-related data from public APIs (OpenAQ, WHO, ECDC, Eurostat)
- Loads raw data into a **data lake** on Amazon S3 (Bronze layer)
- Transforms json files (parse and flatten) into parquet format with AWS Glue Jobs (Silver layer)
- Catalogs data using AWS Glue in Silver layer and exposes it in Athena
- Transforms data through versioned dbt models (Gold layer)
- Validates and tests code and data via automated CI/CD
- Publishes data for reuse through AWS Athena

---

## Key Features

- **Lakehouse architecture** using S3 + Glue + Athena + dbt
- **ELT workflow** with modular Python ingestion, AWS Glue Jobs and dbt transformations
- **Layered modeling**: Bronze → Silver → Gold
- **CI/CD pipelines** with GitHub Actions (Python + dbt)
- **Automated testing**:
  - Python unit tests for ingestion
  - Data validation logic (nulls, types, schema)
  - dbt tests (`not_null`, `unique`, etc.)
- Designed for **data sharing** with analysts, researchers, and policymakers

---

## Repository Structure

project2-air-health-trends/

├── .github/workflows/          # CI/CD automation

│   ├── run-tests.yml           # Python tests + validation

│   └── dbt-build.yml           # dbt build + test on push/PR

│   └── deploy-lambda.yml           # AWS lambda function for data ingestion

├── .venv/                 # Python virtual environment

├── docs/                 # documentation files and diagrams for the project

│   └── architecture.png

│   └── sources.md

│   └── dbt-dag.png

│   └── stepfunction_graph.png

├── dbt/                        # dbt project (Athena backend)

│   ├── models/

│   │   ├── silver/             # Cleaned / normalized

│   │   │   ├── sources.yml		# Data sources from the silver layer registered in AWS Glue

│   │   └── gold/               # Analytical business logic

│   │   │   ├── dim_country.sql

│   │   │   ├── dim_year.sql

│   │   │   ├── fact_air_health.sql

│   ├── tests/                  # Data quality and integrity checks

│   ├── macros/                 # Reusable Jinja functions

│   ├── seeds/              # Static reference data for dbt

│   ├── dbt_project.yml		# core configuration

│   └── profiles.yml            # dbt connection and target configuration

├── glue/                  # AWS Glue jobs scripts for bronze - silver transformations

│   ├── project-2-ecdc-job.py

│   ├── project-2-eurostat-job.py

│   ├── project-2-openaq-job.py

│   └── project-2-who-job.py

├── ingestion/                  # Python scripts for downloading data from API

│   ├── download_openaq.py

│   ├── download_who.py

│   ├── download_ecdc.py

│   └── download_eurostat.py

├── lambda_build/                  # Deployment packages for AWS Lambda functions

│   ├── download_openaq.py

│   ├── download_who.py

│   ├── download_ecdc.py

│   └── download_eurostat.py

├── orchestration/              # AWS Step Functions definition

│   └── step_function_definition.json

├── terraform/                  # Terraform folder for project infrastructure definition and managment (IaC approach)

│   ├── athena.tf		# Configures Athena settings, such as query result location in S3

│   ├── cloudwatch.tf		# Create the main CloudWatch Dashboard for the project

│   ├── eventbridge.tf		# Terraform configuration for EventBridge scheduling

│   ├── glue.tf		# Provisions Glue Data Catalog database, jobs and crawlers for schema discovery

│   ├── iam.tf		# Sets up IAM roles and policies for AWS resources

│   ├── lambda.tf		# Terraform configuration for AWS Lambda functions

│   ├── outputs.tf		# Specifies which output values (e.g. bucket ARN, IAM role name) should be printed after apply

│   ├── providers.tf	# Defines the required providers (e.g. AWS) and their versions

│   ├── s3.tf		# Creates the S3 data lake structure (bronze/silver/gold/public/query-results)

│   ├── stepfunction.tf		# Defines Step Functions state machines for orchestrating ingestion workflows

│   ├── variables.tf		# Declares input variables used across all modules (e.g. region, bucket name)

│   └── terraform.tfvars		# Values for variables – used locally or in CI (do not commit real values)

├── tests/                      # Unit tests for ingestion

│   ├── test_download_openaq.py

│   ├── test_download_ecdc.py

│   ├── test_download_who.py

│   ├── test_download_eurostat.py

├── .gitignore                  # Files and folders to exclude from Git

└── README.md

├── requirements-dbt.txt            # dbt dependencies

├── requirements-tests.txt            # Python tests dependencies

## Technologies Used

- **Python 3.11+** – ingestion scripts, validation, testing
- **AWS Lambda** - data ingestion from API
- **AWS S3** – raw and processed data storage
- **AWS Glue** – automatic transformations with Glue Jobs, schema inference with Glue Crawlers and Data Catalog
- **AWS Athena** – querying data with SQL over S3
- **AWS Step Functions** – orchestration of ingestion and Glue transformation workflows
- **AWS CloudWatch -** project dashboard with basic pipeline quality metrics
- **AWS EventBridge** - scheduling trigger for all workflows
- **AWS IAM** - roles and policies for project services
- **dbt** – transformation logic with SQL models, testing, documentation
- **GitHub Actions** – CI/CD pipelines for Python and dbt
- **Terraform** - IaC tool

## CI/CD Workflows

| File                                    | What it does                                         |
| --------------------------------------- | ---------------------------------------------------- |
| `.github/workflows/run-tests.yml`     | Runs `pytest` for ingestion scripts                |
| `.github/workflows/dbt-build.yml`     | Runs `dbt build` and `dbt test` on model changes |
| `.github/workflows/deploy-lambda.yml` | Runs data ingestion scripts                          |

CI/CD is triggered automatically on every push or pull request to the `dev` and `main` branches.

---

## Testing and Validation Strategy

- Unit tests for Python ingestion scripts (e.g., API response, structure, nulls)
- Mocked tests for S3 upload logic using `boto3`
- dbt schema tests (`not_null`, `unique`, `accepted_values`)
- All tests are automatically executed in CI pipelines

Tests are written **during development**, and **automated** via GitHub Actions.

---

## Output & Data Sharing

The final datasets from the `gold` layer are:

- Stored in Parquet format
- Available for querying via AWS Athena
- Ready for sharing or integration through AWS Athena or AWS Data Exchange.

---

## License

This project is licensed under the terms of the [LICENSE](./LICENSE) file.

Created by **Piotr Miernik – 2025**
