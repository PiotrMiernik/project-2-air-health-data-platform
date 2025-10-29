-- Custom test: ensure all country codes are 2 or 3 uppercase letters
SELECT *
FROM {{ ref('dim_country') }}
WHERE NOT REGEXP_LIKE(country_code, '^[A-Z]{2,3}$')