import scrapy

class stressTest(scrapy.Spider):
    name = "stressTest"
    custom_settings = {
        "CONCURRENT_REQUESTS": 500,
        "LOG_FILE": None
    }
    hits = 0
    def start_requests(self):
        for i in range(2000):
            yield scrapy.Request(
                "https://fanfiction.online/read",
                callback = self.parse,
                dont_filter=True
            )
    def parse(self, response) :
        self.hits += 1
        print ("Hit " + str(self.hits)) 
        pass