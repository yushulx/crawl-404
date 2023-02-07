import requests
from bs4 import BeautifulSoup
import signal
import threading
import argparse

shutdown_event = None
GAME_OVER = '404 analysis completed!!!!!!'

def ctrl_c(signum, frame):
    global shutdown_event
    shutdown_event.set()

class Crawler(threading.Thread):
    def __init__(self, shutdown_event, link, depth):
        threading.Thread.__init__(self)
        self.all_links = {}
        self.max_depth = depth
        self.shutdown_event = shutdown_event
        self.link = link

    def run(self):
        with open("404.txt", "a") as log404:
            with open("200.txt", "a") as log200:
                self.detect_404_pages(self.link, 0, log404, log200)
            
    def detect_404_pages(self, url, depth=0, log404=None, log200=None):
        if self.shutdown_event.is_set():
            return 
        
        if url in self.all_links:
            return

        if depth == self.max_depth:
            return

        self.all_links[url] = True

        try:
            response = requests.get(url, timeout=3)

            if response.status_code == 404:
                print(f"404 Error: {url}")
                log404.write(f"{url}\n")
            else:
                print(f"200 OK: {url}")
                log200.write(f"{url}\n")
                try:
                    if response.headers["Content-Type"].startswith("text/html"):
                        soup = BeautifulSoup(response.content, "html.parser")
                        links = soup.find_all("a")
                        for link in links:
                            href = link.get("href")
                            if href != None and href.startswith("http"):
                                self.detect_404_pages(href, depth + 1, log404, log200)
                    elif response.headers["Content-Type"].startswith("text/xml"):
                        soup = BeautifulSoup(response.content, "xml")
                        urlTags = soup.find_all("url")
                        for tag in urlTags:
                            loc = tag.find("loc")
                            if loc != None:
                                self.detect_404_pages(loc.text, depth + 1, log404, log200)
                    
                except Exception as e:
                    print(f"Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

def crawlPages(link, depth):
    global shutdown_event
    shutdown_event = threading.Event()

    signal.signal(signal.SIGINT, ctrl_c)

    crawler = Crawler(shutdown_event, link, depth)
    crawler.start()
    while crawler.is_alive():
        crawler.join(timeout=0.1)

    print(GAME_OVER)

def main():
    parser = argparse.ArgumentParser(description='404 page detector')
    parser.add_argument('-l', '--link', help='The target web page to be analyzed')
    parser.add_argument('-d', '--depth', default=2, type=int, help='The depth of the link analysis')
    args = parser.parse_args()
    
    try:
        link = args.link
        depth = args.depth
        
        if  link == None:
            parser.print_help()
            return
        
        try:
            crawlPages(link, depth)
        except KeyboardInterrupt:
            print('\nKeyboardInterrupt')
        
    except Exception as e:
        print(f'Error: {e}')
        parser.print_help()

if __name__ == '__main__':
    main()