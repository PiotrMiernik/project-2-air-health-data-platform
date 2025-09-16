# Data Sources Overview

This document provides an overview of the external data sources used in the **Air Quality and Health Data Platform**. All sources are publicly available and will be programmatically accessed using AWS Lambda and stored in Amazon S3 in the `bronze` layer. Only data related to **EU-27 countries** will be ingested.

---

## 1. OpenAQ – Air Quality Measurements

- **Website:** [https://openaq.org](https://openaq.org)
- **API Docs:** [https://docs.openaq.org](https://docs.openaq.org)
- **Access:** Public (no authentication required)
- **Format:** JSON
- **Granularity:**
  - Spatial: Station-level, city-level
  - Temporal: Hourly (realtime and historical)
- **Available Parameters:** PM2.5, PM10, NO2, CO, SO2, O3, BC, etc.
- **Update Frequency:** Hourly, depending on location
- **Coverage Period:** From ~2014 to present
- **Usage in Project:**
  - Daily air pollution measurements per 1-10 cities (depending on country))
  - Focus on 10-15 major pollutants (e.g. PM2.5, PM10, NO2)
  - Aggregated to city or country level depending on target dataset

---

## 2. WHO – World Health Statistics

- **Website:** [https://www.who.int/data/gho](https://www.who.int/data/gho)
- **API Docs:** [https://www.who.int/data/gho/info/gho-odata-api](https://www.who.int/data/gho/info/gho-odata-api)
- **Access:** Public (OData API)
- **Format:** JSON (OData v4.0)
- **Granularity:**
  - Spatial: Country-level (no city-level data)
  - Temporal: Yearly
- **Indicators Used:**
  - Mortality from chronic respiratory diseases (MORT_100)
  - Mortality from lower respiratory infections (MORT_101)
  - Lung cancer mortality (MORT_103)
  - DALYs for respiratory diseases
  - Asthma prevalence
- **Update Frequency:** Annual or biannual
- **Coverage Period:** From ~2000 to ~2023 (varies per indicator)
- **Usage in Project:**
  - Health outcome indicators at the national level
  - Data used for long-term analysis and correlation with air quality trends

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

- **Website:** [https://ec.europa.eu/eurostat](https://ec.europa.eu/eurostat)
- **API Docs:** [https://ec.europa.eu/eurostat/web/json-and-unicode-web-services](https://ec.europa.eu/eurostat/web/json-and-unicode-web-services)
- **Access:** Public
- **Format:** JSON (SDMX), CSV, TSV
- **Granularity:**
  - Spatial: Country and NUTS-1/2/3 regional levels
  - Temporal: Yearly, some quarterly/montly
- **Relevant Datasets:**
  - `hlth_cd_aro`: Deaths from respiratory diseases
  - `hlth_cd_asdr2`: Standardized death rate by cause (e.g. lung cancer)
  - `hlth_co_dischls`: Hospital discharges by diagnosis
  - `env_air_emis`: Pollutant emissions (PM, CO2, NOx)
- **Update Frequency:** Yearly
- **Coverage Period:** From ~2000 to ~2023
- **Usage in Project:**
  - High-quality, standardized health and environmental indicators
  - Complement to WHO data with regional granularity (NUTS-2)
  - Will be used in the `silver` and `gold` layers for modeling

---
