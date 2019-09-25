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


def get_courseNums(chonker):
    
    # List to hold the course numbers 
    courseNums = []

    for tag in chonker:
        # Check for None stuff
        if tag.contents[1].contents[0] is not None:
            # Check for newlines
            if tag.contents[1].contents[0] != "\xa0":
                # Make list to get just course nums
                # Course nums don't have spaces in name
                pos_course = tag.contents[1].contents[0].string.strip().split()

                # Check for just course name and remove the dumb "Course" value
                if (len(pos_course) == 1) and (pos_course[0] != "Course"):
                    courseNums += pos_course

    return courseNums

def main():

    # Send that sweet sweet request to get the goodies
    r = simplerequest.SimpleRequest("www.rit.edu", port=443, resource="/study/computing-security-bs", https=True)
    r.render()
    r.send()

    # Start the soup!
    soup = bs4.BeautifulSoup(r.data, "html.parser")

    # Chonker is the list that holds all "tr" tags
    chonker = []
    chonker = soup.find_all('tr')
        
    # parse the chonker for courseNumbers
    courseNums = get_courseNums(chonker)


if __name__ == '__main__':
    main()