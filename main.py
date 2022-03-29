import pprint
from parse import *
import os
from os import walk
import threading
import time
from multiprocessing import Process, Pool
from functools import partial

'''
create a method that gets filepaths as arguements
create 4 threads and give each of them 1/4 of our filepaths 
obtain 4 txt file outputs (can send the code the zane if its working to this point)
merge the files
'''

def main():
    # Specify the path to a single source file (for now)
    source_folder_path = '../data/code2seq/java-small/training'
    #source_file_path = \
    #    f'{source_folder_path}/cassandra/SecondaryIndexManager.java'
    #source_file_path = '../data/code2seq/sampleClass.java'

    # Parsing all java files in training dataset
    arr = os.listdir(source_folder_path)
    files = []
    
    # creates a list of filepaths
    for dir in arr:
        source_file_path_outer = source_folder_path + '/'
        source_file_path_outer += dir
        javaFiles = os.listdir(source_file_path_outer)
        
        for file in javaFiles:
            source_file_path = source_file_path_outer + "/" + file
            files.append(source_file_path)
    
    # to be deleted (for testing)
    #files = files[:100]

    # determine chunk size and divide the filepath list
    chunk_size = 20
    chunks = [files[x:x+chunk_size] for x in range(0, len(files), chunk_size)]
    
    # creating arguements to pass to the processes
    arguements = []
    for i in range(len(chunks)):
        arguements.append((chunks[i],i))

    # multiprocessing
    pool = Pool()       
    #pool.map(partial(main_parse, chunks), range(len(chunks)))  
    pool.starmap(main_parse,arguements)
    pool.close()
    pool.join()

    print("Done!")


def main_parse(filepaths, thr_no):
    """A method that gets filepaths of Java files and calls parse_source_file.
    thr_no: thread number to be used in the name of the txt file.
    """

    for source_file_path in filepaths:
        # Delete files if they already exist
        if os.path.isfile('java_small'+str(thr_no)+'.txt'):
            os.remove('java_small'+str(thr_no)+'.txt')
        else:
            pass

        # List of dictionaries containing the contexts of each method
        methods = parse_source_file(source_file_path)
        pp = pprint.PrettyPrinter(indent=2, sort_dicts=False)

        with open('java_small'+str(thr_no)+'.txt', 'w') as writefile:
            writefile.write(pprint.pformat(methods, indent=4))


if __name__ == '__main__':
    main()
