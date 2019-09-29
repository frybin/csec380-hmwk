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
import os


def save_images(req, count):
    """
    This function taks a reqeust object, and saves the body of the response
    as a binary file. It uses the URI and a count to name the file

    :param req: A single request object
    :param count: A count value to append to filename
    """

    with open(
        "./staff_pics/" + req.resource.split("/")[-1] + str(count), "wb"
    ) as fd:
        fd.write(req.data["body"])


def get_image_links(images):
    """
    This function takes the initial soup parsing for img tags and
    further parses it to get just the links that we want to send
    a GET request to.

    :param images: A list of img tags from the dank soup
    :return: Returns a list of just links to send GET reqs to
    """

    # List of image links
    links = []

    for tag in images:
        # I got one link with this dumb fucking pattern
        if "\r\naa2f\r\n" in tag["data-src"]:
            tmp = str(tag["data-src"]).split("\r\naa2f\r\n")
            dumb = tmp[0] + tmp[1]
            links.append(dumb)
        # Everything else is fine /shrug
        else:
            links.append(str(tag["data-src"]).strip("\r\n"))

    return links


def main():

    # Make a GET request for the page
    r = simplerequest.SimpleRequest(
        "www.rit.edu",
        port=443,
        resource="/computing/directory?term_node_tid_depth=4919",
        https=True,
        conn="close",
    )
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

    # Make a list of hosts, resources, and https
    vals = []
    for link in links:
        vals.append(simplerequest.parse_url(link))

    # Create list of request objects
    requests = []
    for data in vals:
        requests.append(
            simplerequest.SimpleRequest(
                data["host"],
                port=443,
                resource=data["resource"],
                https=data["https"],
                follow=True,
            )
        )

    # Thread the sending of prepared requests
    # Save the finished requests
    new = []
    new = simplerequest.thread_requests(requests)

    # Send count to append to file name because same name
    # will over write... caused me 1 hour of headaches
    count = 0
    for req in new:
        save_images(req, count)
        count += 1


if __name__ == "__main__":
    main()
