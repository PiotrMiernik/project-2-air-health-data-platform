import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F

# --- Initialization ---
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# --- Input and output paths ---
input_path = "s3://project-2-air-health-data-platform/bronze/ecdc/"
output_path = "s3://project-2-air-health-data-platform/silver/ecdc/"

# --- Read raw JSON file (array of objects) ---
# The raw ECDC files are JSON arrays, so we first read them as plain text
raw_df = spark.read.text(input_path)

# --- Parse JSON array into individual records ---
# Define the schema explicitly to ensure correct typing
schema_str = """
array<
  struct<
    country:string,
    country_code:string,
    continent:string,
    population:long,
    indicator:string,
    year_week:string,
    weekly_count:int,
    cumulative_count:int,
    rate_14_day:double,
    source:string,
    note:string
  >
>
"""

# Flatten JSON array -> one row per record
parsed_df = raw_df.select(
    F.explode(F.from_json(F.col("value"), schema_str)).alias("record")
).select("record.*")

# --- Write output to Parquet ---
# Save transformed data to the Silver layer in Parquet format
parsed_df.write.mode("overwrite").parquet(output_path)

# --- Commit job ---
job.commit()

