import csv
import os
import time
from subprocess import Popen, PIPE

class KaggleScraper:
    def save_competition_meta_and_download_related_kernels(self, competition_ref, path='tmp/'):
        metadata = self.save_csv(competition_ref, path)
        kernel_refs = [record[0] for record in metadata]
        self.batch_download_kernel(kernel_refs, path)

    def batch_download_kernel(self, kernel_refs, path='tmp/'):
        time1 = time.perf_counter()
        for kernel_ref in kernel_refs:
            self.download_kernel(kernel_ref, path)
            time.sleep(5)
        time2 = time.perf_counter()
        print(f'Finished in { time2 - time1 } seconds')

    def download_kernel(self, kernel_ref, path='tmp/'):
        process = Popen(f'kaggle kernels pull {kernel_ref} -p {path}',
                        shell=True,
                        stderr=PIPE,
                        stdout=PIPE)
        stdout, stderr = process.communicate()
        exit_code = process.wait()
        print(stdout, stderr, exit_code)

    def retrieve_all_kaggle_competitions_by_search(self, competition):
        page = 1
        upper_bound = 100
        stream = os.popen(f'kaggle competitions list -s "{competition}" -p {page} -v')
        raw_output = stream.read()
        output = []

        while raw_output and raw_output != 'No competitions found\n' and page < upper_bound:
            output.append(raw_output)
            page += 1
            stream = os.popen(f'kaggle competitions list -s {competition} -p {page} -v')
            raw_output = stream.read()

        if page == upper_bound:
            print('competition search reaches upper bound')

        return output


    def retrieve_all_kernels_of_a_competition(self,
                                              competition_ref,
                                              kernel_type='notebook',
                                              language='python'):
        page = 1
        page_size = 100
        upper_bound = 1000
        universal_parameters = "--competition {} --page-size {} --kernel-type {} --language {}" \
                               .format(competition_ref, page_size, kernel_type, language)

        stream = os.popen(f'kaggle kernels list -p {page} {universal_parameters} -v')
        raw_output = stream.read()
        output = []

        while raw_output and raw_output != 'No kernels found\n' and page < upper_bound:
            output.append(raw_output)
            page += 1
            stream = os.popen(f'kaggle kernels list -p {page} {universal_parameters} -v')
            raw_output = stream.read()

        if page == upper_bound:
            print('kernels reach upper bound')

        return output

    def save_csv(self, competition, path='tmp/'):
        csv_text_list = self.retrieve_all_kernels_of_a_competition(competition)
        metadata = list()
        for content in csv_text_list:
            reader = csv.reader(content.splitlines(), delimiter=',')
            header = next(reader)
            if not metadata:
                header.extend(['competition', 'kernel'])
                metadata.append(header)

            for row in reader:
                new_row = row[:]
                kernel = row[0].split('/')[1] if len(row[0].split('/')) == 2 else ''
                new_row.extend([competition, kernel])
                metadata.append(new_row)

        with open(f'{path}{competition}.csv', mode='w') as csv_file:
            csv_writer = csv.writer(csv_file,
                                    delimiter=',',
                                    quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
            for row in metadata:
                csv_writer.writerow(row)

        return metadata
