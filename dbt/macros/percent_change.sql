{% macro percent_change(current_value, previous_value) %}
    CASE
        WHEN {{ previous_value }} = 0 OR {{ previous_value }} IS NULL THEN NULL
        ELSE ROUND((({{ current_value }} - {{ previous_value }}) / {{ previous_value }}) * 100, 2)
    END
{% endmacro %}
