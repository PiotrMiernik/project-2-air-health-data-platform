{{ config(materialized = 'table') }}

-- Year dimension table derived from the fact table
SELECT DISTINCT
    year AS year_id,
    year,
    CASE
        WHEN year BETWEEN 1990 AND 1999 THEN '1990s'
        WHEN year BETWEEN 2000 AND 2009 THEN '2000s'
        WHEN year BETWEEN 2010 AND 2019 THEN '2010s'
        WHEN year BETWEEN 2020 AND 2029 THEN '2020s'
        ELSE 'Other'
    END AS decade_label
FROM {{ ref('fact_air_health') }}
WHERE year IS NOT NULL
ORDER BY year;