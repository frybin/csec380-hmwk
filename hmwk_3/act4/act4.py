#!/usr/bin/env python

#
# Name: Simon Buchheit
# Date: October 6, 2019
#
# CSEC-380 : hmwk3 : Act4
#
# Purpose: This script is a "dirbuster" program.
#          It will use the "urls" file to enumerate possible
#          paths on the site http://csec380-core.csec.rit.edu:83/
#

import simplerequest
import time
from multiprocessing import Process, Manager


def discover(paths, host, port, found, allpaths):

    wait = True
    starttime = time.time()

    while len(paths) > 0 or wait:
        try:
            wait = False

            try:
                path = paths.pop()
                starttime = time.time()

            except IndexError:
                minutes, seconds = divmod((time.time() - starttime), 60)

                if minutes > 1:
                    print("Thread decided to quit...")
                    break
                else:
                    wait = True
                    continue

            # Make request
            # no redirects
            req = simplerequest.SimpleRequest(host, resource=path, port=port, https=False)
            req.render()
            req.send()
            req.redirects()
            # print(path)

            try:
                if (req.status == "200") and (path not in found):
                    if path.count("/") < 4:
                        print(path)
                        found.append(path)

                        if path != "/":
                            for p in allpaths:
                                if ".." not in p:
                                    paths.append(f"{path}{p}")
            except IndexError:
                continue
            else:
                continue
        except Exception:
            continue


def write_to_file(good):

    seen = []
    path = "./good.txt"
    while True:
        time.sleep(0.1)
        for p in good:
            if p not in seen:
                seen.append(p)
                with open(path, "a+") as sd:
                    sd.write(p + "\n")


def main():

    host = "csec380-core.csec.rit.edu"
    port = 83

    manager = Manager()

    paths = manager.list()
    found = manager.list()
    allpaths = manager.list()

    with open("./urls", "r") as fd:

        for line in fd.readlines():
            line = line.strip()

            if not line:
                continue
            if line[0] != "/":
                line = f"/{line}"

            paths.append(line)
            allpaths.append(line)

    threads = []
    for x in range(10):
        thread = Process(target=discover, args=(paths, host, port, found, allpaths))
        threads.append(thread)
        thread.start()

    # Write correct to a file
    writer = Process(target=write_to_file, args=(found,))
    writer.start()
    threads.append(writer)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()