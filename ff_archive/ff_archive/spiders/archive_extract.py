import scrapy

class archiveExtract(scrapy.Spider):
    name = "archiveExtract"
    start_urls = [
        # "https://ia800401.us.archive.org/view_archive.php?archive=/21/items/fanfictiondotnet_repack/Fanfiction_H_rest.zip&file=Fanfiction%2FHannah%20Montana%2FCompleted%2FHannah%20Montana%20-%200T0Y0L0E0R0%20-%20Mimicking%20Love.txt"
        "file:///C:/Users/obaid/Py Projects/ffarchive_py/ff_archive/ff_archive/archive.html"
    ]
    count = 0
    def parse(self, response):
        for link in response.css("a"):
            yield scrapy.Request(
                link.attrib["href"],
                callback = self.parseSingle,
            )
    def parseSingle(self, response):
        lines = response.text.split("\n")
        if lines[12][:11] == "Published: ":
            year = int(lines[12][11:15])
        elif lines[13][:11] == "Published: ":
            year = int(lines[13][11:15])
        elif lines[14][:11] == "Published: ":
            year = int(lines[14][11:15])
        
        if year >= 2006 and year <= 2007:
            self.count += 1
            print(self.count)
        