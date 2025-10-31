{{ config(
    materialized = 'table',
    external = true,
    file_format = 'parquet',
    alias = 'fact_air_health'
) }}

--- 1. PIVOT WHO DATA (Health Indicators) ---
-- Pivoting all 11 indicator_codes to separate measure columns.
WITH pivoted_who_data AS (
    SELECT
        T1.country_code,
        CAST(T1.year AS INT) AS year,
        
        -- PIVOTING: Indicator_code to measure columns (using MAX/CASE WHEN)
        MAX(CASE WHEN T1.indicator_code = 'AIR_12' THEN T1.value_numeric END) AS who_air_12_value,
        MAX(CASE WHEN T1.indicator_code = 'AIR_62' THEN T1.value_numeric END) AS who_air_62_value,
        MAX(CASE WHEN T1.indicator_code = 'AIR_15' THEN T1.value_numeric END) AS who_air_15_value,
        MAX(CASE WHEN T1.indicator_code = 'AIR_16' THEN T1.value_numeric END) AS who_air_16_value,
        MAX(CASE WHEN T1.indicator_code = 'AIR_35' THEN T1.value_numeric END) AS who_air_35_value,
        MAX(CASE WHEN T1.indicator_code = 'TOTENV_3' THEN T1.value_numeric END) AS who_totenv_3_value,
        MAX(CASE WHEN T1.indicator_code = 'AIR_46' THEN T1.value_numeric END) AS who_air_46_value,
        MAX(CASE WHEN T1.indicator_code = 'AIR_10' THEN T1.value_numeric END) AS who_air_10_value,
        MAX(CASE WHEN T1.indicator_code = 'AIR_6' THEN T1.value_numeric END) AS who_air_6_value,
        MAX(CASE WHEN T1.indicator_code = 'AIR_42' THEN T1.value_numeric END) AS who_air_42_value,
        MAX(CASE WHEN T1.indicator_code = 'AIR_60' THEN T1.value_numeric END) AS who_air_60_value
        
    FROM {{ source('silver', 'who_who') }} T1
    WHERE T1.value_numeric IS NOT NULL
    GROUP BY 1, 2
),

--- 2. AGGREGATE ECDC DATA (Weekly to Annual Counts) ---
-- Summing weekly_count to get annual cases per Country-Year.
aggregated_ecdc_data AS (
    SELECT
        T1.country_code,
        CAST(SUBSTRING(T1.year_week, 1, 4) AS INT) AS year, -- Extracting year from 'YYYY-WW' format
        SUM(T1.weekly_count) AS ecdc_annual_covid_cases
        
    FROM {{ source('silver', 'ecdc_ecdc') }} T1
    WHERE T1.weekly_count IS NOT NULL
    GROUP BY 1, 2
),

--- 3. AGGREGATE OPENAQ DATA (Air Pollution) ---
-- Aggregating PM25 (the only parameter) to Country-Year level.
aggregated_openaq_data AS (
    SELECT
        {{ map_country_code_2_to_3_letter('T1.country_code') }} AS country_code,
        EXTRACT(YEAR FROM from_iso8601_timestamp(T1.datetime_from_utc)) AS year,
        
        -- PM25 is the only parameter, calculate average concentration
        AVG(T1.value) AS avg_pm25_concentration
        
    FROM {{ source('silver', 'openaq_openaq') }} T1
    WHERE T1.value IS NOT NULL AND T1.parameter_name = 'pm25'
    GROUP BY 1, 2
),

--- 4. JOIN ALL DATA WITH DIMENSIONS (Star Schema) ---
final_fact_table AS (
    SELECT
        -- Dimension Keys (Foreign Keys)
        DC.country_id,
        DY.year_id,
        DC.country_code,
        DY.year,

        -- Measures from WHO
        WH.who_air_12_value,
        WH.who_air_62_value,
        WH.who_air_15_value,
        WH.who_air_16_value,
        WH.who_air_35_value,
        WH.who_totenv_3_value,
        WH.who_air_46_value,
        WH.who_air_10_value,
        WH.who_air_6_value,
        WH.who_air_42_value,
        WH.who_air_60_value,

        -- Measures from ECDC
        EC.ecdc_annual_covid_cases,
        
        -- Measures from OpenAQ
        OA.avg_pm25_concentration
        
    FROM {{ ref('dim_country') }} DC
    
    -- CROSS JOIN to guarantee every Country-Year combination from the dimensions
    CROSS JOIN {{ ref('dim_year') }} DY
    
    -- LEFT JOINs to attach measures (allowing NULLs if no data exists for a Country-Year)
    LEFT JOIN pivoted_who_data WH
        ON DC.country_code = WH.country_code
        AND DY.year = WH.year

    LEFT JOIN aggregated_ecdc_data EC
        ON DC.country_code = EC.country_code
        AND DY.year = EC.year
        
    LEFT JOIN aggregated_openaq_data OA
        ON DC.country_code = OA.country_code
        AND DY.year = OA.year

    WHERE DC.country_code IS NOT NULL
)

SELECT * FROM final_fact_table
ORDER BY country_id, year_id