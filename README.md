# README.md

## VERSION 0.1.1 is Here:

### What's Changed

- added in more robust error exceptions when the log lines have invalid data or are truncated in unexpected ways
- fixed issue where http requests were not counted properly
- fine tuned multi core to use only use max cores - 1 so that the entire system is not bogged down
- added the ability to analyze log files in multiple directories

### Previous Changes v0.1.0

- Output will only show types that are found. If there are no pushes in the logs then the pushes section will not be displayed.
- Complete re-write of the logp class to better handle logging and class methods
- JIRA output will now be the default (use -o screen to display normal output to the screen)
- Shallow Clones should now be counted and displayed correctly
- And the biggest change is, logp.py is now multi-processor capable. This means that on the new Mac Book Pros with 12 CPU’s we are able to process 9GB of Access logs in under 2 minutes. Before that same analysis could take as much as 3.5 minutes for logp.py or over 18 minutes for logp.sh (no one shoould still be using logp.sh).

### Performance Comparison:

Performance improvments were realized by optimizing the code, not making checks that have already been decided (if the line is a Ref Adv then don't also check to see if it is a clone) but mostly by assigning each file to be evaluatted to its own process.

The side effect of this is that when there are fewer large files, multi process doesn't have as large of an impact. The other side effect of this is that to get these fast responses CPUs (all CPUs) were between 88 - 99% utilized for the entire time. This is in contrast to the old version where only one CPU would reach 88 - 99% utilized.

Below is the test data showing the impact of small, medium, & massive data sets along with a massive data set run on a local disk compared to an external USB disk.

#### Small Data Set

GB of Access logs
832MB of Access logs

- 3,281,094 Total Lines
- 1,640,442 Outgoing Replies
- 556,269 scm replies

logp.py (Version 0.1.0) : 7 seconds
logp.py (Version 0.0.7) : 15 seconds
logp.sh : 1 minute 14 seconds

#### Medium Data Set

9GB of Access logs

- 31,033,112 Total Lines
- 15,516,556 Outgoing Replies
- 10,694,487 scm replies

logp.py (Version 0.1.0) : 1 minute 48 seconds
logp.py (Version 0.0.7) : 3 minutes 23 seconds
logp.sh : 18 minutes 30 seconds

#### Massive Data Set - External Hard Drive

19GB of Access logs

- 77,760,293 Total Lines
- 38,880,026 Outgoing Replies
- 12,693,455 scm replies

logp.py (Version 0.1.0) : 10 minutes 9 seconds
logp.py (Version 0.0.7) : 10 minutes 49 seconds
logp.sh : 1 hour 55 minutes 4 seconds

To show the impact that a slow external (USB) drive has on the processing I copied the 19GB of data to my local hard drive and re-ran all three methods:

#### Massive Data Set - Internal Hard Drive

19GB of Access logs

- 77,760,293 Total Lines
- 38,880,026 Outgoing Replies
- 12,693,455 scm replies

logp.py (Version 0.1.0) : 2 minutes 56 seconds
logp.py (Version 0.0.7) : 6 minutes 14 seconds
logp.sh : 30 minutes 8 seconds

Your results may vary based on the number of CPU's, other processes running on your system, and the distribution of the different SCM requests that are in the logs being analyzed.

# VERSION 0.0.7 f3a0309 (Now deprecated)

This is the rewrite of logp.sh in Python.

Why would you want to use the python version instead of the bash version?

One reason, speed. When analyzing a complete dataset we clocked the following speeds.

Dataset Size: 3.6GB
Total Number of lines in the access logs: 12,449,948
Total Number of o[@\*] lines: 6,224,966
Total Number of SCM Outgoing responses: 5,441,290

Bash logp.sh - 7 minutes 22 seconds (442 seconds)
Python logp.py - 1 minute 35 seconds ( 95 seconds) - 4.65 times faster

Another reason, more information. logp.sh provided lots of good information but logp.py provides more.
As an example here is the output for refs from logp.sh:

            {panel:title=Total Ref Advertisements}
            Number of refs: 5,399,926
            {panel}

            {panel:title=Top 20 Ref Advertisement IP Addresses}
            10.53.81.191 : 5,399,388
            10.53.81.191 : 535
            {panel}

Here is the output from logp.py:

            h1. HTTP Ref Advertisements
            h2. Total Requests: 5,399,390
            h2. ==========================================
            h3. Top 10 IP Addresses
            {noformat}
            5,399,388 - 10.53.81.191,127.0.0.1
            {noformat}

            h2. ==========================================
            h3. Top 10 Repositories
            {noformat}
                156,492 - proja/repo1.git
                133,550 - projb/repo2.git
                127,868 - projc/repo3.git
                106,760 - projd/repo4.git
                102,400 - proje/repo5.git
                95,920 - projf/repo6.git
                92,937 - projg/repo7.git
                91,911 - projh/repo8.git
                91,348 - proji/repo9.git
                91,169 - projj/repo0.git
            {noformat}

            h2. ==========================================
            h3. Top 10 Users
            {noformat}
            3,278,766 - -
                395,481 - userp
                342,794 - userq
                258,482 - userr
                212,502 - users
                175,207 - usert
                93,446 - userv
                88,088 - userw
                83,130 - userx
                78,547 - usery
            {noformat}


            Some Additional Details about Ref Advertisements:
            HTTP(s) Refs: 5,399,390
            SSH Exp Refs:        0
            SSH Imp Refs:        0


            Percentage of Requests that are refs 99 percent

Here is the output from log.py with the --graph option

            h1. HTTP Ref Advertisements
            h2. Total Requests: 5,399,390 
            h2. ==========================================
            h3. Top 10 IP Addresses
            {noformat}
            10.53.81.191,127.0.0.1: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 5,399,388

            {noformat}
            These represent 100.00% of total requests
             
            h2. ==========================================
            h3. Top 10 Repositories
            {noformat}
            proja/repo1.git: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 156,492
            projb/repo2.git: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 133,550
            projc/repo3.git: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 127,868
            projd/repo4.git: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 106,760
            proje/repo5.git: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 102,400
            projf/repo6.git: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 95,920
            projg/repo7.git: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 92,937
            projh/repo8.git: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 91,911
            proji/repo9.git: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 91,348
            projj/repo0.git: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 91,169

            {noformat}
            These represent 20.19% of total requests
             
            h2. ==========================================
            h3. Top 10 Users
            {noformat}
            userp: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 395,481
            userq: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 342,974
            userr: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 258,482
            users: ▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇▇ 212,502
            usert: ▇▇▇▇▇▇▇▇▇▇▇▇▇ 175,207
            userv: ▇▇▇▇▇▇▇ 93,446
            userw: ▇▇▇▇▇▇ 88,088
            userx: ▇▇▇▇▇▇ 83,130
            usery: ▇▇▇▇▇ 78,547

            {noformat}
            These represent 32.00% of total requests


            Some Additional Details about Ref Advertisements:
            HTTP(s) Refs: 5,399,390
            SSH Exp Refs:        0
            SSH Imp Refs:        0


            Percentage of Requests that are refs 99 percent

Clearly with so much more information and more than 4 times faster logp.py is superior is every way.

# How to use logp.py

logp.py required Python 3.6 or higher. Assuming that your python is installed and symlinked as python3 then the following is how to run logp.py

usage: `python3 logp.py [-h] [-n NUMBER] [-o {screen,file,jira}] [-f FILE] [-g] [-d] path`

positional arguments:
paths Required, full path to the location of the
atlassian*access*.log files. To analyze more than one directory include each path separated by a space

optional arguments:

-h, --help show this help message and exit

-n NUMBER, --number NUMBER
Optional, number of results you want returned in the output, default is 10

-o {screen,file,jira}, --output {screen,file,jira}
Optional, Can be either screen, file or jira, Default is jira

-f FILE, --file FILE Optional, the filename to output the results

-g, --graph Optional, show bar graphs

-d, --debug Optional, Enables debug logging to the screen

`python3 logp.py /Users/yourname/cases/PS/ps-1234/Zip1/Applicaiton-logs /Users/yourname/cases/PS/ps-1234/Zip2/Applicaiton-logs -o screen`

- runs the program using data from the specified locations and outputing the results in a format that can be read easily on the screen.

# Dependencies:
* [Python3](https://www.python.org/downloads/) 

* [termgraph](https://pypi.org/project/termgraph/)

        pip3 install termgraph --user

Or Install dependencies using the requirements.txt file

        pip3 install -r requirements.txt --user