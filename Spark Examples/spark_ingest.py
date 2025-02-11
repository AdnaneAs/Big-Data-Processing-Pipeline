#!/usr/bin/env python3
"""
spark_ingest_refresh.py

This script connects to a remote Spark master, reads JSON data from a file,
and writes it to HDFS. The ingestion process repeats every 5 seconds.

Ensure that:
  - Your Spark containers can resolve the HDFS namenode.
  - The HDFS namenode is accessible at the configured host and port.
"""

import time
import sys
from pyspark.sql import SparkSession

def ingest_data(spark, input_file, output_path):
    """
    Reads a JSON file into a DataFrame and writes it to HDFS.
    """
    try:
        # Read the JSON file into a DataFrame
        df = spark.read.json(input_file)
    except Exception as e:
        print("Error reading the JSON file:", e)
        return False

    # Optional: Print schema and a data preview for debugging
    print("Schema of the ingested data:")
    df.printSchema()
    print("Data preview:")
    df.show(truncate=False)
    
    try:
        # Write the DataFrame to HDFS in JSON format, overwriting existing data
        df.write.mode("overwrite").json(output_path)
        print(f"Data successfully ingested to HDFS at: {output_path}")
    except Exception as e:
        print("Error writing data to HDFS:", e)
        return False
    
    return True

def main():
    # IMPORTANT: Replace 'namenode' with the actual hostname or IP if needed.
    spark = SparkSession.builder \
        .appName("JSON to HDFS Ingestion Refresh") \
        .master("spark://spark-master:7077") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:8020") \
        .getOrCreate()

    # Local JSON file path (make sure this file exists where the job is run)
    input_file = "data.json"
    
    # HDFS output path (adjust if necessary)
    output_path = "hdfs://namenode:8020/user/spark/json_data"
    
    print("Starting the ingestion process. Press Ctrl+C to stop.")
    try:
        while True:
            print("Starting new ingestion cycle...")
            ingest_data(spark, input_file, output_path)
            print("Cycle complete. Waiting for 5 seconds before the next ingestion cycle...\n")
            time.sleep(5)
    except KeyboardInterrupt:
        print("Ingestion process interrupted by user. Exiting...")
    finally:
        spark.stop()
        print("Spark session stopped.")

if __name__ == '__main__':
    main()

