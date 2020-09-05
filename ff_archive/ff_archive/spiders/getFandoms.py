import os 
import scrapy

def removeEmptyFilter(v):
    if (v == ''):
        return False
    return True
class getFandoms(scrapy.Spider):
    name = "getFandoms"
    start_urls = [
        "https://www.fanfiction.net/book/",
        "https://www.fanfiction.net/anime/",
        "https://www.fanfiction.net/comic/",
        "https://www.fanfiction.net/game/",
        "https://www.fanfiction.net/misc/",
        "https://www.fanfiction.net/play/",
        "https://www.fanfiction.net/movie/",
        "https://www.fanfiction.net/tv/"
    ]

    def parse(self, response) :
        parts = []
        url_parts = response.url.split('/')
        for part in url_parts:
            if (part != ""):
                parts.append(part)
        cat = parts[-1]
        fandomNames = response.css("#list_output > table a::attr(title)").getall()
        with open("category-ffn/" + cat + ".tags", "w+",encoding="utf-8") as dump_file:
            dump_file.write( "\n".join(fandomNames) )