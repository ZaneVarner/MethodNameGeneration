import pprint
from parse import *


def main():
    # Specify the path to a single source file (for now)
    source_folder_path = '../data/code2seq/java-small'
    #source_file_path = \
    #    f'{source_folder_path}/training/elasticsearch/BulkProcessor.java'
    source_file_path = '../data/code2seq/sampleClass.java'

    # List of dictionaries containing the contexts of each method
    methods = parse_source_file(source_file_path)

    # Print the results in a pretty format
    pp = pprint.PrettyPrinter(indent=2, sort_dicts=False)
    pp.pprint(methods)


if __name__ == '__main__':
    main()
