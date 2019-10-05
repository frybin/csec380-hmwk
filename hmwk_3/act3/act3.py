import simplerequest
from multiprocessing import Process, Manager


def main():
    threads = []
    manager = Manager()

    linksVisited = manager.list()
    # Ununsed
    emails = manager.list()

    linksToSearch = manager.list()
    with open("companies.csv", "r") as fd:
        lines = fd.readlines()

        for line in lines:
            linksToSearch.append(line.strip().split(",")[1])

    for x in range(10):
        thread = Process(target=simplerequest.new_crawl_worker, args=(linksToSearch, linksVisited, emails, None, False))
        threads.append(thread)
        thread.start()

    new = Process(target=simplerequest.shit_urls_to_file, args=(linksVisited,))
    new.start()
    threads.append(new)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()