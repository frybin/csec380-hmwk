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


def get_values(chonker):
    """
    This function parses the initial bs4 filter for the course numbers
    and the corresponding course names. If a course does not have a number
    or name it will not be saved. 
    
    :param chonker: The massive list from the intial filter from bs4
    :return: Returns a dictionary of course numbers and their 
    corresponding name
    """

    # Dict to hold the values
    values = {}
    
    # List to hold the course numbers 
    courseNums = []

    # Loop through the tags
    for tag in chonker:
        # Check for None stuff
        if (tag.contents[1].contents[0] is not None):

            # Check for newlines
            if (tag.contents[1].contents[0] != "\xa0"):

                # Make list to get just course nums
                # Course nums don't have spaces in name
                pos_course = tag.contents[1].contents[0].string.strip().split()

                # Check for just course name and remove the dumb "Course" value
                if (len(pos_course) == 1) and (pos_course[0] != "Course"):
                    # Save course number
                    courseNums = pos_course[0]
                    # Save corresponding course name
                    # find "div" tags where "class=course-name"
                    name = tag.contents[3].find_all("div", "course-name")[0].get_text().strip()

                    # Build dict
                    values[str(courseNums)] = str(name)
    
    return values
    

def write_csv(values):
    """
    This function simply creates a new file and writes the values dict
    to the new file in a CSV format
    
    :param values: Dictionary of courseNum:courseName
    """
    
    with open("./courses.csv", "w+") as fd:
        for key in values:
            fd.write(f"{key},{values[key]}\n")




def main():

    # Send that sweet sweet request to get the goodies
    r = simplerequest.SimpleRequest("www.rit.edu", port=443, resource="/study/computing-security-bs", https=True)
    r.render()
    r.send()

    # Start the soup!
    soup = bs4.BeautifulSoup(r.data, "html.parser")

    # Chonker is the list that holds all "tr" tags
    chonker = []

    # Find all "<tr>" tags with "class=hidden-row*"
    chonker = soup.find_all('tr', "hidden-row")
        
    # parse the chonker for courseNumbers
    values = get_values(chonker)

    # Create CSV value
    write_csv(values)


if __name__ == '__main__':
    main()