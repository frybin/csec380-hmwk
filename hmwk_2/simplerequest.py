# /usr/bin/env python

#
# Name: Simon Buchheit
# Email: scb5436@rit.edu
#
# File: simplerequest.py
#
# Purpose: This file contains my own library for creating, sending, and dealing
#           with HTTP requests.
#

import socket

# Dict of URL encodings for conversions
URL_ENC_DICT = {"&": "%26", "=": "%3D"}


class SimpleRequest:
    """
    SimpleRequst allows easy creation and sending of HTTP requests tailored to
    the user's needs
    """

    def __init__(
        self,
        host,
        port="80",
        type="GET",
        resource="/",
        body="",
        contentType="application/x-www-form-urlencoded",
        request="",
        agent="reeeeeee",
    ):
        """
        Sets up the variables that will build the user's custom HTTP request
        
        Args:
            host (str): The host that you are sending the request to.
            port (str, optional): Specify a nonstandard port. Defaults to '80'
            type (str, optional): The type of request to send: GET, POST, etc
            resource (str, optional): The resource being requested. 
                               Defaults to '/'.
            body (str, optional): Information to include in HTTP body. 
                               Defaults to ''.
            contentType (str, optional): Type for the content body. 
                               Defaults to 'application/x-www-form-urlencoded'.
            request (str, optional): Optionaly provide another request to build 
                               onto. Rarely used. Defaults to ''.
            agent (str, optional): Optionaly provide a custom user agent. 
                               Defaults to 'reeeeeee'.
        """
        self.host = host
        self.port = port
        self.type = type
        self.resource = resource
        self.request = request
        self.body = body
        self.contentType = contentType
        self.agent = agent

        # Create a socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def render(self):
        """
        Render builds the HTTP request using values provided by the user
        
        Returns:
            self.request(str): The full HTTP request properly formatted 
        """
        self.request += (
            str(self.type) + " " + str(self.resource) + " HTTP/1.1\r\n"
        )
        self.request += (
            "Host: " + str(self.host) + ":" + str(self.port) + "\r\n"
        )
        self.request += "User-Agent: " + str(self.agent) + "\r\n"
        self.request += "Accept: text/html\r\n"
        self.request += "Accept-Language: en-US\r\n"
        self.request += "Accept-Encoding: text/html\r\n"
        self.request += "Connection: keep-alive\r\n"
        self.request += (
            "Content-Type: "
            + str(self.contentType)
            + "; charset=utf-8\r\n"
        )
        self.request += "Content-Length: " + str(len(self.body)) + "\r\n"
        self.request += "\r\n"
        self.request += str(self.body)

        return self.request

    def send(self):
        """
        Send will send the HTTP request, wait for the response and 
        return the data from the response
        
        Returns:
            self.data(str): The HTTP response from the server
        """
        self.sock.connect((self.host, self.port))
        self.sock.sendall(self.request.encode("utf-8"))
        self.data = self.sock.recv(4096).decode("ascii")

        return self.data


def parse_value(request, value):
    """
    parses an HTTP request and returns the desired value
    
    Args:
        request (str): HTTP request that you want to get a value from
        value (str): Part of the string describing the value. 
                            Ex: Finding a token in the body-->value="Token is:"
    
    Returns:
        str: Returns the desired value
    """

    request = request.split("\r\n")

    if ":" in value:
        for field in request:
            if value in field:
                return (":".join(field.split(":")[1:]).strip()).strip('"')
    else:
        for field in request:
            if value in field:
                return (field.split()[-1]).strip('"')


def url_encode(s):
    """
    Takes a string and URL encodes it using the URL_ENC_DICT
    
    Args:
        s (str): The string to URL encode
    
    Returns:
        encoded (str): The URL encoded string
    """
    encoded = ""
    for c in s:
        if c in URL_ENC_DICT:
            encoded += URL_ENC_DICT[c]
        else:
            encoded += c

    return encoded
