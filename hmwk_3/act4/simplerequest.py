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
import select
import time
from queue import Queue
from urllib.parse import urlparse
from multiprocessing import Process, Manager

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

        # if self.https is False:
        #     self.port = 80

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
        else is received.
        """

        while (self.data is not None) and (self.redir):
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
                    # if self.https is True:
                    #     self.port = 443
                    # else:
                    #     self.port = 80

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
            # REEE CHAIM
            https = False
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

            url_dict = {
                "host": self.host,
                "resource": f"{resource}",
                "https": False,
            }
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
        thread = threading.Thread(
            group=None, target=thread_work, args=(tasks, results)
        )
        thread.start()

    # Join on the queue tasks (that good good thread safe)
    tasks.join()

    return results


def link_filter(tag):
    """
    Some hot link filtering

    :param tag: A BS4 tag
    :return: the desired tag
    """
    return not email_filter(tag) and (
        tag.has_attr("href") and tag["href"] != "#"
    )


def email_filter(tag):
    """
    Some hot email filtering

    :param tag: A BS4 tag
    :return: the desired tag
    """
    return (
        tag.has_attr("href")
        and ("mailto:" in tag["href"])
        and ("@" in tag["href"])
        and (tag["href"].split("@")[1].count(".") > 0)
    )


def better_parse_url(url):
    return urlparse(url)


def new_crawl_worker(linksToHit, linksVisited, emails, scope, getemails=True):
    """
    This function is for the worker thread that handles the scraping of emails
    This funciton can also be used to harvest urls instead of emails by
    passing getemails=False

    :param linksToHit: The list of links that need to visited
    :param linksVisited: The list of links visited
    :param emails: A list to hold emails
    :param scope: The string of the scope to stay between
    :param getemails: whether or not to get emails, defaults to True
    """

    wait = True
    starttime = time.time()

    while len(linksToHit) > 0 or wait:
        try:
            wait = False

            try:
                link = linksToHit.pop()
                starttime = time.time()

            except IndexError:
                minutes, seconds = divmod((time.time() - starttime), 60)

                if minutes > 1:
                    print("Thread decided to quit....")
                    break
                else:
                    wait = True
                    continue

            linksVisited.append(link)
            link = better_parse_url(link)

            if link.scheme == "https":
                port = 443
                https = True
            else:
                port = 80
                https = False

            req = SimpleRequest(
                link.netloc, resource=link.path, port=port, https=https
            )

            req.render()
            req.send()
            req.redirects()

            soup = bs4.BeautifulSoup(req.data["body"], "html.parser")

            foundlinks = soup.find_all(link_filter)

            # Get emails
            if getemails:
                foundemails = soup.find_all(email_filter)

                for email in foundemails:
                    email = (
                        email["href"]
                        .replace("mailto:", "")
                        .strip()
                        .split("?")[0]
                        .lower()
                    )
                    depth = link.path.count("/")

                    if ";" in email:
                        for e in email.split(";"):
                            if "@" in e:
                                for x in emails:
                                    _, pp = x
                                    if e == pp:
                                        found = True
                                        break
                                if not found:
                                    emails.append((depth, e))
                                    print(e)
                    else:
                        if "@" in email:
                            # i is a list of emails
                            found = False
                            for j in emails:
                                # j are the emails in the i email list
                                # _ is depth, k is an email
                                _, k = j
                                if email == k:
                                    found = True
                                    break
                            if not found:
                                emails.append((depth, email))
                                print(email)
            else:
                scope = link.netloc

            for x in foundlinks:
                x = better_parse_url(x["href"])
                path = x.path

                while "//" in path:
                    path = path.replace("//", "/")

                if (scope in x.netloc) or (
                    (x.netloc == "" and path != "")
                    and (
                        ":" not in path and "@" not in path and "#" not in path
                    )
                ):
                    path = path.lower().strip()

                    if (path) and (path[0] == "/"):
                        fullLink = f"{link.scheme}://{link.netloc}{path}"
                    else:
                        fullLink = (
                            f"{link.scheme}://{link.netloc}{link.path}/{path}"
                        )

                    fullLink = fullLink.rstrip("/")
                    if (
                        fullLink not in linksToHit
                        and fullLink not in linksVisited
                    ):
                        # 6 is not a magic number... change my mind
                        # it is fucking math
                        if fullLink.count("/") > 6:
                            continue
                        linksToHit.append(fullLink)
        except Exception:
            # Do what I thought I coded you to do you piece of shit
            continue


def new_crawl(scope):
    """
    A better crawl function than the first one that I wrote

    :param scope: The scope to stay in ("rit.edu")
    """

    threads = []
    manager = Manager()

    linksToHit = manager.list()
    linksVisited = manager.list()
    emails = manager.list()

    linksToHit.append("https://www.rit.edu")

    for x in range(10):
        thread = Process(
            target=new_crawl_worker,
            args=(linksToHit, linksVisited, emails, scope),
        )
        threads.append(thread)
        thread.start()

    new = Process(target=shit_emails_to_file, args=(emails,))
    new.start()
    threads.append(new)

    for thread in threads:
        thread.join()


def shit_emails_to_file(ems):
    """
    As you can see... I am very upsetti with this hmwk...

    This function is the little boi thread. It is run by a thread
    that yeets emails into the correct files. It reads the emails
    from the workers that are writting emails to the "emails" list

    :param ems: Because I need an ambulance... its the shared
    email tuples list with the searching thread
    """

    shit = []
    while True:
        time.sleep(0.1)
        for depthEmailTuple in ems:
            dep, em = depthEmailTuple
            # plop is a singular email.... reeeeeeee
            path = f"./depth{dep}"
            if em not in shit:
                with open(path, "a+") as fd:
                    fd.write(em + "\n")
                shit.append(em)


def shit_urls_to_file(linkbois):
    """
    This function reads the urls that are written by the worker threads
    in the list "linksVisited" and writes them to a file with proper
    formatting. It makes sure there are no duplicates written.

    :param linkbois: The shared list that the workers are writing links to
    """

    seen = []
    path = "./urls"
    while True:
        time.sleep(0.1)
        for l in linkbois:
            l = better_parse_url(l).path

            for unit in l.split("/"):
                if (unit is not None) and (unit not in seen):
                    seen.append(unit)
                    print(unit)
                    with open(path, "a+") as fd:
                        fd.write("/" + unit + "\n")
