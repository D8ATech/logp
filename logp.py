#!/usr/bin/env python3
import argparse
import sys
from os import listdir
import os
import concurrent.futures
from time import gmtime, strftime
import datetime
from datetime import timedelta
from datetime import datetime
from datetime import timezone
import gitactivity
from glob import glob
from os import system, name
import re
import sys
import time
import logging

class logp():

    def clear(self):
        if name == 'nt':
            _ = system('cls')
        else:
            _ = system('clear')

    def get_files(self, paths):
        """Gets the list of files that are to be processed"""
        filenames = []
        logging.debug("filenames: {}".format(filenames))
        for path in paths:
            path = path + "/atlassian*access*.log"
            filenames.extend(glob(path))
        return filenames

    def outputResults(self):
        self.clear()
        if self.clones.counter > 0:
            self.clones.display(self.howMany, self.output, self.output_File, self.graph)
        if self.sclones.counter > 0:
            self.sclones.display(self.howMany, self.output, self.output_File, self.graph)
        if self.fetches.counter > 0:
           self.fetches.display(self.howMany, self.output, self.output_File, self.graph)
        if self.pushes.counter > 0:
            self.pushes.display(self.howMany, self.output, self.output_File, self.graph)
        if self.refs.counter > 0:
            self.refs.display(self.howMany, self.output, self.output_File, self.graph)
            print (" ")
            print("Some Additional Details about Ref Advertisements:")
            print("HTTP(s) Refs: {0:8,d}".format(self.httpRef))
            print("SSH Exp Refs: {0:8,d}".format(self.sshExpRef))
            print("SSH Imp Refs: {0:8,d}".format(self.sshImpRef))
            print("Mismatch : {0:8,d}".format(self.missmatch))
            print(" ")
        if self.scmLinesProcessed > 0:
            print("Percentage of Requests that are refs: %2.0f" % (((self.httpRef + self.sshExpRef + self.sshImpRef)/self.scmLinesProcessed)*100))

    def finalize(self, output):
        logging.debug("Processing complete, displaying output")
        self.outputResults()
        if output != "file":
            if self.skipped_transactions > 0:
                print("{} skipped transactions".format(self.skipped_transactions))
    
    def process_File(self, file):
        Entry = {}
        output_pattern = re.compile(r"o[@*]")
        scm_pattern = re.compile(r"scm")
        ssh_pattern = re.compile(r" ssh ")
        http_pattern = re.compile(r" http[s]* ")
        http_unauth = re.compile(r" 401 ")
        external_pattern = re.compile(r"git[/\'\"]")

        ref_http_pattern = re.compile(r"/info/refs")
        fetch_pattern = re.compile(r"fetch[ ,]")
        clone_pattern = re.compile(r" clone[ ,](?! shallow)")
        sclone_pattern = re.compile(r" clone, shallow")
        push_pattern = re.compile(r"push[ ,]")
        ref_ssh_exp_pattern = re.compile(r"refs,")          

        found = False

        localClones = gitactivity.gitactivity("Clones")
        localSclones = gitactivity.gitactivity("Shallow Clones")
        localFetches = gitactivity.gitactivity("Fetches")
        localPushes = gitactivity.gitactivity("Pushes")
        localRefs = gitactivity.gitactivity("HTTP Ref Advertisements")

        local_stats = {'local_linesProcessed': 0,
            'local_outgoingLinesProcessed': 0,
            'local_scmLinesProcessed': 0,
            'local_skipped_transactions': 0,
            'local_httpRef': 0,
            'local_sshExpRef': 0,
            'local_sshImpRef': 0,
            'local_missmatch': 0}

        with open(file, 'r') as currentfile:
            logging.debug("===================")
            logging.debug("file: {}".format(file))
            logging.debug("----------")

            for line in currentfile:
                try:
                    local_stats['local_linesProcessed'] += 1
                    
                    logging.debug("01 - local_linesProcessed: {}".format(local_stats['local_linesProcessed']))
                    logging.debug("-----")
                    
                    found = False

                    # First check if there is an o[@*] in the line.  This is because we only want to process
                    # the outgoing part of the log
                    match = output_pattern.search(line)
                    if match:
                        local_stats['local_outgoingLinesProcessed'] += 1                        
                        logging.debug("02 - local_outgoingLinesProcessed: {}".format(local_stats['local_outgoingLinesProcessed']))
                        logging.debug("-----")

                        # Second check if the line is an scm request (and not a rest request)
                        isSSH = ssh_pattern.search(line)
                        scmMatch = scm_pattern.search(line)
                        if scmMatch:
                            isAuthed = http_unauth.search(line)
                            if isAuthed:
                                scmMatch = False

                        if scmMatch or isSSH:
                            logging.debug("03 - is either an scm or ssh match")
                            logging.debug("-----")
                            local_stats['local_scmLinesProcessed'] += 1
                            logging.debug("04 - local_scmLinesProcessed: {}".format(local_stats['local_scmLinesProcessed']))
                            logging.debug("-----")

                            # A match was found so now split up the line into its separate components as we will only
                            # pass certain fields to the object
                            try:
                                fields = [x.strip() for x in line.split('|')]
                                logging.debug("05 - fields: {}".format(fields))
                                logging.debug("-----")
                            except Exception as e:
                                logging.debug("EXCEPTION: Could not split")
                                logging.debug(e)
                                logging.debug("-----")

                            # Next we need to make sure that this is an external request.  For now this is looking for
                            # ".git"  May need to find a better way to determine this
                            try:
                                externalMatch = external_pattern.search(fields[5])
                                logging.debug("externalMatch: {}".format(externalMatch))
                                externalMatch = True
                            except Exception as e:
                                logging.debug("EXCEPTION: Failed External Match")
                                logging.debug(e)
                                logging.debug("-----")
                                externalMatch = False

                            if externalMatch:
                                # Now we need to filter out the project and repository this requires that we first
                                # figure out if the request is HTTP or SSH

                                if isSSH:
                                    # The request was sent over SSH so split us the 6th column to grab out just the
                                    # project/repository
                                    try:
                                        split_repo_fields = fields[5].split(' ')
                                        split_repo_second = split_repo_fields[3]    
                                    except Exception as e:
                                        logging.debug("EXCEPTION: Couldn't split SSH entry")
                                        logging.debug(e)
                                        logging.debug("-----")
                                        proceed = False

                                    try:
                                        split_repo_second_fields = split_repo_second.split('\'')
                                    except Exception as e:
                                        logging.debug("EXCEPTION: Couldn't split SSH second field")
                                        logging.debug("%s", split_repo_second)
                                        logging.debug(e)
                                        logging.debug("-----")
                                        proceed = False
                                    
                                    try:
                                        split_repo = split_repo_second_fields[1].strip('/')
                                        proceed = True
                                    except Exception as e:
                                        logging.debug("Couldn't strip / from SSH entry")
                                        logging.debug("base value: %s", split_repo_second_fields)
                                        logging.debug(e)
                                        logging.debug("-----")
                                        proceed = True
                                else:
                                    # The request is not SSH so check to make sure it is HTTP this should capture all but
                                    # a tiny fraction of transactions.
                                    isHTTP = http_pattern.search(line)
                                    if isHTTP:
                                        # The transaction is HTTP so split up the 6th column of fields to extract the
                                        # project/repository.  Store this in split_repo variable
                                        try: 
                                            split_repo_fields = fields[5].split(' ')
                                            split_repo_second = split_repo_fields[1]
                                            split_repo_second_fields = split_repo_second.split('/')
                                            split_repo = split_repo_second_fields[2]+"/"+split_repo_second_fields[3]
                                            proceed = True 

                                        except Exception as e:
                                            logging.debug("EXCEPTION: Couldn't split for HTTP entry")
                                            logging.debug(e)
                                            logging.debug("-----")
                                            proceed = False
                                    else:
                                        # The request is not HTTP or SSH so we basically skip adding the line to the
                                        # statistics, this happens when the access logs roll over in the middle of a
                                        # transaction
                                        logging.debug("ERROR: Request is not HTTP(s) or SSH, something has alredy gone wrong")
                                        proceed = False
    
                                        local_stats['local_skipped_transactions'] += 1
                                        logging.debug("06 - local_skipped_transactions: {}".format(local_stats['local_skipped_transactions']))
                                        logging.debug("-----")

                                # If we are able to proceed with adding data to the appropriate object the get to it
                                if proceed:
                                    # in case the request has been performed by an anonymous user,
                                    # the access log will contain "-" as the username.
                                    # Replacing "-" with "<anonymous user>" for clarity.
                                    if fields[3] == "-":
                                        user = "<anonymous user>"
                                    else:
                                        user = fields[3]

                                    # Build up the entry dictionary with only the information that is needed.
                                    # status and time are included now for future development
                                    Entry = {'ip':fields[0], 'repo':split_repo, 'user':user}
                                    
                                    logging.debug("Entry: {}".format(Entry))
                                    logging.debug("-----")

                                    # Check if this is a HTTP Ref.  For many instances HTTP Refs are likely the most numberous.  Since we
                                    # must check for SSH Refs last as they are the catch all I picked this order to try to stop looking faster
                                    matchHttpRef = ref_http_pattern.search(line)
                                    if matchHttpRef:
                                        local_stats['local_httpRef'] += 1
                                        localRefs.add_entry(**Entry)
                                        found = True
                                    else:
                                        found = False

                                    # Next check if line is a fetch, but only if we have determined that it is not an httpRef    
                                    if not found:
                                        matchFetch = fetch_pattern.search(line)
                                        if matchFetch:
                                            localFetches.add_entry(**Entry)
                                            found = True
                                        else:
                                            found = False

                                    # Next check if line is a clone or shallow clone, but only if we have determined that it is not a fetch
                                    if not found:
                                        matchClone = clone_pattern.search(line)
                                        if matchClone:
                                            # Yes this was a clone so process it as such
                                            localClones.add_entry(**Entry)
                                            found = True
                                        else:
                                            # Not a Clone so check if it is a shallow clone
                                            matchShallow = sclone_pattern.search(line)
                                            if matchShallow:
                                                localSclones.add_entry(**Entry)
                                                found = True
                                            else:
                                                found = False

                                    if not found:
                                        matchPush = push_pattern.search(line)
                                        if matchPush:
                                            localPushes.add_entry(**Entry)
                                            found = True
                                        else:
                                            found = False

                                    if not found:
                                        matchSSH = ssh_pattern.search(line)
                                        if matchSSH:
                                            matchRefs = ref_ssh_exp_pattern.search(line)
                                            if matchRefs:
                                                    local_stats['local_sshExpRef'] += 1
                                                    localRefs.add_entry(**Entry)
                                                    found = True
                                            else:
                                                # Not a explicit SSH Ref so it must be an implicit Ref
                                                local_stats['local_sshImpRef'] += 1
                                                localRefs.add_entry(**Entry)
                                                found = True
                                        else:
                                            local_stats['local_missmatch'] += 1
                                            logging.debug("ERROR: Mismatch found line is: {}".format(line))
                                            logging.debug("----------")
                                            found = False

                                    Entry.clear()
                except:
                    logging.debug('Log Line Read Failure.  Skipping')
                                
            return [local_stats,
                    localClones, 
                    localSclones, 
                    localFetches, 
                    localPushes, 
                    localRefs]

    def buildMasterData(self, returnData, internalObject):
        for key, value in returnData.ipaddresses.items():
            ipaddress = internalObject.ipaddresses.setdefault(key, 0)
            internalObject.ipaddresses[key] = ipaddress + value
        
        for key, value in returnData.repositories.items():
            repository = internalObject.repositories.setdefault(key, 0)
            internalObject.repositories[key] = repository + value

        for key, value in returnData.users.items():
            users = internalObject.users.setdefault(key, 0)
            internalObject.users[key] = users + value
        
        internalObject.counter += returnData.counter        

    def __init__(self, paths, howMany, output, output_File, graph, useThreads, workers):
        """the logp Object.  This is the main Object"""

        self.clones = gitactivity.gitactivity("Clones")
        self.sclones = gitactivity.gitactivity("Shallow Clones")
        self.fetches = gitactivity.gitactivity("Fetches")
        self.pushes = gitactivity.gitactivity("Pushes")
        self.refs = gitactivity.gitactivity("HTTP Ref Advertisements")

        self.howMany = howMany
        self.output = output
        self.output_File = output_File
        self.graph = graph
        self.useThreads = useThreads
        self.workers = workers

        self.linesProcessed = 0
        self.outgoingLinesProcessed = 0
        self.scmLinesProcessed = 0
        self.skipped_transactions = 0

        list_of_files = self.get_files(paths)
        self.httpRef = 0
        self.sshExpRef = 0
        self.sshImpRef = 0
        self.missmatch = 0

        returnList = {}

        start_time = time.monotonic()
        self.clear()

        logging.debug("__init__ started")

        # START NEW LOGIC BASED ON BEING THREADED OR NOT
        if self.useThreads:
            executor = concurrent.futures.ProcessPoolExecutor(max_workers=self.workers)
            tasks=[]
            logging.debug("Threads are being used")

        for file in list_of_files:
            if self.useThreads:
                tasks.append(executor.submit(self.process_File, file))
            else:
                self.process_File(file)
                logging.debug("Not using threads, File just processed: {}".format(file))
        
        if useThreads:
            logging.debug("tasks: {}".format(tasks))
            for task in concurrent.futures.as_completed(tasks):
                #print("{}".format(task.result()[0]))
                # 20 = INFO, 10 = DEBUG 
                if logging.getLogger().getEffectiveLevel() < 20:
                    print('.', end='', flush=True)                
                
                returnList = task.result()[0]

                self.buildMasterData(task.result()[1], self.clones)
                self.buildMasterData(task.result()[2], self.sclones)
                self.buildMasterData(task.result()[3], self.fetches)
                self.buildMasterData(task.result()[4], self.pushes)
                self.buildMasterData(task.result()[5], self.refs)

                self.linesProcessed += returnList.get('local_linesProcessed')
                self.outgoingLinesProcessed += returnList.get('local_outgoingLinesProcessed')
                self.scmLinesProcessed += returnList.get('local_scmLinesProcessed')
                self.skipped_transactions += returnList.get('local_skipped_transactions')
                self.httpRef += returnList.get('local_httpRef')
                self.sshExpRef += returnList.get('local_sshExpRef')
                self.sshImpRef += returnList.get('local_sshImpRef')
                self.missmatch += returnList.get('local_missmatch')

        if self.outgoingLinesProcessed > 0:
            logging.debug("Processing complete, displaying output")
            self.outputResults()
        else:
            logging.debug("No lines were processed")

        end_time = time.monotonic()
        elapsed_time = end_time - start_time
        if output != "file":
            print("{} skipped transactions".format(self.skipped_transactions))
            print("Execution time: {0:.3f} seconds".format(elapsed_time))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", help="Required, full path to the location of the atlassian*access*.log files", nargs='+', type=str)
    #parser.add_argument("-t", "--threads", help="Enable Multi Threading", action="store_true")
    #parser.add.argument("-w", "--workers", help="Define the number of worker threads that can be used, default is 12", type=int, default=12)
    parser.add_argument("-n", "--number", help="Optional, number of results you want returned in the output, default is 10", type=int, default=10)
    parser.add_argument("-o", "--output", help="Optional, Can be either screen, file or jira, Default is jira", type=str, choices=["screen", "file", "jira"], default="jira")
    parser.add_argument("-f", "--file", help="Optional, the filename to output the results")
    parser.add_argument("-g", "--graph", help="Optional, show bar graphs", action="store_true")
    parser.add_argument("-d", "--debug", help="Optional, Enables debug logging to the screen", action="store_true")
    args = parser.parse_args()

    dir_path = args.path
    howMany = args.number
    output = args.output
    #workers = args.workers
    if os.cpu_count() > 1:
        workers = os.cpu_count()-1
    else:
        workers = 1

    if args.debug:
        logging.basicConfig(format='%(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.DEBUG)
        logging.debug("Debug Logging Enabled:")
        logging.debug("dirpath: %s", dir_path)
        logging.debug("howMany: %s", howMany)
        logging.debug("output:  %s", output)
    else:
        logging.basicConfig(format='%(levelname)s:%(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    
    if output == "file":
        output_file = args.file
    else:
        output_file = ""

    graph = args.graph

    useThreads = True

    logging.debug("Starting -------------------------------------- ")

    r = logp(dir_path, howMany, output, output_file, graph, useThreads, workers)

    if output != "file":
        if r.linesProcessed == 0:
            print ("Done.  Nothing to process")
        else:
            print(" ")
            print ("Processed {:,} Total Lines".format(r.linesProcessed))
            print ("Processed {:,} Outgoing Replies".format(r.outgoingLinesProcessed))
            print ("Processed {:,} scm replies".format(r.scmLinesProcessed))
            print ("Done.")

if __name__ == '__main__':
    main()