#!/usr/bin/env python

#
# Name: Simon Buchheit
# Date: October 6, 2019
#
# Purpose: This script scrapes the site https://www.rit.edu/study/computing-security-bs 
#           and collects the course number and corresponding course name. If there
#           is no name with the number or vice versa the data will not be recorded.
#           This script will output a CSV file with the data
#

import bs4
import simplerequest

def main():

    r = simplerequest.SimpleRequest("www.rit.edu", port=443, resource="/study/computing-security-bs", https=True)
    print(r.render())
    r.send()

    print(r.data)


if __name__ == '__main__':
    main()