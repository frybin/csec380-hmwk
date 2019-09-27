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
        follow=True
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
            https (bool, optional): Whether or not to use TLS to wrap the socket 
                               Defaults to False
            ohterheaders (dict, optional): Additional user specified headers
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
        Render builds the HTTP request using values provided by the user

        Returns:
            self.request(str): The full HTTP request properly formatted 
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
        data = b''
        data_block = self.sock.recv(4096)
        while data_block != b'':
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
        if (self.status == "302") or (self.status == "301"):
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

        while (self.redir):
            # Follow the redirect
            follow = parse_value(self.data["headers"], "Location:")
            if (follow is not None):
                parsed = parse_url(follow)
                
                # If host == None path was found not a new link
                if (parsed["host"] == None):
                    follow = f"{parsed['resource']}"

                    # Shenanigans for just a path being passed back
                    tmp = self.resource.split("/")

                    # Parse the new resource value and update it in the request object
                    newResource = f"/{tmp[1]}/{follow}"
                    self.resource = newResource
                else:
                    # If a new url is found update the values
                    self.host = parsed["host"]
                    self.resource = parsed["resource"]
                    self.https = parsed["https"]
                    if (self.https is True):
                        self.port = 443

            # Rebuild the new request and send
            self.render()
            self.send()


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
    elif value == "HTTP/1.1":
        return (request[0].split()[1])
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


def parse_url(url):
    """
    This function takes a url and seperates it into the
    host and resource so that it is ready to use for a new
    request.

    :param url: A url in its raw form (https://example.com/robots.txt)
    :return: Returns a dict of the (host, resource, https)
    Example: ("host": example.com, "resource": /robots.txt, "https": False)
    """

    # Check if https or not
    if ("https" in url):
        url = url.strip("https://")
        https = True
    elif ("http" in url):
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
