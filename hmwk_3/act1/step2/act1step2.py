#!/usr/bin/env python

#
# Name: Simon Buchheit
# Date: October 6, 2019
#
# CSEC-380 : hmwk3 : Act1 Part 1
#
# Purpose: This script scrapes the site:
#               https://www.rit.edu/computing/directory?term_node_tid_depth=4919
#
#           and collects all the pictures of staff and downloads them. It does
#           this using threads to accomplish the task faster
#


import simplerequest
import bs4
import multiprocessing
import os


def download_images(link):

    vals = simplerequest.parse_url(link)
    print(vals)

    r = simplerequest.SimpleRequest(vals["host"], port=443, resource=vals["resource"], https=vals["https"])
    r.render()
    r.send()
    r.redirects()

    with open("./staff_pics/" + vals["resource"].split("/")[-1], "wb") as fd:
        fd.write(r.data["body"])


def get_image_links(images):

    # List of image links
    links = []

    for tag in images:
        links.append(str(tag['data-src']).strip("\r\naa2f\r\n"))

    return links


def main():

    # Make a GET request for the page
    r = simplerequest.SimpleRequest("www.rit.edu", port=443, resource="/computing/directory?term_node_tid_depth=4919", https=True, conn="close")
    r.render()
    r.send()

    # Make the soup!
    soup = bs4.BeautifulSoup(r.data["body"], "html.parser")

    # Find all "img" tags
    images = soup.find_all("img", {"class": "card-img-top"})

    # Get the image urls from the images list
    links = get_image_links(images)

    # Make the directory
    try:
        os.mkdir("./staff_pics")
    except FileExistsError:
        pass

    # Threading shenanigans
    for link in links:
        download_images(link)


if __name__ == '__main__':
    main()
