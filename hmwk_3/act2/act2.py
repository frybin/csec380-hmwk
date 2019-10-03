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


def main():
    # Sweet sweet initial req
    req = simplerequest.SimpleRequest("www.rit.edu", port=443, https=True)
    req.render()
    req.send()

    # Start the soup!
    print("[+] starting initial crawl to depth 1...")
    soup = bs4.BeautifulSoup(req.data["body"], "html.parser")
    tags = soup.find_all("a")

    # Get links from hrefs
    links = []
    for tag in tags:
        # Some anchors don't have "href" throwing exceptions
        try:
            links.append(tag["href"])
        except KeyError:
            pass

    # Start the crawl!
    allLinks = simplerequest.crawl(req, links, "rit.edu")

    print(len(allLinks))



if __name__ == "__main__":
    main()
