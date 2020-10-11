import time
from spark_processor import SparkProcessor

from utils import Print
from constant import DEFAULT_PARQUET_PATH
from similarity_calculator import SimilarityCalculator

def main():
    tic = time.perf_counter()
    Print.info('Start preprocessing')
    parallel_processor = SparkProcessor()
    spark = parallel_processor.spark

    Print.info('Load metadata parquet from s3')
    metadata_s3_path = DEFAULT_PARQUET_PATH
    metadata_df = spark.read.parquet(metadata_s3_path)

    pairwise_metadata_df = SimilarityCalculator() \
                            .generate_pairwise_comparison_df_w_filter(metadata_df)
    Print.info('Generate pairwise comparison dataframe')

    similarity_score_df = parallel_processor.attach_similarity_score_to_df(pairwise_metadata_df)
    Print.info('Attached similarity score to dataframe')

    Print.info('Finished similarity score calculation')
    toc = time.perf_counter()
    records = metadata_df.count()
    Print.info('===============================================')
    Print.info(f'Total comparisons: {similarity_score_df.count()}')
    Print.info(f'Records: {records}')
    Print.info(f'Original required comparisons: {records**2}')
    Print.info(f'Total processing time: {toc - tic:0.4f} seconds')
    Print.info('===============================================')
    parallel_processor.write_final_results_to_database(similarity_score_df)
    similarity_score_df.write.parquet('s3a://code-database-s3/real-challenge-final-dataset/similarity_score.parquet', mode='overwrite')

if __name__ == '__main__':
    main()
