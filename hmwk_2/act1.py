# /usr/bin/env python

#
# Name: Simon Buchheit
# Email: scb5436@rit.edu
#
# File: act1.py
#
# Purpose: This is my implementation for act_1 of homework 2 for CSEC-380
#

import simplerequest


def main():
    r = simplerequest.SimpleRequest(
        "csec380-core.csec.rit.edu", port=82, type="POST"
    )
    r.render()
    r.send()

    print(simplerequest.parse_value(r.data, "flag is"))


if __name__ == "__main__":
    main()
