import scrapy
import mysql.connector
import json
import time
import math
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

def sqlPlaceholder(l):
    return ",".join(['%s'] * l )
def dbInsert(table,insertData):
    sql = "INSERT INTO " + table + " (" + ",".join(insertData.keys()) + ")" + " VALUES (" + sqlPlaceholder(len(insertData)) + ")"
    db.execute(sql,list( insertData.values()))
    sql_connection.commit()
    return db.lastrowid

letter = """
The first Letter
Second Line

Gap Line

mon.mon
"""
letter_subject = "The first Subject"

class ffnAllowMessages(scrapy.Spider):
    name = "ffn_outreach"
    start_urls = ["https://www.fanfiction.net/" + url + "?&srt=1&lan=1&r=10&t=4" for url in [
        "book/Harry-Potter/",
        # "anime/Naruto/",
        # "book/Twilight/",
        # "anime/Hetalia-Axis-Powers/",
        # "anime/Inuyasha/",
        # "tv/Supernatural/"
    ]]
    cookies = settings.creds["ffn-authorPM"]["cookies"]
    max_pages = 10
    def parse(self, response):
        pass
        # yield response.follow(
        #     "/u/" + str(11649582),
        #     callback = self.parseProfile,
        #     cb_kwargs = {
        #         "uid"           : 11649582
        #     }
        # )
        # for book in response.css('#content_wrapper_inner > div.z-list'):
            # Author_ID = int(book.css("a[href^='/u']::attr(href)").get().split('/')[2])
            # yield response.follow(
            #     "/u/" + str(Author_ID),
            #     callback = self.parseProfile,
            #     cb_kwargs = {
            #         "uid"           : Author_ID
            #     }
            # )
        # pg = int(response.xpath('//*[@id="content_wrapper_inner"]/center[1]/b[1]/text()').get())
        # next_pg_attr = response.xpath('//*[@id="content_wrapper_inner"]/center[1]/a[contains(text(),\'Next »\')]').attrib
        # if ("href" in next_pg_attr) & (pg < self.max_pages):
        #     next_pg = next_pg_attr['href']
        #     yield scrapy.Request(
        #         response.urljoin(next_pg),
        #         callback = self.parse
        #     )
    def parseProfile(self, response, uid):
        ratingNums = {
            "K": 1,
            "K+": 2,
            "T": 3,     
            "M": 5
        }
        dataSend = {
            "uid": uid,
            "data": {
                "username": response.css("#content_wrapper_inner > span:first-of-type::text").get().lstrip(),
                "ffn_joined": int(response.css("#content_wrapper_inner > table > tr > td > table > tr:nth-child(2) > td > span:nth-child(1)").attrib["data-xutime"]),
                "profile_updated": 0,
                "total_stories": int(response.css("#l_st > span::text").get())
            },
            "total": {
                "chapters": 0,
                "words":    0,
                "favs":     0,
                "follows":  0,
                "reviews":  0,
                "rating":   0
            },
            "newest": {},
            "oldest": {},
            "top_favs": {}
        }
        if (response.css("#content_wrapper_inner > table > tr > td > table > tr:nth-child(2) > td > span:nth-of-type(2)")):
            dataSend["data"]["profile_updated"] =  int(response.css("#content_wrapper_inner > table > tr > td > table > tr:nth-child(2) > td > span:nth-of-type(2)").attrib["data-xutime"])
            
        fandoms_count = {}
        for story in response.css("div.z-list.mystories"):
            tags = ''.join(story.css('.z-padtop2.xgray::text,.z-padtop2.xgray *::text').getall()).split(' - ')
            tags_dict = {}
            tags_dict["updated"] = int(story.attrib["data-dateupdate"])
            tags_dict["published"] = int(story.attrib["data-datesubmit"])
            tags_dict["fandom"] = tags.pop(0)
            if (tags_dict["fandom"] == "Crossover"):
                tags_dict["fandom"] = tags.pop(0)
            tags_dict["language"] = tags.pop(1)
            tags_dict["genre"] = tags.pop(1)
            for tag in tags:
                sp = tag.split(": ")
                if (len(sp) < 2):
                    continue
                if sp[0] == "Rated":
                    dataSend["total"]['rating'] += ratingNums[sp[1]]
                    tags_dict['rating'] = sp[1]
                if sp[0] in ["Chapters","Words","Reviews","Favs","Follows"]:
                    field = sp[0].lower()
                    value = int(sp[1].replace(',',''))
                    dataSend["total"][field] += value
                    tags_dict[field] = value
            # Tags Collected
            if (tags_dict["updated"] > dataSend["newest"].get("updated",0)):
                dataSend["newest"] = tags_dict
            if (tags_dict.get("favs",0) > dataSend["top_favs"].get("favs",0)):
                dataSend["top_favs"] = tags_dict
            if (tags_dict["published"] < dataSend["oldest"].get("published",math.inf)):
                dataSend["oldest"] = tags_dict
            fandoms_count[tags_dict["fandom"]] = fandoms_count.get(tags_dict["fandom"],0) + 1 

        for fandom,count in fandoms_count.items():
            if "most_fandom" not in dataSend["data"]:
                dataSend["data"]["most_fandom"] = fandom
                continue
            if count > fandoms_count[dataSend["data"]["most_fandom"]]:
                dataSend["data"]["most_fandom"] = fandom
        for attr in ["newest","oldest","top_favs"]:
            if dataSend[attr] == {}:
                dataSend[attr] = tags_dict

        yield response.follow(
            "/pm2/post.php?uid=" + str(uid),
            callback = self.sendMessage,
            cookies = self.cookies,
            cb_kwargs = dataSend
        )
    def sendMessage (self, response, uid, data, total, newest, oldest, top_favs):
        insertItems = {
            "ffn_user_id": uid,
            "message_sent": int(time.time()),
            "ffn_username": data["username"],
            "ffn_joined": data["ffn_joined"],
            "profile_updated": data["profile_updated"],
            "total_stories": data["total_stories"],
            "most_fandom": data["most_fandom"],
            "total_chapters": total["chapters"],
            "total_words": total["words"],
            "total_favs": total["favs"],
            "total_follows": total["follows"],
            "total_reviews": total["reviews"],
            "total_rating": total["rating"],
            "top_favs_fandom": top_favs["fandom"],
            "top_favs_words": top_favs["words"],
            "top_favs_reviews": top_favs.get('reviews',0),
            "top_favs_chapters": top_favs["chapters"],
            "top_favs_favs": top_favs.get("favs",0),
            "top_favs_follows": top_favs.get("follows",0),
            "top_favs_rating": top_favs["rating"],
            "top_favs_language": top_favs["language"],
            "top_favs_genre": top_favs["genre"],
            "top_favs_updated": top_favs["updated"],
            "top_favs_published": top_favs["published"],
            "oldest_published": oldest["published"],
            "oldest_updated": oldest["updated"],
            "newest_published": newest["published"],
            "newest_updated": newest["published"]
        }
        dbInsert("ffn_outreach",insertItems)
        print(response.css('#fpost input,#fpost textarea'))
        return scrapy.FormRequest.from_response(
            response,
            formname = 'fpost',
            formdata = {
                'subject'  : letter_subject,
                'message'  : letter.replace('###USERNAME###',data["username"])
            },
        )