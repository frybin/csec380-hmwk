#!/usr/bin/env python

#
# Name: Simon Buchheit
# Date: October 6, 2019
#
# CSEC-380 : hmwk3 : Act3
#
# Purpose: This script crawls the compaines from "companies.csv"
#          to a depth of 4. On each page the links are split on the "/"
#          and saved to a file
#


import simplerequest
from multiprocessing import Process, Manager


def main():
    threads = []
    manager = Manager()

    linksVisited = manager.list()
    # Ununsed
    emails = manager.list()

    linksToSearch = manager.list()
    with open("companies.csv", "r") as fd:
        lines = fd.readlines()

        for line in lines:
            linksToSearch.append(line.strip().split(",")[1])

    for x in range(10):
        thread = Process(target=simplerequest.new_crawl_worker, args=(linksToSearch, linksVisited, emails, None, False))
        threads.append(thread)
        thread.start()

    new = Process(target=simplerequest.shit_urls_to_file, args=(linksVisited,))
    new.start()
    threads.append(new)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()