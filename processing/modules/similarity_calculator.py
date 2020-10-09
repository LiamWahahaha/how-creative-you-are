import boto3
import pycode_similar
from pyspark.sql.functions import col

from constant import (
    DEFAULT_BUCKET,
    ROOT_FOLDER,
    Print
)

class SimilarityCalculator:
    SCRIPT_FOLDER = 'cleaned'
    SCRIPT_FILE_TYPE = '.py'

    def __init__(self, bucket=DEFAULT_BUCKET, root_folder=ROOT_FOLDER):
        self.bucket = bucket
        self.root_folder = root_folder

    @classmethod
    def generate_pairwise_comparison_df_wo_filter(cls, kernel_df=None):
        """
        Return a Cartesian product dataframe (records from N to N^2)
        """
        return cls._generate_pairwise_comparison_df(kernel_df)

    @classmethod
    def generate_pairwise_comparison_df_w_filter(cls, kernel_df=None):
        """
        Return filtered Cartesian product dataframe (records from N to less than N^2)
        """
        original_df = cls._generate_pairwise_comparison_df(kernel_df)
        final_df = original_df.where((col('competitor') != col('competitor2')) &
                                     (col('competition') == col('competition2')) &
                                     (col('lastRunTime') > col('lastRunTime2')) &
                                     (col('packageHash') != col('packageHash2')))
        return final_df

    def _generate_pairwise_comparison_df(self, kernel_df=None):
        """
        helper function
        """
        dummy_kernel_df = kernel_df.select(
            kernel_df['competitor'].alias('competitor2'),
            kernel_df['lastRunTime'].alias('lastRunTime2'),
            kernel_df['competition'].alias('competition2'),
            kernel_df['kernel'].alias('kernel2'),
            kernel_df['importedPackages'].alias('importedPackages2'),
            kernel_df['packageHash'].alias('packageHash2')
        )
        return kernel_df.crossJoin(dummy_kernel_df)

    def calculate_code_similarity_using_record(self, record):
        """
        A flatMap function
        """
        s3_res = boto3.resource('s3')
        competition = record.competition
        competitor1 = record.competitor
        kernel1 = record.kernel
        competitor2 = record.competitor2
        kernel2 = record.kernel2
        similarity_score = -1

        s3_download_path = f'{self.root_folder}/{competition}/{self.SCRIPT_FOLDER}'
        download_file_1 = f'{kernel1}{self.SCRIPT_FILE_TYPE}'
        download_file_2 = f'{kernel2}{self.SCRIPT_FILE_TYPE}'
        try:
            s3_res.Bucket(self.bucket) \
                  .download_file(f'{s3_download_path}/{download_file_1}', download_file_1)
            s3_res.Bucket(self.bucket) \
                  .download_file(f'{s3_download_path}/{download_file_2}', download_file_2)
            similarity_score = self._calculate_similarity_score(download_file_1, download_file_2)
        except:
            Print.error('Process single record failed')

        return [(competitor1,
                 competition,
                 kernel1,
                 competitor2,
                 kernel2,
                 record.importedPackes,
                 similarity_score)]

    def _calculate_similarity_score(self, file1, file2):
        similarity_score = -1
        try:
            local_kernel1 = open(file1, 'r')
            local_kernel2 = open(file2, 'r')
            score = pycode_similar.detect([local_kernel1.read(), local_kernel2.read()])
            similarity_score = score[0][0]
        except:
            Print.error('Calculate similarity score failed')

        return similarity_score
