import scrapy
import os
import json
import time

class ffnForums(scrapy.Spider):
    name = "ffnForums"
    newerThan = 1600560000
    dumped = 0
    part = 1
    forums = 0
    pages = 0
    threads = 0
    forum_list = {}
    start_urls = [
        # "https://www.fanfiction.net/forums/general/0/",
        "https://www.fanfiction.net/forums/misc/",
        "https://www.fanfiction.net/forums/anime/",
        "https://www.fanfiction.net/forums/book/",
        "https://www.fanfiction.net/forums/movie/",
        "https://www.fanfiction.net/forums/cartoon/",
        "https://www.fanfiction.net/forums/play/",
        "https://www.fanfiction.net/forums/comic/",
        "https://www.fanfiction.net/forums/tv/",
        "https://www.fanfiction.net/forums/game/",
    ]
    def parse(self, response) :
        all_got = response.css("#list_output > table a,#list_output > table a + span.gray::text")
        for i, el in enumerate(all_got):
            if (i % 2) == 0:
                # Is anchor
                continue
            # Is span
            if int(el.get().strip('()')) <= 5:
                # Less Count
                continue
            yield response.follow(
                all_got[i-1].attrib["href"],
                callback = self.parsePage
            )
    def parsePage(self, response) :
        self.pages += 1
        yield from response.follow_all(
            response.css("#content_wrapper_inner .z-list > a.novtitle"),
            callback = self.parseForum
        )
        next_pg_attr = response.xpath('//*[@id="content_wrapper_inner"]/form[1]/div[1]/span/a[contains(text(),\'Next »\')]').attrib
        if ("href" in next_pg_attr):
            yield response.follow(
                next_pg_attr["href"],
                callback = self.parsePage
            )
    def parseForum(self, response):
        forumLink = '/'.join(response.url.split('/')[:6])
        if forumLink not in self.forum_list:
            self.forum_list[forumLink] = {
                "link": forumLink,
                "name": response.css("#content_wrapper_inner > div:nth-child(1) > strong::text").get(),
                "active_threads": 0
            }
        shouldBreak = False
        for timestamp in response.css("#gui_table1i > tbody > tr:not(:first-child) > td:nth-child(2) > div.xgray"):
            if int(timestamp.attrib["data-xutime"]) < self.newerThan:
                shouldBreak = True
                break
            self.threads += 1
            self.forum_list[forumLink]["active_threads"] += 1
        next_pg_attr = response.xpath('//*[@id="content_wrapper_inner"]/div[2]/span/center/a[contains(text(),\'Next »\')]').attrib
        if ( (shouldBreak == False) and ("href" in next_pg_attr) ):
            yield response.follow(
                next_pg_attr["href"],
                callback = self.parseForum
            )
        else:
            if self.forum_list[forumLink]["active_threads"] > 0:
                if self.dumped > (self.part*100):
                    self.part += 1
                print("Pages Crawled: " + str(self.pages))
                print("Forums Dumped: " + str(self.dumped))
                print("Forums Crawled: " + str(self.forums))
                print("Active Threads: " + str(self.threads))
                with open("forumsRecent-" + str(self.part) + ".jsonl", "a+") as dump_file:
                    dump_file.write( json.dumps(self.forum_list[forumLink]) + "\n" )
                self.dumped += 1
            self.forums += 1
            del self.forum_list[forumLink]

class ffnF (scrapy.Spider):
    name = 'f'
    forum_list = {}
    newerThan = int(time.time()) - (60*60*0.1)
    start_urls = ['https://www.fanfiction.net/']
    # exclude = 'forumsRecentLast.jsonl'
    def parse(self, response):
        ex = []
        if hasattr(self,'exclude'):
            with open(self.exclude, "r") as dump_file:
                old = dump_file.readlines()
            for single in old:
                ex.append(json.loads(single)["link"])
        with open("forums-1.jsonl", "r") as dump_file:
            L = dump_file.readlines()
        links = []
        for line in L:
            lk = json.loads(line)["link"]
            if lk not in ex:
                links.append(lk)
        yield from response.follow_all(
            links,
            callback = self.parseForum
        )
    def parseForum(self, response):
        forumLink = '/'.join(response.url.split('/')[:6])
        if forumLink not in self.forum_list:
            self.forum_list[forumLink] = {
                "link": forumLink,
                "name": response.css("#content_wrapper_inner > div:nth-child(1) > strong::text").get(),
                "active_threads": 0
            }
        for timestamp in response.css("#gui_table1i > tbody > tr:not(:first-child) > td:nth-child(2) > div.xgray"):
            if int(timestamp.attrib["data-xutime"]) >= self.newerThan:
                self.forum_list[forumLink]["active_threads"] += 1
        if self.forum_list[forumLink]["active_threads"] > 0:
            with open("forumsRecentLast1.jsonl", "a+") as dump_file:
                dump_file.write( json.dumps(self.forum_list[forumLink]) + "\n" )
