import scrapy
import mysql.connector
import json
import time
import ff_archive.spiders.crawl_settings as crawl_settings
settings = crawl_settings.settings()

# SQL get unverified
sql_connection = mysql.connector.connect(
  host = "localhost",
  user = settings.db["user"],
  password = settings.db["password"],
  database = settings.db["name"]
)
db = sql_connection.cursor()

letter = """"

"""
letter_subject = ""



class ffnAllowMessages(scrapy.Spider):
    name = "ffn_allow_alert"
    start_urls = ["https://www.fanfiction.net/book/Harry-Potter/?&srt=1&lan=1&r=10&len=10&t=4"]
    cookies = settings.creds["ffn"]["cookies"]
    max_pages = 10
    def parse(self, response):
        for book in response.css('#content_wrapper_inner > div.z-list'):
            Author_ID = int(book.css("a[href^='/u']::attr(href)").get().split('/')[2])
            yield scrapy.Request(
                response.urljoin( "/pm2/post.php?uid=" + str(Author_ID) ),
                callback = self.sendMessage,
                cookies = self.cookies,
                cb_kwargs = {
                    "uid"          : Author_ID,
                }
            )
        pg = int(response.xpath('//*[@id="content_wrapper_inner"]/center[1]/b[1]/text()').get())
        next_pg_attr = response.xpath('//*[@id="content_wrapper_inner"]/center[1]/a[contains(text(),\'Next »\')]').attrib
        if ("href" in next_pg_attr) & (pg < self.max_pages):
            next_pg = next_pg_attr['href']
            yield scrapy.Request(
                response.urljoin(next_pg),
                callback = self.parse
        )
    def sendMessage (self, response, uid):
        username = response.css('#gui_table2i > tbody > tr:nth-child(2) > td:nth-child(2) > a[href="/u/6411012/"]::text').get()
        custom_letter = letter.replace('###USERNAME###',username)
        return scrapy.FormRequest.from_response(
            response,
            formname = 'fpost',
            formdata = {
                'subject'  : letter_subject,
                'message'   : letter
            },
        )