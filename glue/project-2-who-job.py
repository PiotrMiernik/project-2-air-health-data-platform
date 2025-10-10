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
input_path = "s3://project-2-air-health-data-platform/bronze/who/"
output_path = "s3://project-2-air-health-data-platform/silver/who/"

# --- Read all JSON files recursively (each represents one indicator) ---
raw_df = spark.read.option("recursiveFileLookup", "true").text(input_path)

# --- Define schema for WHO data ---
schema_str = """
struct<
  indicator:string,
  records:array<
    struct<
      Id:long,
      IndicatorCode:string,
      SpatialDimType:string,
      SpatialDim:string,
      TimeDimType:string,
      ParentLocationCode:string,
      ParentLocation:string,
      Dim1Type:string,
      Dim1:string,
      TimeDim:int,
      Dim2Type:string,
      Dim2:string,
      Dim3Type:string,
      Dim3:string,
      DataSourceDimType:string,
      DataSourceDim:string,
      Value:string,
      NumericValue:double,
      Low:double,
      High:double,
      Comments:string,
      Date:string,
      TimeDimensionValue:string,
      TimeDimensionBegin:string,
      TimeDimensionEnd:string
    >
  >
>
"""

# --- Parse and flatten structure ---
parsed_df = raw_df.select(F.from_json(F.col("value"), schema_str).alias("data"))

# Explode array of records -> one row per record
flattened_df = parsed_df.select(
    F.col("data.indicator").alias("indicator_code"),
    F.explode(F.col("data.records")).alias("record")
)

# Select and rename relevant fields
final_df = flattened_df.select(
    "indicator_code",
    F.col("record.Id").alias("record_id"),
    F.col("record.IndicatorCode").alias("indicator_subcode"),
    F.col("record.SpatialDim").alias("country_code"),
    F.col("record.ParentLocation").alias("region"),
    F.col("record.Dim1").alias("sex"),
    F.col("record.Dim2").alias("environmental_cause"),
    F.col("record.TimeDim").alias("year"),
    F.col("record.NumericValue").alias("value_numeric"),
    F.col("record.Value").alias("value_text"),
    F.col("record.Low").alias("low_ci"),
    F.col("record.High").alias("high_ci"),
    F.col("record.Date").alias("record_date"),
    F.col("record.TimeDimensionBegin").alias("period_start"),
    F.col("record.TimeDimensionEnd").alias("period_end")
)

# --- Write to Parquet (Silver layer) ---
final_df.write.mode("overwrite").parquet(output_path)

# --- Commit job ---
job.commit()
