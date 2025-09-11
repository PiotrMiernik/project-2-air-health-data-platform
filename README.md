# Project 2 – Air Quality and Health Data Platform

This project is an **end-to-end data engineering pipeline** built around a modern **data lakehouse architecture** on AWS using dbt and Python. It integrates air quality and public health data from multiple trusted sources and transforms them into structured, queryable datasets ready for analysis and sharing.

---

## Project Overview

The main goal is to design and implement a complete data platform that:

- Collects air quality and disease-related data from public APIs (OpenAQ, WHO, ECDC)
- Loads raw data into a **data lake** on Amazon S3 (Bronze layer)
- Catalogs data using AWS Glue and exposes it in Athena
- Transforms data through versioned dbt models (Silver and Gold layers)
- Validates and tests code and data via automated CI/CD
- Publishes data for reuse through AWS Athena or AWS Data Exchange

---

## Key Features

- **Lakehouse architecture** using S3 + Glue + Athena + dbt
- **ELT workflow** with modular Python ingestion and dbt transformations
- **Layered modeling**: Bronze → Silver → Gold
- **CI/CD pipelines** with GitHub Actions (Python + dbt)
- **Automated testing**:
  - Python unit tests for ingestion and helper functions
  - Data validation logic (nulls, types, schema)
  - dbt tests (`not_null`, `unique`, etc.)
- Designed for **data sharing** with analysts, researchers, and policymakers

---

## Repository Structure

project2-air-health-trends/

├── ingestion/                  # Python scripts for downloading data

│   ├── download_openaq.py

│   ├── download_who.py

│   ├── download_ecdc.py

│   └── download_eurostat.py

├── dbt/                        # dbt project (Athena backend)

│   ├── models/

│   │   ├── bronze/             # Raw staging from S3

│   │   ├── silver/             # Cleaned / normalized

│   │   └── gold/               # Analytical business logic

│   ├── tests/                  # dbt schema tests

│   ├── macros/                 # Reusable Jinja functions

│   ├── snapshots/              # (Optional) slowly changing dimensions

│   ├── dbt_project.yml		# core configuration

│   └── profiles.yml            # dbt profile (local or CI secret)

├── terraform/                  # Terraform folder for project infrastructure definition and managment (IaC approach)

│   ├── athena.tf		# Configures Athena settings, such as query result location in S3

│   ├── glue.tf		# Provisions Glue Data Catalog database and crawlers for schema discovery

│   ├── s3.tf		# Creates the S3 data lake structure (bronze/silver/gold/public/query-results)

│   ├── stepfunction.tf		# Defines Step Functions state machines for orchestrating ingestion workflows

│   ├── iam.tf		# Sets up IAM roles and policies for Lambda, CI/CD, and Step Functions

│   └── main.tf		# Optional central file to coordinate module loading or key resources

│   ├── outputs.tf		# Specifies which output values (e.g. bucket ARN, IAM role name) should be printed after apply

│   ├── providers.tf	# Defines the required providers (e.g. AWS) and their versions

│   ├── variables.tf		# Declares input variables used across all modules (e.g. region, bucket name)

│   └── terraform.tfvars.example		# Example values for variables – used locally or in CI (do not commit real values)

│   └── README.md		# Usage instructions for initializing and deploying infrastructure with Terraform

├── tests/                      # Unit tests for ingestion and utils

│   ├── test_download_openaq.py

│   ├── test_download_ecdc.py

│   ├── test_download_who.py

│   ├── test_download_eurostat.py

│   ├── test_s3_utils.py

├── config/                 # env. variables for local tests and development

│   └── .env

├── docs/                 # documentation files and diagrams for the project.

│   └── architecture.png

│   └── sources.md

├── orchestration/              # AWS Step Functions definition

│   └── step_function_definition.json

├── utils/                      # Helper functions

│   └── s3_utils.py

├── .github/workflows/          # CI/CD automation

│   ├── run-tests.yml           # Python tests + validation

│   └── dbt-build.yml           # dbt build + test on push/PR

│   └── deploy-lambda.yml           # AWS lambda function for data ingestion

├── data/                       # (Optional) local sample data

├── requirements.txt            # Python dependencies

├── .gitignore                  # Files and folders to exclude from Git

└── README.md

## Technologies Used

- **Python 3.11+** – ingestion scripts, validation, testing
- **AWS S3** – raw and processed data storage
- **AWS Glue** – automatic schema inference and Data Catalog
- **AWS Athena** – querying data with SQL over S3
- **dbt** – transformation logic, testing, documentation
- **GitHub Actions** – CI/CD pipelines for Python and dbt
- **AWS Step Functions** – orchestration of ingestion workflows
- **AWS Data Exchange** – data sharing platform for publishing datasets

## CI/CD Workflows

| File                                    | What it does                                         |
| --------------------------------------- | ---------------------------------------------------- |
| `.github/workflows/run-tests.yml`     | Runs `pytest` for ingestion scripts and utils      |
| `.github/workflows/dbt-build.yml`     | Runs `dbt build` and `dbt test` on model changes |
| `.github/workflows/deploy-lambda.yml` | Runs data ingestion scripts                          |

CI/CD is triggered automatically on every push or pull request to the `dev` and `main` branches.

---

## Testing and Validation Strategy

- Unit tests for Python ingestion scripts (e.g., API response, structure, nulls)
- Mocked tests for S3 upload logic using `boto3`
- dbt schema tests (`not_null`, `unique`, `accepted_values`)
- All tests are automatically executed in CI pipelines

Tests are written **during development**, and **automated during project stage 4** via GitHub Actions.

---

## Output & Data Sharing

The final datasets from the `gold` layer are:

- Stored in Parquet or CSV format
- Available for querying via AWS Athena
- Shared through public S3 buckets or published as a **data product** on **AWS Data Exchange**

---

## License

This project is licensed under the terms of the [LICENSE](./LICENSE) file.

---

Created by **Piotr Miernik – 2025**
