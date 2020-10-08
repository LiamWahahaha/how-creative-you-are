from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    LongType
)
from pyspark.sql.functions import udf

from file_manager import S3FileManager


class SparkProcessor:
    def __init__(self):
        self.spark = SparkSession \
                        .builder \
                        .appName('KernelCatcher') \
                        .getOrCreate()
        self.spark.sparkContext.addPyFile('utils.py')
        self.spark.sparkContext.addPyFile('file_manager.py')
        print('add py file success')
        self.spark.sparkContext.setLogLevel('ERROR')

    def extract_imported_packages_to_df(self, metadata_df):
        file_manager = S3FileManager()
        imported_packages_rdd = metadata_df.rdd.flatMap(file_manager.process_single_file_using_record)
        imported_packages_schema = StructType([StructField('competitor', StringType(), False),
                                               StructField('lastRunTime', StringType(), False),
                                               StructField('competition', StringType(), False),
                                               StructField('kernel', StringType(), True),
                                               StructField('importedPackages', StringType(), True)])
        imported_packages_df = imported_packages_rdd.map(lambda row: list(row)) \
                                                    .toDF(imported_packages_schema)

        return imported_packages_df

    def add_package_hash_to_df(self, imported_packages_df):
        hash_udf = udf(lambda imported_packages: hash(imported_packages), LongType())

        return imported_packages_df.withColumn('packageHash', hash_udf(imported_packages_df.importedPackages))

        
