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
input_path = "s3://project-2-air-health-data-platform/bronze/eurostat/"
output_path = "s3://project-2-air-health-data-platform/silver/eurostat/"

# --- Read all raw JSON files recursively (each is a dataset for one country) ---
# The files are nested in subfolders (one per indicator), so we use recursive loading
raw_df = spark.read.option("recursiveFileLookup", "true").text(input_path)

# --- Extract key fields from JSON structure ---
# Each file contains a complex JSON object. We select only essential metadata fields.
# The "value" object is empty in most cases and can be ignored for now.
# Focus on general dataset metadata (label, source, updated, geo, time range).
parsed_df = raw_df.select(
    F.from_json(
        F.col("value"),
        """
        struct<
            version:string,
            class:string,
            label:string,
            source:string,
            updated:string,
            id:array<string>,
            size:array<int>,
            dimension:struct<
                geo:struct<category:struct<label:map<string,string>>>,
                time:struct<category:struct<label:map<string,string>>>,
                sex:struct<category:struct<label:map<string,string>>>,
                age:struct<category:struct<label:map<string,string>>>,
                icd10:struct<category:struct<label:map<string,string>>>
            >
        >
        """
    ).alias("data")
)

# --- Flatten fields for analysis ---
# Extract country, dataset label, update date, and number of time points
df_flat = parsed_df.select(
    F.lit("eurostat").alias("dataset_name"),
    F.col("data.label").alias("dataset_label"),
    F.col("data.source").alias("source"),
    F.col("data.updated").alias("last_updated"),
    F.map_keys("data.dimension.geo.category.label")[0].alias("country_code"),
    F.map_values("data.dimension.geo.category.label")[0].alias("country_name"),
    F.size(F.col("data.dimension.time.category.label")).alias("num_years")
)

# --- Write to Parquet (Silver layer) ---
df_flat.write.mode("overwrite").parquet(output_path)

# --- Commit job ---
job.commit()