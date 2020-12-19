import scrapy

class test(scrapy.Spider):
    name = "ip"

    ipLoc = "https://api.ipify.org/"
    agentLoc = "https://www.whatsmyua.info/"
    headersLoc = "https://www.whatismybrowser.com/detect/what-http-headers-is-my-browser-sending"
    
    # proxy = "http://142.93.20.59:3128"
    headers=""
    userAgent = ""

    custom_settings={"LOG_FILE": None}
    
    def start_requests (self):
        metaN = {}
        if (hasattr(self,"proxy")):
            metaN["proxy"] = self.proxy
        yield scrapy.Request(
            url=self.ipLoc,
            meta=metaN,
            callback=self.parseIp
        )
        yield scrapy.Request(
            url=self.agentLoc,
            meta=metaN,
            callback=self.parseAgent
        )
    def parseAgent(self, response):
        self.thisHeaders = response.request.headers
        self.thisAgent = response.css('textarea::text').get()
    def parseIp(self, response) :
        self.thisIp = response.body
    def parseHeaders(self, response):
        self.thisHeaders = {}
        for row in response.css('.table-striped > tr'):
            self.thisHeaders[row.css('th::text').get()] = row.css('td::text').get()
    def closed(self, reason):
        print("--------------------------------------------------------")
        print("--------------------------------------------------------")
        print("--------------------------------------------------------")
        print("--------------------------------------------------------")
        print("--------------------------------------------------------")
        print("--------------------------------------------------------")
        print(self.thisIp)
        print(self.thisAgent)
        print(self.thisHeaders)
        print("--------------------------------------------------------")
        print("--------------------------------------------------------")
        print("--------------------------------------------------------")
        print("--------------------------------------------------------")
        print("--------------------------------------------------------")
        print("--------------------------------------------------------")
