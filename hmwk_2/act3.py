#
# Name: Simon Buchheit
# Email: scb5436@rit.edu
#
# File: act3.py
#
# Purpose: This is my implementation for act_3 of homework 2 for CSEC-380
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
        resource="/getFlag3Challenge",
        body=f"token={token}",
    )
    r.render()
    r.send()

    captcha = simplerequest.parse_value(r.data, "following:")

    # Possible operator list
    operators = ["+", "-", "//", "*"]

    # Find the operator in the captcha
    op = list(filter(lambda operator: (operator in captcha), operators))
    op = op[0]

    # Get the numbers from the captcha
    captcha = captcha.split(op)

    if op == "//":
        captcha = int(captcha[0]) // int(captcha[1])
    elif op == "+":
        captcha = int(captcha[0]) + int(captcha[1])
    elif op == "-":
        captcha = int(captcha[0]) - int(captcha[1])
    elif op == "*":
        captcha = int(captcha[0]) * int(captcha[1])
    else:
        print("Operator unknown....")

    r = simplerequest.SimpleRequest(
        "csec380-core.csec.rit.edu",
        port=82,
        type="POST",
        resource="/getFlag3Challenge",
        body=f"token={token}&solution={captcha}",
    )
    r.render()
    r.send()

    print(simplerequest.parse_value(r.data, "flag is"))


if __name__ == "__main__":
    main()
