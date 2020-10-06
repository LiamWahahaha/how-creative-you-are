FROM = 'from'
IMPORT = 'import'
AS = 'as'
COMMA = ','
COMMENT = '#'
CONTINUATION_CHARACTER = '\\'
DOT = '.'


def extract_imported_package(line):
    """
    handled case:
    1. import x0                  => x0
    2. import x0.y0               => x0
    3. import x0,x1               => x0, x1
    4. import x0   ,   x1         => x0, x1
    5. import x0 as y1, x1 as y2  => x0, x1
    6. from x0 import y0          => x0 (next version)
    7. from x0.y0 import z0       => x0 (next version)
    8. from x0 import (           => x0 (next version)
        x1, x2, x3
    )
    9. from x0 import (           => x0 (next version)
        x1,
        x2,
        x3
    )
    10. import x0, \\             => x0, x1 (next version)
       x1
    """
    should_combine_next_line = False
    text = line.strip().partition(COMMENT)[0].split()
    imported_packages = set()

    if text and text[0] == IMPORT:
        should_skip = False
        for chunk in text[1:]:
            # handle the situation of import <chunk> as <skipped chunk>
            if should_skip:
                should_skip = False
                # if the <skipped chunk> contains breakline
                if chunk and chunk[-1] == CONTINUATION_CHARACTER:
                    should_combine_next_line = True
                    break
                continue
            if chunk == AS:
                should_skip = True
                continue

            # case: import <chunk> , <chunk>
            if chunk == COMMA:
                continue

            # extract packages from chunk
            should_combine_next_line, packages = extract_from_chunk(chunk)
            imported_packages = imported_packages.union(packages)
            if should_combine_next_line:
                break

    return should_combine_next_line, imported_packages

def extract_imported_package_from_next_line(line):
    """
    This is a dummy function
    """
    has_next_line = False
    imported_packages = set()
    return has_next_line, imported_packages

def extract_from_chunk(chunk):
    """Extract packages from chunk

    Parameters:
    chunk (str): a chunk is a string without space

    Returns:
    bool: should_combine_next_line
    set: packages
    """
    packages = set()
    should_combine_next_line = False

    if not chunk:
        return should_combine_next_line, packages

    if chunk[-1] == CONTINUATION_CHARACTER:
        should_combine_next_line = True

    if COMMA in chunk:
        packages = packages.union(extract_from_chunk_contains_comma(chunk))
    else:
        packages.add(extract_from_normal_chunk(chunk))

    return should_combine_next_line, packages

def extract_from_normal_chunk(chunk):
    """Deal with the following cases:
    'x0'
    'x0.y0'
    """
    return chunk if DOT not in chunk else chunk.split('.')[0]

def extract_from_chunk_contains_comma(chunk):
    """Deal with the following cases:
    'x0,x1.y0,x2'
    'x0,x1,'
    'x0,x1,x2,...,xn,\\'
    """
    packages = set()

    for content in chunk.split(','):
        if not content or content == CONTINUATION_CHARACTER:
            continue
        package = extract_from_normal_chunk(content)
        packages.add(package)

    return packages

def is_notebook_code_cell(notebook_cell):
    try:
        return notebook_cell['cell_type'] == 'code'
    except:
        return False

def extract_source_code_from_notebook(notebook_cell):
    """Return the source code block"""
    return notebook_cell['source']

class Print:
    """Print message with color"""
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    @classmethod
    def info(cls, msg):
        """Print out green msg"""
        print(f'{cls.OKGREEN}{msg}{cls.ENDC}')

    @classmethod
    def error(cls, msg):
        """"Print out red msg"""
        print(f'{cls.FAIL}{msg}{cls.ENDC}')
