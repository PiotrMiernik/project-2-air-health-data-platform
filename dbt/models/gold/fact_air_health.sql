{{ config(
    materialized = 'table',
    external = true,
    file_format = 'parquet'
) }}

-- 1. Air quality data (OpenAQ)
WITH air_quality AS (
    SELECT
        country_code,
        parameter_name AS pollutant,
        CAST(SUBSTRING(datetime_from_utc, 1, 4) AS INT) AS year,
        AVG(COALESCE(value, 0)) AS avg_pollutant_value
    FROM {{ source('silver', 'openaq_openaq') }}
    WHERE country_code IS NOT NULL AND datetime_from_utc IS NOT NULL
    GROUP BY country_code, parameter_name, CAST(SUBSTRING(datetime_from_utc, 1, 4) AS INT)
),

-- 2. Disease data (ECDC)
diseases AS (
    SELECT
        country_code,
        indicator AS disease_type,
        CAST(SPLIT_PART(year_week, '-', 1) AS INT) AS year,
        SUM(COALESCE(weekly_count, 0)) AS total_cases,
        AVG(COALESCE(rate_14_day, 0)) AS avg_rate_14_day
    FROM {{ source('silver', 'ecdc_ecdc') }}
    WHERE year_week IS NOT NULL
    GROUP BY country_code, indicator, CAST(SPLIT_PART(year_week, '-', 1) AS INT)
),

-- 3. WHO health metrics
who_metrics AS (
    SELECT
        country_code,
        indicator_code AS who_indicator,
        CAST(year AS INT) AS year,
        AVG(COALESCE(value_numeric, 0)) AS who_value_avg
    FROM {{ source('silver', 'who_who') }}
    WHERE year IS NOT NULL
    GROUP BY country_code, indicator_code, CAST(year AS INT)
),

-- 4. Eurostat environmental indicators
eurostat_avg AS (
    SELECT
        country_code,
        AVG(COALESCE(emission_value, 0)) AS avg_emission_value
    FROM {{ source('silver', 'eurostat_eurostat') }}
    WHERE country_code IS NOT NULL
    GROUP BY country_code
)

-- 5. Final fact table
SELECT
    a.country_code,
    a.pollutant,
    a.year,
    a.avg_pollutant_value,

    d.disease_type,
    d.total_cases,
    d.avg_rate_14_day,

    w.who_indicator,
    w.who_value_avg,

    e.avg_emission_value,

    CASE 
        WHEN d.total_cases > 0 AND w.who_value_avg > 0 THEN 
            ROUND(d.total_cases / NULLIF(w.who_value_avg, 0), 4)
        ELSE NULL 
    END AS cases_per_health_metric
FROM air_quality a
LEFT JOIN diseases d
       ON a.country_code = d.country_code
      AND a.year = d.year
LEFT JOIN who_metrics w
       ON a.country_code = w.country_code
      AND a.year = w.year
LEFT JOIN eurostat_avg e
       ON a.country_code = e.country_code;