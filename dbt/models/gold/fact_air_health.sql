{{ config(
    materialized = 'table',
    schema = 'gold'
) }}

-- 1. Air quality data (OpenAQ)
WITH air_quality AS (
    SELECT
        country_code,
        parameter_name AS pollutant,
        CAST(SUBSTRING(datetime_from_utc, 1, 4) AS INT) AS year,
        AVG(value) AS avg_pollutant_value
    FROM {{ source('silver', 'openaq_openaq') }}
    GROUP BY country_code, parameter_name, year
),

-- 2. Disease data (ECDC)
diseases AS (
    SELECT
        country_code,
        indicator AS disease_type,
        CAST(SPLIT_PART(year_week, '-', 1) AS INT) AS year,
        SUM(COALESCE(weekly_count, 0)) AS total_cases,
        MAX(COALESCE(rate_14_day, 0))   AS rate_14_day
    FROM {{ source('silver', 'ecdc_ecdc') }}
    GROUP BY country_code, indicator, year
),

-- 3. WHO health metrics
who_metrics AS (
    SELECT
        country_code,
        indicator_code AS who_indicator,
        sex,
        environmental_cause,
        CAST(year AS INT) AS year,
        AVG(COALESCE(value_numeric, 0)) AS who_value_avg
    FROM {{ source('silver', 'who_who') }}
    GROUP BY country_code, indicator_code, sex, environmental_cause, year
),

-- 4. Eurostat socioeconomic indicators
eurostat_data AS (
    SELECT
        country_code,
        dataset_label AS socio_indicator,
        CAST(num_years AS INT)  AS num_years
    FROM {{ source('silver', 'eurostat_eurostat') }}
)

-- 5. Final fact table
SELECT
    a.country_code,
    a.pollutant,
    a.year,
    a.avg_pollutant_value,

    d.disease_type,
    d.total_cases,
    d.rate_14_day,

    w.who_indicator,
    w.sex,
    w.environmental_cause,
    w.who_value_avg,

    e.socio_indicator,
    e.num_years,

    CASE 
        WHEN d.total_cases > 0 AND w.who_value_avg > 0 THEN 
            ROUND(d.total_cases / w.who_value_avg, 4)
        ELSE NULL 
    END AS cases_per_health_metric
FROM air_quality a
LEFT JOIN diseases d
       ON a.country_code = d.country_code
      AND a.year = d.year
LEFT JOIN who_metrics w
       ON a.country_code = w.country_code
      AND a.year = w.year
LEFT JOIN eurostat_data e
       ON a.country_code = e.country_code;
