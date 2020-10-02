import sys
from collections import defaultdict

import boto3

S3_RESPONSE_METADATA = 'ResponseMetadata'
S3_RESPONSE_METADATA_HTTP_STATUS = 'HTTPStatusCode'
S3_RESPONSE_CONTENTS = 'Contents'
S3_RESPONSE_CONTENT_KEY = 'Key'
S3_RESPONSE_NEXT_CONTINUATION_TOKEN = 'NextContinuationToken'
S3_MAX_KEY = 1000

class S3FileManager:
    METADATA = 'metadata'
    METADATA_FILE_TYPE = '.csv'
    ORIGINAL_FILES = 'original'
    ORIGINAL_FILE_TYPE = '.ipynb'
    CLEANED_FILES = 'cleaned'
    CLEANED_FILE_TYPE = '.py'
    ITERATION_UPPER_BOUND = 4e5/S3_MAX_KEY

    def __init__(self):
        self.s3_res = boto3.resource('s3')
        self.s3_client = boto3.client('s3')
        self.lookup_table = defaultdict(lambda: {
            self.METADATA: str,
            self.CLEANED_FILES: set()
        })

    def construct_lookup_table(self, bucket='code-database-s3', root_folder='real-challenges'):
        response = self.s3_client.list_objects_v2(
            Bucket=bucket, Prefix=root_folder, MaxKeys=S3_MAX_KEY
        )

        try:
            iteration = 0
            while iteration < self.ITERATION_UPPER_BOUND and \
                  response[S3_RESPONSE_METADATA][S3_RESPONSE_METADATA_HTTP_STATUS] == 200:
                if S3_RESPONSE_CONTENTS not in response:
                    break
                self._parse_contents(response[S3_RESPONSE_CONTENTS])

                if S3_RESPONSE_NEXT_CONTINUATION_TOKEN in response:
                    iteration += 1
                    response = self.s3_client.list_objects_v2(
                        Bucket=bucket,
                        Prefix=root_folder,
                        MaxKeys=S3_MAX_KEY,
                        ContinuationToken=response[S3_RESPONSE_NEXT_CONTINUATION_TOKEN]
                    )
                else:
                    break
        except KeyError:
            sys.exit()

    def _parse_contents(self, contents):
        for content in contents:
            keys = content[S3_RESPONSE_CONTENT_KEY].strip('/').split('/')
            self._update_metadata_to_lookup_table(keys, content[S3_RESPONSE_CONTENT_KEY])
            self._add_cleaned_file_to_lookup_table(keys, content[S3_RESPONSE_CONTENT_KEY])

    def _update_metadata_to_lookup_table(self, keys, s3_key):
        """
        a valid keys would be in the following format:
        [root-folder]/[challenge name]/[file name].METADATA_FILE_TYPE
        """
        if len(keys) != 3 or \
           len(keys[2]) <= len(self.METADATA_FILE_TYPE) or \
           keys[2][-len(self.METADATA_FILE_TYPE):] != self.METADATA_FILE_TYPE:
            return False

        self.lookup_table[keys[1]][self.METADATA] = s3_key

        return True

    def _add_cleaned_file_to_lookup_table(self, keys, s3_key):
        """
        a valid keys would be in the following format:
        [root-folder]/[challenge name]/CLEANED_FILES/[file name].CLEANED_FILE_TYPE
        """
        if len(keys) != 4 or \
           keys[2] != self.CLEANED_FILES or \
           len(keys[3]) <= len(self.CLEANED_FILE_TYPE) or \
           keys[3][-len(self.CLEANED_FILE_TYPE):] != self.CLEANED_FILE_TYPE:
            return False

        self.lookup_table[keys[1]][self.CLEANED_FILES].add(s3_key)

        return True

    # def retrieve_notebooks_by_challenges(bucket, root_path):
    #     response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=)
