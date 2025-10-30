{{ config(
    materialized = 'table',
    external = true,
    file_format = 'parquet',
    alias = 'dim_country'
) }}

SELECT
    ROW_NUMBER() OVER (ORDER BY country_code) AS country_id, 
    country_code,
    country AS country_name,
    AVG(population) AS avg_population 
FROM {{ source('silver', 'ecdc_ecdc') }}
WHERE 
    country_code IS NOT NULL
    AND country IS NOT NULL
GROUP BY 
    country_code, 
    country
ORDER BY 
    country_id
