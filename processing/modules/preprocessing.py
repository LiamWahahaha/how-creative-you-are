import time
from spark_processor import SparkProcessor
from utils import Print

def main():
    tic = time.perf_counter()
    Print.info('Start preprocessing')
    parallel_processor = SparkProcessor()
    spark = parallel_processor.spark
    
    Print.info('Load metadata file from s3')
    metadata_s3_path = 's3a://code-database-s3/real-challenges-meta'
    metadata_df = spark.read.option('header', 'true').csv(metadata_s3_path)
    metadata_df.show()

    packages_info_df = parallel_processor.extract_imported_packages_to_df(metadata_df)
    packages_info_df.show()

    packages_hash_df = parallel_processor.add_package_hash_to_df(packages_info_df)
    packages_hash_df.show()


    Print.info('Upload metadata file to s3 in parquet format')
    packages_hash_df.write.parquet('s3a://code-database-s3/real-challenge-final-dataset/final.parquet', mode='overwrite')
    toc = time.perf_counter()
    Print.info(f'===============================================')
    Print.info(f'Processed {packages_hash_df.count()} records')
    Print.info(f'Total processing time: {toc - tic:0.4f} seconds')
    Print.info(f'===============================================')

if __name__ == '__main__':
    main()
