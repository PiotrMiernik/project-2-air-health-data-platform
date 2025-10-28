{{ config(materialized = 'table') }}

-- Dimension table for WHO health indicators
WITH ranked AS (
    SELECT
        indicator_code AS who_indicator_code,
        environmental_cause,
        country_code,
        year,
        ROW_NUMBER() OVER (PARTITION BY indicator_code ORDER BY year DESC) AS rn
    FROM {{ source('silver', 'who_who') }}
    WHERE indicator_code IS NOT NULL
)
SELECT
    who_indicator_code,
    environmental_cause,
    country_code,
    year
FROM ranked
WHERE rn = 1
ORDER BY who_indicator_code
