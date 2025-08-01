# Project 2 – Air Quality and Health Data Platform

This project is an **end-to-end data engineering pipeline** built around a modern **data lakehouse architecture** on AWS with dbt. It integrates air quality and public health data from multiple authoritative sources and transforms them into structured, queryable datasets ready for analysis and sharing.

## **Project Overview**

The main goal is to design and implement a complete data platform that:

- Collects air quality and disease-related data from public APIs (e.g.
  OpenAQ, WHO, ECDC)
- Loads the raw data into a **data lake** on Amazon S3
- Organizes and transforms the data into curated layers using dbt
  (Bronze → Silver → Gold)
- Enables data analysis and sharing through **AWS Athena** and open data
  publishing
- Automates the workflow via orchestration and CI/CD tools

## **Key Features**

- **Lakehouse architecture** using S3 + Glue + Athena + dbt
- **ELT workflow** using Python: Extract → Load → Transform
- **Versioned transformations** with dbt models and tests
- **CI/CD integration** with GitHub Actions for testing and model
  deployment
- Designed for **data sharing** with researchers, analysts, and policy
  makers

## **Repository Structure**

project-2-air-health-data-platform/

├── ingestion/ # Python scripts for API
ingestion

├── dbt/ # dbt project: models, tests,
macros, snapshots

│ ├──
models/bronze/ # Raw staging models

│ ├──
models/silver/ # Cleaned/normalized models

│ ├── models/gold/Business-level curated models

├── orchestration/ # AWS Step Functions
definitions

├── utils/ # Helper functions (e.g. S3
uploader)

├── .github/workflows/ # CI/CD
pipelines

├── data/ # (Optional) sample local
data

└── README.md

## **Technologies Used**

- **Python 3.11+** – ingestion, S3 upload
- **AWS S3** – data lake storage
- **AWS Glue** – metadata catalog
- **AWS Athena** – SQL querying over S3
- **dbt** – transformations, documentation, testing
- **GitHub Actions** – CI/CD for testing and dbt builds
- **AWS Step Functions** – (optional) orchestration for ELT
- **AWS Data Exchange** - data sheering platform

## **CI/CD Workflows**

.github/workflows/run-tests.yml: Unit tests for ingestion and
transformation scripts

.github/workflows/dbt-build.yml: Automated dbt model builds and tests

## **Output & Data Sharing**

The final output (Gold models) is available as structured datasets via AWS Athena and designed to be shared through open data shering platforms such
as AWS Data Exchange or public S3 buckets.

## **License**

This project is licensed under the terms of the LICENSE file.

Created by Piotr Miernik – 2025.
