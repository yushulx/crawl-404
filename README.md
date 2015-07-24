# Crawling Broken Links with 404 Error in Python
The sample demonstrates how to use Python to crawl Website pages via sitemap.xml and check broken links for every page.

Installation
------------
* ``pip install beautifulsoup4``

Basic Steps
-----------
1. Read sitemap.xml of the target Website.
2. Search for attribute 'href' to get all valid links in every page.
3. Check link response code.
4. Dump 404 error URLs to a text file.


How to Run
----------
1. Specify sitemap: ``request = build_request("http://kb.dynamsoft.com/sitemap.xml")``.
2. ``python broken_links.py``.
3. Use ``ctrl+c`` to stop the program.

Blog
----
Coming soon...
