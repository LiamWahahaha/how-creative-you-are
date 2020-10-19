import unittest
from modules.file_manager import S3FileManager

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

if __name__ == '__main__':
    unittest.main()
