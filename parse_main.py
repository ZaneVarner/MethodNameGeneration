import math
import os
from multiprocessing import Process
from parse import *


def parse_main(dataset_dir_path, output_file_path, n_processes):
    # List of paths to every source file
    source_file_paths = gather_source_file_paths(dataset_dir_path)

    # Number of source files that each Process will parse and write
    block_size = math.ceil(len(source_file_paths) / n_processes)

    # Map each process index to the Process object
    processes = {}

    for i in range(n_processes):
        # Extract the section of the dataset for this Process
        block_start = i * block_size
        block_end = min((i + 1) * block_size, len(source_file_paths))
        block_source_file_paths = source_file_paths[block_start:block_end]

        # Temporary output file for this process
        block_output_file_path = f'./temp_{i}.txt'

        # Create and start the Process
        p = Process(
            target=parse_and_write_source_files,
            args=(block_source_file_paths, block_output_file_path, True, i,))
        p.start()

        # Keep track of the Process to join later
        processes[i] = p

    # Create a single output file to consolidate all Process results
    with open(output_file_path, 'w') as output_file:
        for i in range(n_processes):
            # Wait until this process has finished parsing and writing
            p = processes[i]
            p.join()
            
            # Copy the results of the Process to main output file
            block_output_file_path = f'./temp_{i}.txt'
            with open(block_output_file_path) as block_output_file:
                block_output = block_output_file.read()
                output_file.write(block_output)

            # Delete the temporary output file for the Process
            os.remove(block_output_file_path)


if __name__ == '__main__':

    dataset_dir_path = '../data/code2seq/java-small'
    output_file_path = '../data.txt'
    n_processes = 12

    parse_main(dataset_dir_path, output_file_path, n_processes)
