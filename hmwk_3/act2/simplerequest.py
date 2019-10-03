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
import threading
import bs4
import re
import queue
import select
import os
from queue import Queue

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

        if self.https is False:
            self.port = 80

        # Wrap sock in TLS if HTTPS is true
        if self.https:
            self.sock = ssl.wrap_socket(self.sock, ssl_version=ssl.PROTOCOL_TLS)

        # self.sock.setblocking(0)
        self.sock.settimeout(10)
        try:
            self.sock.connect((self.host, self.port))
        except (socket.timeout, socket.gaierror, socket.error):
            self.sock.close()
            self.data = None
            return self.data

        self.sock.sendall(self.request.encode("utf-8"))

        # Shenanigans to make sure we get all data from the socket
        # because python sockets are dumb... web is dumb... reeeee
        data = b""
        ready = select.select([self.sock], [], [], 10)
        if ready[0]:
            data_block = self.sock.recv(4096)
            while data_block != b"":
                data += data_block

                ready = select.select([self.sock], [], [], 10)
                if ready[0]:
                    data_block = self.sock.recv(4096)
        else:
            self.data = None
            self.sock.shutdown(1)
            self.sock.close()
            return self.data

        self.sock.shutdown(1)
        self.sock.close()

        # response holds the entire response, headers and body
        self.response = data

        # Split on \r\n to seperate headers and body
        tmp = self.response.split(b"\r\n\r\n", maxsplit=1)

        # make that sweet sweet dict
        try:
            self.data = {"headers": tmp[0].decode("ascii"), "body": tmp[1]}
        except IndexError:
            self.data = None
            return self.data

        # Get status code
        self.status = parse_value(self.data["headers"], "HTTP/1.1")

        # Check for redirect
        if ((self.status == "302") or (self.status == "301")):
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

        while self.redir and self.data is not None:
            # Follow the redirect
            follow = parse_value(self.data["headers"], "Location:")
            if follow is not None:
                parsed = self.parse_url(follow)

                # If host == None path was found not a new link
                if parsed["host"] is None:
                    follow = f"{self.parsed['resource']}"

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

    def parse_url(self, url):
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
            url = url.lstrip("https://")
            https = True
        elif "http" in url:
            url = url.lstrip("http://")
            https = False
        else:
            # Path found... not a full URL
            # Properly make resource based on relative or absolute path
            if (self.resource != "/") and (url[0] == "/"):
                resource = url
            elif (self.resource == "/") and (url[0] == "/"):
                resource = url
            elif (self.resource != "/") and (url[0] != "/"):
                resource = self.resource + "/" + url
            else:
                resource = self.resource + url

            url_dict = {"host": self.host, "resource": f"{resource}", "https": self.https}
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


def thread_work(tasks, results):
    """
    This function is the target of threads to send requests.
    It will carry out each request/thread to completion then
    end.

    :param tasks: The full queue of tasks that was created
    a tasks consists of (idx, request[idx])
    :param results: A new list to hold the results of the threading shenanigans
    """

    while not tasks.empty():
        task = tasks.get()
        task[1].render()
        task[1].send()
        task[1].redirects()
        # Save the results
        results[task[0]] = task[1]
        tasks.task_done()

    return True


def thread_requests(requests, maxthreads=50):
    """
    This function takes a list of request objects and will spawn
    a thread for each object that will make the request outlined
    by each object.

    :param requests: A list of request objects that are ready to rock'n'roll
    :param maxthreads: The maximum number of threads to spawn
    """

    # How many threads!?
    numThreads = min(len(requests), maxthreads)

    # Make a bunch of tasks (queue objects)
    tasks = Queue(maxsize=0)
    for idx in range(len(requests)):
        tasks.put((idx, requests[idx]))

    # Make a list for results
    results = [None for i in range(len(requests))]
    for idx in range(len(numThreads)):
        # Full send the threads
        thread = (threading.Thread(group=None, target=thread_work, args=(tasks, results)))
        thread.start()

    # Join on the queue tasks (that good good thread safe)
    tasks.join()

    return results


