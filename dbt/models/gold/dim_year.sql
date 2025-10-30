{{ config(
    materialized = 'table',
    external = true,
    file_format = 'parquet',
    alias = 'dim_year'
) }}

WITH who_years AS (
    SELECT
        DISTINCT CAST(year AS INT) AS year_value
    FROM {{ source('silver', 'who_who') }}
    WHERE year IS NOT NULL
),

openaq_years AS (
    SELECT
        DISTINCT EXTRACT(YEAR FROM from_iso8601_timestamp(datetime_from_utc)) AS year_value
    FROM {{ source('silver', 'openaq_openaq') }}
    WHERE datetime_from_utc IS NOT NULL
),

all_unique_years AS (
    SELECT year_value FROM who_years
    UNION
    SELECT year_value FROM openaq_years
    WHERE year_value BETWEEN 2010 AND 2025
)

SELECT
    ROW_NUMBER() OVER (ORDER BY year_value) AS year_id,
    year_value AS year,
    CASE
        WHEN year_value BETWEEN 2010 AND 2019 THEN '2010s'
        ELSE '2020s'
    END AS decade_label   
FROM all_unique_years
ORDER BY year