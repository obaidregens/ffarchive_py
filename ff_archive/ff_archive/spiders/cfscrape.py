import cloudscraper
# from time import sleep
# from urllib.parse import urlparse
# from pprint import pprint

# urls = [
#     "https://www.fanfiction.net",
#     "https://www.fanfiction.net/book",
#     "https://www.fanfiction.net/misc"
# ]
# scraper = cloudscraper.create_scraper()

# i = 0
# for url in urls:
#     i += 1
#     html = scraper.get(url).text
#     pprint(vars(scraper))

#     with open("fanfiction-"  + str(i) + ".html", "w+") as dump_file:
#         dump_file.write(html)
    
#     sleep(10)