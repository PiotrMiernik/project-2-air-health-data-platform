# Data Sources Overview

This document provides an overview of the external data sources used in the **Air Quality and Health Data Platform**. All sources are publicly available and will be programmatically accessed using AWS Lambda and stored in Amazon S3 in the `bronze` layer. Only data related to european countries will be ingested.

---

---

## 1. OpenAQ – Air Quality Measurements

- **Website:** [https://openaq.org](https://openaq.org)
- **API Docs:** [https://docs.openaq.org](https://docs.openaq.org)
- **Access:** Requires API key (v3)
- **Format:** JSON

* **Granularity:**

  * Spatial: Monitoring station level, filtered to selected major cities in each EU country
  * Temporal: Hourly raw measurements
* **Selected Parameters:** PM2.5
* **Update Frequency:** Hourly, depending on station availability
* **Coverage Period in this project:** From ~2015 to ~2025
* **Usage in Project:**

  * Hourly measurements are collected from the **most representative sensors** in major EU cities (1–3 per country, depending on country size and data availability)
  * Two pollutants relevant for public health and respiratory diseases (PM2.5) are included
  * Data is ingested and stored in the **bronze layer** on S3 in JSON format, and later processed with AWS Glue, Athena, and dbt as part of the data lakehouse pipeline

## 2. WHO – World Health Statistics

- **Website:** [https://www.who.int/data/gho](https://www.who.int/data/gho)
- **API Docs:** [https://www.who.int/data/gho/info/gho-odata-api](https://www.who.int/data/gho/info/gho-odata-api)
- **Access:** Public (OData API)
- **Format:** JSON (OData v4.0)
- **Granularity:**
  - Spatial: Country-level (no city-level data)
  - Temporal: Yearly
- **Indicators Used:**
  * `AIR_10`: Ambient air pollution attributable DALYs per 100 000 children under 5
  * `AIR_12`: Household air pollution attributable deaths in children under 5
  * `AIR_15`: Household air pollution attributable DALYs
  * `AIR_16`: Household air pollution attributable DALYs in children under 5
  * `AIR_35`: Joint effects of air pollution attributable deaths
  * `AIR_42`: Ambient air pollution attributable death rate (per 100 000, age-standardized)
  * `AIR_46`: YLLs attributable to ambient air pollution (age-standardized)
  * `AIR_6`: Ambient air pollution attributable deaths per 100 000 children under 5
  * `AIR_60`: Household and ambient air pollution attributable DALYs
  * `AIR_62`: Household and ambient air pollution attributable DALYs (per 100 000, age-standardized)
  * `TOTENV_3`: DALYs attributable to the environment
- **Update Frequency:** Annual or biannual
- **Coverage Period:** From ~2000 to ~2023 (varies per indicator)
- **Usage in Project:**
  * Health outcome indicators at the national level with direct links to air pollution
  * Focus on mortality, DALYs, and YLLs for respiratory and environment-related diseases
  * Data used for long-term analysis and correlation with air quality and environmental trends

## 3. ECDC – European Centre for Disease Prevention and Control

* **Website:** [https://www.ecdc.europa.eu/en/publications-data](https://www.ecdc.europa.eu/en/publications-data)
* **API (COVID-19 cases and deaths):** [https://opendata.ecdc.europa.eu/covid19/nationalcasedeath/json/](https://opendata.ecdc.europa.eu/covid19/nationalcasedeath/json/)
* **Access:** Public
* **Format:** JSON (CSV also available)
* **Granularity:**

  * Spatial: Country-level (EU/EEA + selected other countries)
  * Temporal: Daily records aggregated to weekly reporting
* **Key Topics:**

  * Confirmed COVID-19 cases and deaths by country
  * Basis for monitoring short-term epidemiological trends
* **Update Frequency:** Weekly
* **Coverage Period:** From 2020 to present
* **Usage in Project:**

  * Core dataset for respiratory infection trends (COVID-19)
  * Focused on EU countries (subset of the dataset)
  * Stored in **bronze** as raw JSON, transformed to Parquet in **silver** for optimized querying via Glue/Athena/dbt

## 4. Eurostat – European Health and Environment Statistics

* **Website:** [https://ec.europa.eu/eurostat](https://ec.europa.eu/eurostat)
* **API Docs:** [https://ec.europa.eu/eurostat/web/json-and-unicode-web-services](https://ec.europa.eu/eurostat/web/json-and-unicode-web-services)
* **Access:** Public
* **Format:** JSON (JSON-stat 2.0), CSV, TSV
* **Granularity:**

  * Spatial: Country and NUTS-1/2/3 regional levels
  * Temporal: Yearly (some datasets offer quarterly/monthly updates)
* **Relevant Datasets (used in project):**

  * `hlth_cd_aro`: Deaths from respiratory diseases
  * `env_air_gge`: Greenhouse gas emissions
  * `nama_10_pc`: GPD per capita (PPS)
  * `ilc_mdho06a`: Severe housing deprivation rate
* **Update Frequency:** Yearly
* **Coverage Period:** From ~2000 to ~2023
* **Usage in Project:**

  * High-quality, standardized health and environmental indicators relevant to air quality and respiratory health
  * Complements WHO data with additional environmental and regional granularity (NUTS-2)
  * Stored in the **bronze** layer as raw JSON; transformed into Parquet in **silver** layer for efficient querying and modeling
  * **NOTE on Gold Layer:** While ingested, Eurostat data is **currently excluded from the final dbt Gold/Marts star schema** (`fact_air_health`) for core analytical simplicity. It remains available in the Silver layer for ad-hoc analysis and future modeling.
