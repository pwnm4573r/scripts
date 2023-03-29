import argparse
import logging
import os
import shutil
import time

def sync_folders(source, replica):
    """
    Synchronize source and replica folders.
    """
    for root, directories, files in os.walk(source):
        relative_root = os.path.relpath(root, source)
        replica_root = os.path.join(replica, relative_root)

        # This checks for corresponding path in replica folder and if it doesn't exist, cresates it.
        for dir in directories:
            replica_dir = os.path.join(replica_root, dir)
            if not os.path.exists(replica_dir):
                os.makedirs(replica_dir)
                logging.info(f"Created directory: {replica_dir}")

        # This checks for missing or older version of files in replica folder and creates/updates these files.
        # We use copy2 because it also copies metadata, which we need for comparing file versions using the .getmtime method and update if neccessary.
        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_root, file)

            if not os.path.exists(replica_file):
                shutil.copy2(source_file, replica_file)
                logging.info(f"Copied file: {source_file} to {replica_file}")
            elif os.path.getmtime(source_file) > os.path.getmtime(replica_file):
                shutil.copy2(source_file, replica_file)
                logging.info(f"Updated file: {source_file} to {replica_file}")

    # This checks for paths and files present in the replica and if they are not present in the source folder, removes them from replica.
    for root, directories, files in os.walk(replica):
        relative_root = os.path.relpath(root, replica)
        source_root = os.path.join(source, relative_root)

        for file in files:
            replica_file = os.path.join(root, file)
            source_file = os.path.join(source_root, file)

            if not os.path.exists(source_file):
                os.remove(replica_file)
                logging.info(f"Removed file: {replica_file}")

        for dir in directories:
            replica_dir = os.path.join(root, dir)
            source_dir = os.path.join(source_root, dir)
            
            if not os.path.exists(source_dir):
                shutil.rmtree(replica_dir)                      
                logging.info(f"Removed directory: {replica_dir}")

def main():
    # This defines the command line argument parser and sets 4 arguments.
    parser = argparse.ArgumentParser(description="Synchronize two folders.")
    parser.add_argument("source", help="Source folder")
    parser.add_argument("replica", help="Replica folder")
    parser.add_argument("interval", type=int, help="Synchronization interval (in seconds)")
    parser.add_argument("logfile", help="Path to the log file")
    args = parser.parse_args()

    # Configure logging both to the log file and to the console.
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s", handlers=[logging.FileHandler(args.logfile), logging.StreamHandler()])

    # Performs folder sync periodically 
    while True:
        logging.info(f"Started synchronization of {args.source} to {args.replica}")
        sync_folders(args.source, args.replica)
        logging.info(f"Finished synchronization of {args.source} to {args.replica}")
        time.sleep(args.interval)

if __name__ == "__main__":
    main()