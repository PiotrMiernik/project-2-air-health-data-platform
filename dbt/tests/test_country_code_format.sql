-- Custom test: ensure all country codes are 2 or 3 uppercase letters
SELECT *
FROM {{ ref('dim_country') }}
WHERE country_code NOT REGEXP '^[A-Z]{2,3}$'