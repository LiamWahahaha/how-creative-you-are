import unittest
from ..modules.file_manager import S3FileManager

class S3FileManagerTest(unittest.TestCase):
    def test_file_manager(self):
        test_folder = 'unittest'
        competition = 'fake-competition'
        file_manager = S3FileManager(root_folder=test_folder)
        meta_file = f'{test_folder}/{competition}/tmp.csv'
        cleaned_file = f'{test_folder}/{competition}/cleaned/tmp.py'
        file_manager.construct_lookup_table()
        self.assertTrue(competition in file_manager.lookup_table)
        self.assertEqual(file_manager.lookup_table[competition]['metadata'], meta_file)
        self.assertEqual(file_manager.lookup_table[competition]['cleaned'], {cleaned_file})

    def test_extract_kernel_name(self):
        file_manager = S3FileManager()
        self.assertEqual(
            file_manager.extract_file_name('marcelolafeta/hash-code-drones-google-imt-vamo-pra-cima'),
            'hash-code-drones-google-imt-vamo-pra-cima'
        )
        self.assertEqual(file_manager.extract_file_name('marcelolafeta/'), '')
        self.assertEqual(file_manager.extract_file_name('marcelolafeta'), '')

if __name__ == '__main__':
    unittest.main()
