import pprint
from parse import *
import os
from os import walk
import threading
import time

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
    files = files[:100]

    # determine chunk size and divide the filepath list
    chunk_size = 20
    chunks = [files[x:x+chunk_size] for x in range(0, len(files), chunk_size)]

    threads = []
    for i in range(len(chunks)):
        #print(len(chunks[i]))
        ti = threading.Thread(target=main_parse, args=(chunks[i],i,))
        threads.append(ti)
        ti.start()
        print('thread '+str(i)+' started.')
    
    # all threads are executed at this point
    for i in threads:
        i.join()

    print("Done!")

if __name__ == '__main__':
    main()
