#!/usr/bin/env python

#
# Name: Simon Buchheit
# Date: October 6, 2019
#
# CSEC-380 : hmwk3 : Act2
#
# Purpose: This script crawls the site: www.rit.edu
#          to a depth of 4. On each page emails are harvested
#          and saved.
#

import simplerequest
import bs4
import os


def main():
    # Sweet sweet initial req
    req = simplerequest.SimpleRequest("www.rit.edu", port=443, https=True)
    req.render()
    req.send()

    # Start the soup!
    soup = bs4.BeautifulSoup(req.data["body"], "html.parser")
    tags = soup.find_all("a")

    href = []
    for tag in tags:
        try:
            href.append(tag["href"])
        except KeyError:
            pass

    # pass the list of links and host to crawler function
    simplerequest.crawl(req.host, href)


if __name__ == "__main__":
    main()
