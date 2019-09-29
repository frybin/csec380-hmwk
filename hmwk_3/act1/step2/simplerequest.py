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
import ssl

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
        port=80,
        type="GET",
        resource="/",
        body="",
        request="",
        agent="reeeeeee",
        https=False,
        conn="close",
        otherheaders={},
        follow=True,
    ):
        """
        Handles the setup for class variables and gets everything
        ready for the requests to be built

        :param host: FQDN of the target host EX. www.rit.edu
        :param port: Target port, defaults to 80
        :param type: Type of request to send, defaults to "GET"
        :param resource: This is the URI, defaults to "/"
        :param body: Any data to add to the body, defaults to ""
        :param request: A premade request, defaults to ""
        :param agent: The best user agent, defaults to "reeeeeee"
        :param https: True/False if site uses HTTPS, defaults to False
        :param conn: Keep alive the connection or not, defaults to "close"
        :param otherheaders: A dictionary of additional headers, defaults to {}
        :param follow: Whether or not to follow redirects, defaults to True
        """
        self.host = host
        self.port = port
        self.type = type
        self.resource = resource
        self.request = request
        self.body = body
        self.agent = agent
        self.https = https
        self.conn = conn
        self.otherheaders = otherheaders
        self.follow = follow

    def render(self):
        """
        Render builds the HTTP request based on the headers/values passed
        by the user

        :return: Returns a HTTP request in ASCII
        """

        # If we should follow requests destroy old request for rebuild
        # Clearing the request allows reusing the same request object
        if self.follow:
            self.request = ""

        self.request += f"{self.type} {self.resource} HTTP/1.1\r\n"
        self.request += f"Host: {self.host}\r\n"
        self.request += f"User-Agent: {self.agent}\r\n"
        self.request += f"Connection: {self.conn}\r\n"
        # Add other headers
        for key in self.otherheaders:
            self.request += f"{key}: {self.otherheaders[key]}\r\n"
        self.request += f"Content-Length: {str(len(self.body))}\r\n"
        self.request += "\r\n"
        self.request += str(self.body)

        return self.request

    def send(self):
        """
        Send will send the HTTP request, wait for the response and
        return the data from the response

        Returns:
            self.data(dict): Returns dictionary {"h": headers, "b", body}
        """

        # Create normal socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Wrap sock in TLS if HTTPS is true
        if self.https:
            self.sock = ssl.wrap_socket(self.sock, ssl_version=ssl.PROTOCOL_TLS)

        self.sock.connect((self.host, self.port))
        self.sock.sendall(self.request.encode("utf-8"))

        # Shenanigans to make sure we get all data from the socket
        # because python sockets are dumb... web is dumb... reeeee
        data = b""
        data_block = self.sock.recv(4096)
        while data_block != b"":
            data += data_block
            data_block = self.sock.recv(4096)

        # response holds the entire response, headers and body
        self.response = data

        # Split on \r\n to seperate headers and body
        tmp = self.response.split(b"\r\n\r\n")

        # make that sweet sweet dict
        self.data = {"headers": tmp[0].decode("ascii"), "body": tmp[1]}

        # Get status code
        self.status = parse_value(self.data["headers"], "HTTP/1.1")

        # Check for redirect
        if ((self.status == "302") or (self.status == "301")) and (
            self.follow is True
        ):
            # self.redir tell user that a redirect was encountered
            self.redir = True
        else:
            self.redir = False

        return self.data

    def redirects(self):
        """
        This function handles 301 and 302 status codes and follows
        the locations that are provided by the response

        It will continue following redirects until a 200 or something
        else is received. Links not tested... only paths
        """

        while self.redir:
            # Follow the redirect
            follow = parse_value(self.data["headers"], "Location:")
            if follow is not None:
                parsed = parse_url(follow)

                # If host == None path was found not a new link
                if parsed["host"] is None:
                    follow = f"{parsed['resource']}"

                    # Shenanigans for just a path being passed back
                    tmp = self.resource.split("/")

                    # Parse the new resource value and update it
                    # in the request object
                    newResource = f"/{tmp[1]}/{follow}"
                    self.resource = newResource
                else:
                    # If a new url is found update the values
                    self.host = parsed["host"]
                    self.resource = parsed["resource"]
                    self.https = parsed["https"]
                    if self.https is True:
                        self.port = 443
                    else:
                        self.port = 80

            # Rebuild the new request and send
            self.render()
            self.send()


def parse_value(request, value):
    """
    This function takes a request (usually just headers) and
    a value (usually a header) and returns the info for the value
    that was searched for.

    Note: This function can get the status code by passing "HTTP/1.1"
    as the value parameter.

    :param request: A HTTP request or response to parse
    :param value: The string to search for. EX. value="Date:"--> ret Date value
    :return: Returns the info from the associated value searched for
    """
    request = request.split("\r\n")

    if ":" in value:
        for field in request:
            if value in field:
                return (":".join(field.split(":")[1:]).strip()).strip('"')
    elif value == "HTTP/1.1":
        return request[0].split()[1]
    else:
        for field in request:
            if value in field:
                return (field.split()[-1]).strip('"')


def url_encode(s):
    """
    This function takes a string and returns the URL encoded version

    :param s: The string to url encode
    :return: Returns the URL encoded form of the original string
    """
    encoded = ""
    for c in s:
        if c in URL_ENC_DICT:
            encoded += URL_ENC_DICT[c]
        else:
            encoded += c

    return encoded


def parse_url(url):
    """
    This function takes a url and seperates it into the
    host and resource so that it is ready to use for a new
    request. Primarily used for following redirects

    :param url: A url in its raw form (https://example.com/robots.txt)
    :return: Returns a dict of the (host, resource, https)
    Example: ("host": example.com, "resource": /robots.txt, "https": False)
    """

    # Check if https or not
    if "https" in url:
        url = url.strip("https://")
        https = True
    elif "http" in url:
        url = url.strip("http://")
        https = False
    else:
        # Path found... not a full URL
        https = True
        url_dict = {"host": None, "resource": url, "https": https}
        return url_dict

    # Split on the /
    url = url.split("/")

    # Set HOST and RESOURCE
    host = url[0]
    tmp = url[1:]

    # Format resource
    resource = ""
    for val in tmp:
        resource += f"/{val}"

    url_dict = {"host": host, "resource": resource, "https": https}

    return url_dict
