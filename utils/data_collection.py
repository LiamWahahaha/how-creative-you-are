def retrieve_kaggle_competitions_by_search(competition):
    page = 1
    upper_bound = 100
    stream = os.popen(f'kaggle competitions list -s {competition} -p {page} -v')
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

def retrieve_kernels_by_competition(competition_ref, kernel_type = 'notebook', language = 'python'):
    page = 1
    page_size = 100
    upper_bound = 1000
    universal_parameters = "--competition {} --page-size {} --kernel-type {} --language {}".format(
        competition_ref, page_size, kernel_type, language
    )

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

def pull_single_kernel_by_kernel_ref(kernel_ref, path = ''):
    pass

