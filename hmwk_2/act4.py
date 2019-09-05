#!/usr/bin/env python

#
# Name: Simon Buchheit
# Email: scb5436@rit.edu
#
# File: act4.py
#
# Purpose: This is my implementation for act_4 of homework 2 for CSEC-380
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
        resource="/createAccount",
        body=f"token={token}&username=oneNutW0nder",
        agent="Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    )
    r.render()
    r.send()

    password = simplerequest.parse_value(r.data, "password is")
    password = simplerequest.url_encode(password)

    r = simplerequest.SimpleRequest(
        "csec380-core.csec.rit.edu",
        port=82,
        type="POST",
        resource="/login",
        body=f"token={token}&username=oneNutW0nder&password={password}",
        agent="Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    )
    r.render()
    r.send()

    print(simplerequest.parse_value(r.data, "flag is"))


if __name__ == "__main__":
    main()
