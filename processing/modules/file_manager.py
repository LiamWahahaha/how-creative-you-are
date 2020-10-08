import sys
from collections import defaultdict
import json

import boto3

from utils import (
    is_notebook_code_cell,
    extract_source_code_from_notebook,
    extract_imported_package_from_next_line,
    extract_imported_package,
    Print
)

from constant import (
    S3_RESPONSE_METADATA,
    S3_RESPONSE_METADATA_HTTP_STATUS,
    S3_RESPONSE_CONTENTS,
    S3_RESPONSE_CONTENT_KEY,
    S3_RESPONSE_NEXT_CONTINUATION_TOKEN,
    S3_MAX_KEY,
    DEFAULT_BUCKET,
    ROOT_FOLDER
)

class S3FileManager:
    METADATA = 'metadata'
    METADATA_FILE_TYPE = '.csv'
    ORIGINAL_FILES = 'original'
    ORIGINAL_FILE_TYPE = '.ipynb'
    CLEANED_FILES = 'cleaned'
    CLEANED_FILE_TYPE = '.py'
    ITERATION_UPPER_BOUND = 4e5/S3_MAX_KEY

    def __init__(self, bucket=DEFAULT_BUCKET, root_folder=ROOT_FOLDER):
        self.bucket = bucket
        self.root_folder = root_folder
        self.lookup_table = defaultdict(lambda: {
            self.METADATA: str,
            self.CLEANED_FILES: set()
        })

    def construct_lookup_table(self):
        s3_client = boto3.client('s3')
        response = s3_client.list_objects_v2(
            Bucket=self.bucket, Prefix=self.root_folder, MaxKeys=S3_MAX_KEY
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
                    response = s3_client.list_objects_v2(
                        Bucket=self.bucket,
                        Prefix=self.root_folder,
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
        [root-folder]/[competition name]/[kernel name].METADATA_FILE_TYPE
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
        [root-folder]/[competition name]/CLEANED_FILES/[kernel name].CLEANED_FILE_TYPE
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

    def process_single_file_using_record(self, record):
        """
        A flatMap function
        """
        s3_res = boto3.resource('s3')
        return_data = list()
        competitor = record.ref.split('/')[0]
        competition = record.competition
        kernel = record.kernel
        imported_packages = set()

        if not competition or not kernel:
            imported_packages = ''
            return_data.append((competitor,
                                record.lastRunTime,
                                competition,
                                kernel,
                                imported_packages))
            return return_data

        s3_download_path = f'{self.root_folder}/{competition}/{self.ORIGINAL_FILES}'
        s3_upload_path = f'{self.root_folder}/{competition}/{self.CLEANED_FILES}'
        download_file = f'{kernel}{self.ORIGINAL_FILE_TYPE}'
        upload_file = f'{kernel}{self.CLEANED_FILE_TYPE}'
        s3_upload_key = f'{s3_upload_path}/{upload_file}'

        try:
            s3_res.Bucket(self.bucket).download_file(f'{s3_download_path}/{download_file}',
                                                     download_file)
            notebook, imported_packages = self._process_notebook(download_file)
            self._upload_cleaned_script_to_s3(upload_file=upload_file,
                                              file_content=notebook,
                                              s3_upload_key=s3_upload_key,
                                              s3_resource=s3_res)
        except:
            Print.error('Process single file failed')

        imported_packages = sorted(list(imported_packages))
        return_data.append((competitor,
                            record.lastRunTime,
                            competition,
                            kernel,
                            ','.join(imported_packages)))

        return return_data

    def process_single_file(self, competition='', kernel=''):
        """
        upload cleaned python script back to s3 and return sorted import packages
        """
        s3_res = boto3.resource('s3')
        imported_packages = set()
        if not competition or not kernel:
            return json.dumps({})

        s3_download_path = f'{self.root_folder}/{competition}/{self.ORIGINAL_FILES}'
        s3_upload_path = f'{self.root_folder}/{competition}/{self.CLEANED_FILES}'
        download_file = kernel + self.ORIGINAL_FILE_TYPE
        upload_file = kernel + self.CLEANED_FILE_TYPE
        s3_upload_key = f'{s3_upload_path}/{upload_file}'

        try:
            s3_res.Bucket(self.bucket).download_file(f'{s3_download_path}/{download_file}',
                                                     download_file)
            notebook, imported_packages = self._process_notebook(download_file)
            self._upload_cleaned_script_to_s3(upload_file=upload_file,
                                              file_content=notebook,
                                              s3_upload_key=s3_upload_key,
                                              s3_resource=s3_res)
        except:
            Print.error('Process single file failed')

        imported_packages = sorted(list(imported_packages))

        return imported_packages

    def _process_notebook(self, download_file=None):
        """
        Returns:
        str: cleaned script
        set: imported packages
        """
        cleaned_script = list()
        imported_packages = set()

        try:
            local_file = open(download_file, 'r')
            notebook = json.loads(local_file.read())
            local_file.close()

            for cell in notebook['cells']:
                if not is_notebook_code_cell(cell):
                    continue
                source_code = extract_source_code_from_notebook(cell)
                cleaned_script.append(source_code)
                combine_next_line = False
                for line in source_code.split('\n'):
                    packages = set()
                    if combine_next_line:
                        combine_next_line, packages = extract_imported_package_from_next_line(line)
                    else:
                        combine_next_line, packages = extract_imported_package(line)
                    imported_packages = imported_packages.union(packages)
        except:
            Print.error('Process local notebook file failed')

        return '\n'.join(cleaned_script), imported_packages

    def _upload_cleaned_script_to_s3(self,
                                     upload_file='',
                                     file_content='',
                                     s3_upload_key='',
                                     s3_resource=None):
        try:
            file_writer = open(upload_file, 'w')
            file_writer.write(file_content)
            file_writer.close()
            s3_resource.Object(self.bucket, s3_upload_key).upload_file(upload_file)
        except:
            Print.error('Upload cleaned script to S3 failed')
