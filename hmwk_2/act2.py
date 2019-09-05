# /usr/bin/env python

#
# Name: Simon Buchheit
# Email: scb5436@rit.edu
#
# File: act2.py
#
# Purpose: This is my implementation for act_2 of homework 2 for CSEC-380
#

import simplerequest


def main():
    r = simplerequest.SimpleRequest(
        "csec380-core.csec.rit.edu", port=82, type="POST", resource="/getSecure"
    )
    r.render()
    r.send()

    token = simplerequest.parse_value(r.data, "Token is:")

    r = simplerequest.SimpleRequest(
        "csec380-core.csec.rit.edu",
        port=82,
        type="POST",
        resource="/getFlag2",
        body=f"token={token}",
    )
    r.render()
    r.send()

    print(r.data)


if __name__ == "__main__":
    main()
