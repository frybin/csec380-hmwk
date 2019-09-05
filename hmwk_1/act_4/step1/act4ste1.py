#!/usr/bin/env python

#
# Name: Simon Buchheit
# Email: scb5436@rit.edu
#
# File: act4ste1.py
#
# Purpose: This script sends a get request to "csec.rit.edu"
#

import requests


def main():
    r = requests.get("http://csec.rit.edu")
    print(r)


if __name__ == "__main__":
    main()
