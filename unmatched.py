import argparse
import sys
import os
import datetime
import re
import logging

from glob import glob

class Unmatched:

    def __init__(self, path):
        self.path = path

    def get_files(self):
        """Gets the list of files that are to be processed
           Exclude the atlassian-access.log one which will be added later
           after the sorting completed."""
        searchpath = self.path + "/atlassian*access-*.log"
        filenames = glob(searchpath)

        # grab the date from the filename
        def dateSort(x):
            base=os.path.basename(x)
            x = os.path.splitext(base)[0]
            x = x[27:]
            x = x[:10]
            return x

        # grab the sequential number part from the filename
        def numSort(x):
            base=os.path.basename(x)
            x = os.path.splitext(base)[0]
            x = x[38:]
            return int(x)


        filenames = sorted(filenames, key = numSort)
        filenames = sorted(filenames, key = dateSort)

        # add atlassian-bitbucket-access.log as the last file
        # if it exists
        searchpath = self.path + "/atlassian*access.log"
        if len(glob(searchpath)) == 1:
            filenames.append(glob(searchpath)[0])

        return filenames

    def findUnmatched(self):
        list_of_files = self.get_files()
        output_pattern = re.compile(r"i[@*]")
        incoming={}

        for file in list_of_files:
            logging.debug(f'Processing file {os.path.basename(file)}')

            with open(file, 'r') as currentfile:
                for line in currentfile:

                    fields = line.split('|')
                    if len(fields) > 1:
                        try:
                            linedata = [x.strip() for x in line.split('|')]
                        except Exception as e:
                            logging.error("EXCEPTION: Could not split")
                            logging.error(e)

                        transactionId = linedata[2]
                        transactionId = transactionId[2:]

                        try:
                            match = output_pattern.search(linedata[2])
                        except Exception as e:
                            logging.error('EXCEPTION: Could not search')
                            logging.error(e)

                        if match:
                            incoming[transactionId] = line[:-1]
                        else:
                            try:
                                incoming.pop(transactionId)
                            except KeyError:
                                pass

        return incoming

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Required, full path to the location of the atlassian*access*.log files", type=str)
    parser.add_argument("-d", "--debug", help="Optional, Enables debug logging to the screen", action="store_true")
    args = parser.parse_args()

    path = args.path

    if args.debug:
        logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.DEBUG)
        logging.debug("Debug Logging Enabled:")
        logging.debug(f"path: {path}")
    else:
        logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S', level=logging.WARNING)

    unMatched = Unmatched(path)
    notFound = unMatched.findUnmatched()

    print("The following incoming transactions were not found to have a matching outgoing response")
    for unmatched_request in notFound.values():
        print(f"{unmatched_request}")

if __name__ == '__main__':
    main()