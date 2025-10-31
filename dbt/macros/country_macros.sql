{% macro map_country_code_2_to_3_letter(two_letter_code_field) %}
    (
        SELECT code_3l
        FROM {{ ref('country_code_map') }}
        WHERE code_2l = {{ two_letter_code_field }}
    )
{% endmacro %}