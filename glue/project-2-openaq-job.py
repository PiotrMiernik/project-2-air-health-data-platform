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
input_path = "s3://project-2-air-health-data-platform/bronze/openaq/v3/eu27/"
output_path = "s3://project-2-air-health-data-platform/silver/openaq/"

# --- Read all JSON files recursively (one per country) ---
raw_df = spark.read.option("recursiveFileLookup", "true").text(input_path)

# --- Define schema for the OpenAQ yearly records ---
schema_str = """
struct<
  iso:string,
  sensor_id:long,
  yearly:array<
    struct<
      value:double,
      flagInfo:struct<hasFlags:boolean>,
      parameter:struct<id:int,name:string,units:string,displayName:string>,
      period:struct<
        label:string,
        interval:string,
        datetimeFrom:struct<utc:string,local:string>,
        datetimeTo:struct<utc:string,local:string>
      >,
      coordinates:string,
      summary:struct<
        min:double,
        q02:double,
        q25:double,
        median:double,
        q75:double,
        q98:double,
        max:double,
        avg:double,
        sd:double
      >,
      coverage:struct<
        expectedCount:int,
        expectedInterval:string,
        observedCount:int,
        observedInterval:string,
        percentComplete:double,
        percentCoverage:double,
        datetimeFrom:struct<utc:string,local:string>,
        datetimeTo:struct<utc:string,local:string>
      >
    >
  >
>
"""

# --- Parse and flatten nested structure ---
parsed_df = raw_df.select(F.from_json(F.col("value"), schema_str).alias("data"))

# Explode yearly array into separate rows
flattened_df = parsed_df.select(
    F.col("data.iso").alias("country_code"),
    F.col("data.sensor_id").alias("sensor_id"),
    F.explode(F.col("data.yearly")).alias("yearly_record")
)

# Select and flatten fields inside yearly_record
final_df = flattened_df.select(
    "country_code",
    "sensor_id",
    F.col("yearly_record.parameter.name").alias("parameter_name"),
    F.col("yearly_record.parameter.units").alias("units"),
    F.col("yearly_record.period.label").alias("period_label"),
    F.col("yearly_record.period.interval").alias("period_interval"),
    F.col("yearly_record.period.datetimeFrom.utc").alias("datetime_from_utc"),
    F.col("yearly_record.period.datetimeTo.utc").alias("datetime_to_utc"),
    F.col("yearly_record.value").alias("value"),
    F.col("yearly_record.summary.avg").alias("avg_value"),
    F.col("yearly_record.summary.min").alias("min_value"),
    F.col("yearly_record.summary.max").alias("max_value"),
    F.col("yearly_record.summary.median").alias("median_value"),
    F.col("yearly_record.summary.sd").alias("stddev_value"),
    F.col("yearly_record.coverage.percentCoverage").alias("coverage_percent"),
    F.col("yearly_record.coverage.percentComplete").alias("complete_percent")
)

# --- Write to Parquet (Silver layer) ---
final_df.write.mode("overwrite").parquet(output_path)

# --- Commit job ---
job.commit()