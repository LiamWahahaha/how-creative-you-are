from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    LongType,
    FloatType
)
from pyspark.sql.functions import udf

from processing.modules.database_connector import PostgresConnector
from processing.modules.file_manager import S3FileManager
from processing.modules.similarity_calculator import SimilarityCalculator
from processing.modules.utils import Print


class SparkProcessor:
    def __init__(self):
        self.spark = SparkSession \
                        .builder \
                        .appName('KernelCatcher') \
                        .getOrCreate()
        self.spark.sparkContext.addPyFile('utils.py')
        self.spark.sparkContext.addPyFile('file_manager.py')
        self.spark.sparkContext.addPyFile('similarity_calculator.py')
        Print.info('Add py file success')
        self.spark.sparkContext.setLogLevel('ERROR')

    def extract_imported_packages_to_df(self, metadata_df):
        file_manager = S3FileManager()
        imported_packages_rdd = metadata_df.rdd \
                                           .flatMap(file_manager.process_single_file_using_record)
        imported_packages_schema = StructType([
            StructField('competitor', StringType(), False),
            StructField('lastRunTime', StringType(), False),
            StructField('competition', StringType(), False),
            StructField('kernel', StringType(), True),
            StructField('importedPackages', StringType(), True)
        ])
        imported_packages_df = imported_packages_rdd.map(list) \
                                                    .toDF(imported_packages_schema)

        return imported_packages_df

    def add_package_hash_to_df(self, imported_packages_df):
        hash_udf = udf(hash, LongType())
        return imported_packages_df \
                .withColumn('packageHash', hash_udf(imported_packages_df.importedPackages))

    def attach_similarity_score_to_df(self, metadata_df):
        calculator = SimilarityCalculator()
        similarity_rdd = metadata_df.rdd \
                                    .flatMap(calculator.calculate_code_similarity_using_record)
        similarity_schema = StructType([StructField('competitor', StringType(), False),
                                        StructField('competition', StringType(), False),
                                        StructField('kernel', StringType(), True),
                                        StructField('competitor2', StringType(), False),
                                        StructField('kernel2', StringType(), False),
                                        StructField('importedPackages', StringType(), True),
                                        StructField('similarityScore', FloatType(), True)])
        similarity_df = similarity_rdd.map(list) \
                                      .toDF(similarity_schema)

        return similarity_df

    def write_final_results_to_database(self, final_df):
        postgres_connector = PostgresConnector()
        postgres_connector.write(final_df, 'similarity_scores', 'append')

