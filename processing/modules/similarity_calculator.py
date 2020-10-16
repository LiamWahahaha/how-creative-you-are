import boto3
import pycode_similar
from pyspark.sql.functions import col

from constant import (
    DEFAULT_BUCKET,
    ROOT_FOLDER
)

class SimilarityCalculator:
    SCRIPT_FOLDER = 'cleaned'
    SCRIPT_FILE_TYPE = '.py'

    def __init__(self, bucket=DEFAULT_BUCKET, root_folder=ROOT_FOLDER):
        self.bucket = bucket
        self.root_folder = root_folder

    def generate_pairwise_comparison_df_wo_filter(self, kernel_df=None):
        """
        Return a Cartesian product dataframe (records from N to N^2)
        """
        return self._generate_pairwise_comparison_df(kernel_df)

    def generate_pairwise_comparison_df_w_filter(self, kernel_df=None, competition=None):
        """
        Return filtered Cartesian product dataframe (records from N to less than N^2)
        """
        original_df = self._generate_pairwise_comparison_df(kernel_df)
        final_df = original_df.where((col('competitor') != col('competitor2')) &
                                     (col('competition') == col('competition2')) &
                                     (col('lastRunTime') > col('lastRunTime2')) &
                                     (col('packageHash') != col('packageHash2')))
        if competition:
            final_df = final_df.where(col('competition') == competition)

        return final_df

    def _generate_pairwise_comparison_df(self, kernel_df):
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
        pairwise_comparison_df = kernel_df.crossJoin(dummy_kernel_df)
        return pairwise_comparison_df

    def calculate_code_similarity_using_record(self, record):
        """
        A flatMap function
        competitor1 is candidate
        competitor2 is reference
        """
        s3_res = boto3.resource('s3')
        competition = record.competition
        competitor1 = record.competitor
        kernel1 = record.kernel
        competitor2 = record.competitor2
        kernel2 = record.kernel2
        similarity_score = -1.0

        s3_download_path = f'{self.root_folder}/{competition}/{self.SCRIPT_FOLDER}'
        candidate_file = f'{kernel1}{self.SCRIPT_FILE_TYPE}'
        referenced_file = f'{kernel2}{self.SCRIPT_FILE_TYPE}'

        try:
            if kernel1 == kernel2:
                similarity_score = 1.0
            else:
                s3_res.Bucket(self.bucket) \
                      .download_file(f'{s3_download_path}/{referenced_file}', referenced_file)
                s3_res.Bucket(self.bucket) \
                      .download_file(f'{s3_download_path}/{candidate_file}', candidate_file)
                similarity_score = self._calculate_similarity_score(referenced_file,
                                                                    candidate_file)
        except:
            pass
            # Print.error('Process single record failed')

        return [(competitor1,
                 competition,
                 kernel1,
                 competitor2,
                 kernel2,
                 record.importedPackages,
                 similarity_score)]

    def _calculate_similarity_score(self, referenced_code_str, candidate_code_str):
        """
        pycode_similar.detect([referenced_code_str, candidate_code_str])
        """
        similarity_score = -1.0
        try:
            referenced = open(referenced_code_str, 'r')
            candidate = open(candidate_code_str, 'r')
            score = pycode_similar.detect([referenced.read(), candidate.read()])
            summarize = pycode_similar.summarize(score[0][1])
            similarity_score = summarize[0]
        except:
            pass

        return similarity_score