def crawl_work(tasks, results, scope):
    """
    This function will carry out the work for each thread spawned
    from crawl(). Each thread will be in charge of parsing the HTML
    to find the links for their respective pages

    :param tasks: Queue objects for all the jobs task=(idx, requests[idx])
    :param results: Place to store the results
    :param scope: The scope to stay in
    """

    # Do the tasks
    while not tasks.empty():
        task = tasks.get(timeout=5)
        # Shenanigans because web is dumb
        while True:
            try:
                task[1].render()
                task[1].send()
                if task[1].data is None:
                    continue
                task[1].redirects()
                if task[1].data is None:
                    continue
            except (ConnectionResetError, socket.gaierror, TimeoutError, queue.Empty):
                continue
            else:
                break

        # Save the body
        body = task[1].data["body"]

        # Try decoding... reeeeeeeeee things break
        try:
            body.decode("utf-8")
        except UnicodeDecodeError:
            body.decode("latin-1")

        # Make soup for the thread
        soup = bs4.BeautifulSoup(body, "html.parser")

        tags = soup.find_all("a")

        links = []
        for tag in tags:
            try:
                links.append(tag["href"])
            except KeyError:
                pass

        base = re.escape(scope)
        # Matches relative or absolute RIT links
        valid = re.compile("^(https?://[a-zA-Z0-9_\-\.]*" + base + ".*/?|)(/.*)")
        links_in_scope = []
        # for link in links:
        #     if valid.search(link):
        #         links_in_scope.append(link)
        links_in_scope = [valid.search(i).group() for i in links
                            if valid.match(i)]
        results[task[0]] = links_in_scope
        print(f"Done with page {task[0]}")
        tasks.task_done()
    return True


def crawl(init_req, links, scope, depth=4, maxthreads=50):
    """
    This function crawls through a site confined by the "scope". It
    takes a list of links from an initial request that should be
    made from the originating script. This is because sending one
    request is no problem. After receiving the params, it will
    build the requests and spawn threads to crawl each page for links.
    It will then save all links that are visited and make sure duplicates
    are not saved.

    :param init_req: request object from the first request
    :param links: The initial list of links from the first request
    :param scope: The scope of the crawler EX. (rit.edu)
    :param depth: How deep to crawl, defaults to 4
    :param maxthreads: The max threads to spawn, defaults to 50
    """

    # For saving searched links
    searched = []

    # Since this function takes the list of links from the first page
    # We will do (depth-1), since we are starting at zero, to ensure
    # we go the required depth. We are effectively starting at a depth
    # of one

    for x in range(depth):
        print(f"[+] starting crawl to depth {x+2}...")

        # Prune the initial list of links for scope valid links
        # also parse the link and create a request object
        requests = []
        for link in links:
            if (link):
                # Check scope and path
                if (scope in link) or (link[0] == "/"):
                    urlDict = init_req.parse_url(link)
                    requests.append(SimpleRequest(urlDict["host"], resource=urlDict["resource"], port=443, https=urlDict["https"]))

        numThreads = min(len(requests), maxthreads)
        # Make a bunch of tasks (queue objects)
        tasks = Queue(maxsize=0)
        for idx in range(len(requests)):
            tasks.put((idx, requests[idx]))

        # Make a list for results
        results = [None for i in range(len(requests))]
        for idx in range(numThreads):
            # Full send the threads
            thread = (threading.Thread(group=None, target=crawl_work, args=(tasks, results, scope)))
            thread.start()

        # That good good thread stuff
        tasks.join()
        print(len(results))

        # Updates
        print(f"[+] finished searched {len(requests)} links...")

        # Save searched links so we don't repeat
        searched.extend(links)

        # Save the new links
        links = []
        for result in results:
            for link in result:
                if (link not in links) and (link not in searched):
                    links.append(link)

        print(links)
        print(len(links))
        print(f"[+] beginning search of {len(links)} links...")
        # Loop with new "links" list

    return searched
