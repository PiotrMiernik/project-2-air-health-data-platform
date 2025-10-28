{{ config(materialized = 'table') }}

SELECT DISTINCT
    country_code,
    country AS country_name,
    continent,
    MAX(population) AS population
FROM {{ source('silver', 'ecdc_ecdc') }}
WHERE country_code IS NOT NULL
GROUP BY country_code, country, continent;
