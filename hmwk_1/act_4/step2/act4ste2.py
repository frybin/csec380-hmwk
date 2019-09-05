#!/usr/bin/env python

#
# Name: Simon Buchheit
# Email: scb5436@rit.edu
#
# File: act4ste2.py
#
# Purpose: Given a range of IPs, iterate through the range
#           and return the IPs that are proxy servers.
#

import sys
import requests
import netaddr
import multiprocess


def usage():
    print("Usage: ./act4ste2.py <starting_address> <ending_address>")
    exit()


def sendit(addr):

    addr = str(netaddr.IPAddress(addr))
    # Common ports
    ports = [80, 8080, 8000, 88, 8888, 808]

    for port in ports:
        proxies = {"http": str(addr) + ":" + str(port)}

        try:
            r = requests.get(
                "http://csec.rit.edu", proxies=proxies, timeout=2.5
            )

            if (
                r.status_code == 200
                and "Department of Computing Security | Golisano College of Computing and Information Sciences | RIT"
                in r.text
            ):
                print(f"{addr}:{str(port)}")
                return
            else:
                continue
        except requests.exceptions.RequestException as e:
            pass


def main():

    if len(sys.argv) != 3:
        usage()

    begin = netaddr.IPAddress(sys.argv[1])
    end = netaddr.IPAddress(sys.argv[2])

    # Thread shenanigans here
    p = multiprocess.Pool(569)
    p.map(sendit, range(int(begin), int(end) + 1))
    p.close()
    p.join()


if __name__ == "__main__":
    main()
