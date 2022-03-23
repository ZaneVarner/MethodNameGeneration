import pprint
from parse import *
import os
from os import walk


def main():
    # Specify the path to a single source file (for now)
    source_folder_path = '../data/code2seq/java-small/training'
    #source_file_path = \
    #    f'{source_folder_path}/training/elasticsearch/BulkProcessor.java'
    #source_file_path = '../data/code2seq/sampleClass.java'

    # Parsing all java files in training dataset
    arr = os.listdir(source_folder_path)
    print(arr)

    for dir in arr:
        source_file_path_outer = source_folder_path + '/'
        source_file_path_outer += dir
        javaFiles = os.listdir(source_file_path_outer)
        
        for file in javaFiles:
            source_file_path = source_file_path_outer + "/" + file
            
            # List of dictionaries containing the contexts of each method
            methods = parse_source_file(source_file_path)
            pp = pprint.PrettyPrinter(indent=2, sort_dicts=False)
            pp.pprint(methods)

            with open('java_small.txt', 'w') as writefile:
                writefile.write(pprint.pformat(methods, indent=4))
    
if __name__ == '__main__':
    main()
