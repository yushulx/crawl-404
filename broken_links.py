import requests
import signal
import threading
from bs4 import BeautifulSoup
import urllib
import sys
import time

shutdown_event = None

def ctrl_c(signum, frame):
    """Catch Ctrl-C key sequence and set a shutdown_event for our threaded
    operations
    """

    global shutdown_event
    shutdown_event.set()
    raise SystemExit('\nCancelling...')

class Crawler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        file = None
        try:
            try:
                file = open('broken_link_file.txt', 'a')
            except:
                print 'Failed to open file.'

            if file != None:
                pages = self.readSiteMap()
                # pages = ['http://192.168.8.233/test.aspx'] # for test
                for page in pages:
                    if shutdown_event.isSet():
                        break;

                    links = self.readHref(page)
                    ret = self.crawlLinks(links, file)

                    if not ret:
                        break;

        except IOError:
            print "IOError"
        finally:
            if file:
                file.close()

    def readHref(self, url):
        links = []
        try:
            r = urllib.urlopen(url)
        except:
            print 'Failed to read url'
            return "Failed"

        soup = BeautifulSoup(r.read())

        elements = soup.select('a')
        for element in elements:
            try:
                link = element.get('href')
                if link.startswith('http'):
                    links.append(link)
            except:
                print 'href error!!!'
                continue

        return links

    def readSiteMap(self):
        pages = []
        r = None
        try:
            # r = urllib.urlopen("http://www.codepool.biz/sitemap.xml")
            r = urllib.urlopen("http://kb.dynamsoft.com/sitemap.xml")
        except:
            print 'Failed to read sitemap'
            return 'Failed'

        xml = r.read()

        soup = BeautifulSoup(xml)
        urlTags = soup.find_all("url")

        print "The number of url tags in sitemap: ", str(len(urlTags))

        for sitemap in urlTags:
            link = sitemap.findNext("loc").text
            pages.append(link)

        return pages

    def crawlLinks(self, links, file=None):
        for link in links:
            if shutdown_event.isSet():
                return None

            status_code = 0
            res = None

            print 'link: ', link

            try:
                res = urllib.urlopen(link)
            except:
                pass

            if not res:
                print 'cannot open ', link
                continue

            status_code = res.getcode()

            print 'status_code: ', status_code
            if (status_code == 200):
                continue

            if (status_code == 404):
                if file != None:
                    file.write(link + '\n')

            print str(status_code), ': ', link

        return "Done"

def crawlPages():
    global shutdown_event
    shutdown_event = threading.Event()

    signal.signal(signal.SIGINT, ctrl_c)

    crawler = Crawler()
    crawler.start()
    crawler.join()

    print 'Game over'

def main():
    try:
        crawlPages()
    except KeyboardInterrupt:
        print_('\nCancelling...')

if __name__ == '__main__':
    main()
