import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import functions as F

# Initialize Glue job and Spark context
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Input path (bronze) and output path (silver)
input_path = "s3://project-2-air-health-data-platform/bronze/eurostat/env_air_gge/"
output_path = "s3://project-2-air-health-data-platform/silver/eurostat/"

# Read all JSON files recursively
raw_df = spark.read.option("recursiveFileLookup", "true").json(input_path)

# Extract main metadata and the value field
parsed_df = raw_df.select(
    F.col("label").alias("dataset_label"),
    F.col("source"),
    F.col("updated").alias("last_updated"),
    F.col("value").alias("value_struct")
)

# Convert struct<0:...,1:...,> to map<string,double>
value_field_names = [f.name for f in parsed_df.schema["value_struct"].dataType.fields]
map_entries = []
for c in value_field_names:
    map_entries.append(F.lit(c))
    map_entries.append(F.col(f"value_struct.`{c}`"))
parsed_df = parsed_df.withColumn("value_map", F.create_map(*map_entries))

# Explode map into key-value pairs
exploded_df = parsed_df.select(
    "dataset_label",
    "source",
    "last_updated",
    F.explode("value_map").alias("key", "emission_value")
)

# Extract year index from the key (Eurostat encodes dimensions like "0:0", "0:1", etc.)
# For simplicity, we interpret the second index as time
exploded_df = exploded_df.withColumn("geo_index", F.split(F.col("key"), ":").getItem(0))
exploded_df = exploded_df.withColumn("time_index", F.split(F.col("key"), ":").getItem(1))

# Derive country_code from file path (folder name in S3)
# Glue provides this metadata as _metadata.file_path
exploded_df = exploded_df.withColumn(
    "country_code",
    F.regexp_extract(F.input_file_name(), r"/([A-Z]{2})_", 1)
)

# Map the time index to actual years
# Since we do not have time_labels here, we approximate years sequentially from 1990 onwards
# This is acceptable for simplified educational use
exploded_df = exploded_df.withColumn(
    "year",
    (F.col("time_index").cast("int") + F.lit(1990))
)

# Select final columns for the Silver layer
df_final = exploded_df.select(
    F.lit("eurostat").alias("dataset_name"),
    "dataset_label",
    "source",
    "last_updated",
    "country_code",
    F.col("year").cast("int"),
    F.col("emission_value").cast("double")
)

# Write the transformed data to Parquet
df_final.write.mode("overwrite").parquet(output_path)

# Commit Glue job
job.commit()
