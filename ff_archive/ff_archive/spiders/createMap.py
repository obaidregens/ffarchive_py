import scrapy
import os
import json
import sqlite3

class mapFandoms():
    dbName = "CharacterMaps.db"
    tableName = "ffnMap"
    def __init__(self):
        self.conn = sqlite3.connect(self.dbName)
        self.cursor = self.conn.cursor()
        sql = """
        CREATE TABLE IF NOT EXISTS """ + self.tableName + """(
            fandom         VARCHAR(220)     PRIMARY KEY     NOT NULL,
            category       VARCHAR(220)                     NOT NULL,
            characters     TEXT                             NOT NULL,
            count          BIGINT                           NOT NULL
        );
        """
        self.cursor.execute(sql)
        self.conn.commit()
    def put(self,category,fandom,characters,count):
        self.cursor.execute("""
        REPLACE INTO """ + self.tableName + """
        (fandom, category, characters, count)
        VALUES ( ?, ?, ?, ? )
        """,[fandom,category,json.dumps(characters),int(count)])
    def pursue (self, fandom, count):
        self.cursor.execute("""
        SELECT count FROM """ + self.tableName + """
        WHERE fandom = ?
        """,[fandom])
        r = self.cursor.fetchone()
        if r is None:
            return True
        if int(count) > int(r[0]):
            print(fandom,r[0],count)
            return True
        return False

class createMap(scrapy.Spider):
    name = "createMap"
    start_urls = [
        "https://www.fanfiction.net/cartoon/",
        "https://www.fanfiction.net/book/",
        "https://www.fanfiction.net/anime/",
        "https://www.fanfiction.net/comic/",
        "https://www.fanfiction.net/game/",
        "https://www.fanfiction.net/misc/",
        "https://www.fanfiction.net/play/",
        "https://www.fanfiction.net/movie/",
        "https://www.fanfiction.net/tv/"
    ]

    def __init__ (self):
        self.mapper = mapFandoms()
    def parse(self, response) :
        parts = []
        url_parts = response.url.split('/')
        for part in url_parts:
            if (part != ""):
                parts.append(part)
        cat = parts[-1]
        fandomLinks = response.css("#list_output > table div")
        for fandom in fandomLinks:
            fandom_link = fandom.css("a")[0]
            count = fandom.css('span::text').get()[1:-1]
            if (count[-1] == "K"):
                count = float(count[:-1])*1000
            count = int(count)
            fandomName = fandom_link.attrib["title"]
            if not (self.mapper.pursue(fandomName,count)):
                continue
            yield response.follow(
                fandom_link.attrib["href"],
                callback=self.parseFandom,
                cb_kwargs = {
                    "category"         : cat,
                    "fandom"           : fandomName,
                    "count"            : count
                }
            )
    def parseFandom(self, response, category, fandom, count):
        characters = response.css("select[name='characterid1'] > option:not([value='0'])::text").getall()
        self.mapper.put(category,fandom,characters,count)
    def closed(self,reason):
        self.mapper.conn.commit()