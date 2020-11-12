import scrapy
from scrapy.crawler import CrawlerProcess
import mysql.connector
import json
import time
import math
import ff_archive.spiders.crawl_settings as crawl_settings
settings = crawl_settings.settings()

# SQL
sql_connection = mysql.connector.connect(
    host = "localhost",
    user = settings.db["user"],
    password = settings.db["password"],
    database = settings.db["name"]
)
db = sql_connection.cursor()
 
# Sent Manually
excludeAuthors = []
# Sql Get Existing = 
db.execute("SELECT ffn_user_id from ffn_outreach")
existingAuthors = [int(tup[0]) for tup in db.fetchall()]

def sqlPlaceholder(l):
    return ",".join(['%s'] * l )
def dbInsert(table,insertData):
    sql = "INSERT INTO " + table + " (" + ",".join(insertData.keys()) + ")" + " VALUES (" + sqlPlaceholder(len(insertData)) + ")"
    db.execute(sql,list( insertData.values()))
    sql_connection.commit()
    return db.lastrowid

letter = """
Hi ###USERNAME###! :)

We've created a site at Fanfiction Online {fanfiction (dot) online} for reading and writing fanfiction, since we feel FFN (and other sites) are really outdated and lack a lot of stuff.

Would love if you could post your stories there. You can reach new readers, and since the site has better reading, your current readers will read your fanfics more comfortably as well.

You might find it difficult to post on another site, so the site will do all the heavy lifting for you :) All you have to do is link your FFN account and select the stories you want to import. It's as simple as that. The stories will be updated automatically whenever you update the fic on FFN. 

Thanks! Let me know if you have any questions.
"""
letter_subject = "Hi ###USERNAME###! :)"

out_file = "C:/Users/obaid/Py Projects/ffarchive_py/ff_archive/ff_archive/spiders/UserData.jsonl"

class ffnAllowMessages(scrapy.Spider):

    name = "ffn_outreach"
    custom_settings = {
        "LOG_FILE": "C:/Users/obaid/Py Projects/ffarchive_py/ff_archive/ff_archive/spiders/output-get.txt"
    }
    start_urls = ["https://www.fanfiction.net/" + url + "?&srt=5&r=10&t=4" for url in [
        "book/Harry-Potter/",
        "game/Pokémon/",
        "anime/Naruto/",
        "book/Twilight/",
        "anime/Hetalia-Axis-Powers/",
        "anime/Inuyasha/",
        "tv/Supernatural/",
        "tv/Glee/"
    ]]
    last_sent = 0
    cookies = settings.creds["ffn-authorPM"]["cookies"]
    max_pages = 20
    def parse(self, response):
        for book in response.css('#content_wrapper_inner > div.z-list'):
            Author_ID = int(book.css("a[href^='/u']::attr(href)").get().split('/')[2])
            if ( (Author_ID in excludeAuthors) or (Author_ID in existingAuthors) ):
                continue
            existingAuthors.append(Author_ID)
            yield response.follow(
                "/u/" + str(Author_ID),
                callback = self.parseProfile,
                cb_kwargs = {
                    "uid"           : Author_ID
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
    def parseProfile(self, response, uid):
        if len(response.css("a[title='Send Private Message']")) > 0:
            ratingNums = {
                "K": 1,
                "K+": 2,
                "T": 3,     
                "M": 5
            }
            if "data-xutime" not in response.css("#content_wrapper_inner > table > tr > td > table > tr:last-child > td > span:nth-child(1)").attrib:
                print("------------------------------XXXXXXXXXX------------------------------")
                print(response.css("#content_wrapper_inner > table > tr > td > table > tr:last-child > td > span:nth-child(1)"))
                print(response.css("#content_wrapper_inner > table > tr > td > table > tr:last-child > td > span:nth-child(1)")).attrib
                print("------------------------------XXXXXXXXXX------------------------------")
            dataSend = {
                "uid": uid,
                "data": {
                    "username": response.css("#content_wrapper_inner > span:first-of-type::text").get().lstrip(),
                    "ffn_joined": int(response.css("#content_wrapper_inner > table > tr > td > table > tr:last-child > td > span:nth-child(1)").attrib["data-xutime"]),
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
                dataSend["data"]["profile_updated"] =  int(response.css("#content_wrapper_inner > table > tr > td > table > tr:last-child > td > span:nth-of-type(2)").attrib["data-xutime"])
                
            fandoms_count = {}
            for story in response.css("div.z-list.mystories"):
                raw_tags_string = ''.join(story.css('.z-padtop2.xgray::text,.z-padtop2.xgray *::text').getall())
                # Remove Crossover
                if raw_tags_string[:12] == "Crossover - ":
                    raw_tags_string = raw_tags_string[12:]
                # Remove Fandom
                raw_tags_string = raw_tags_string[len(story.attrib["data-category"]) + len(" - "):]

                tags = raw_tags_string.split(' - ')
                tags_dict = {}
                tags_dict["fandom"] = story.attrib["data-category"]
                tags_dict["updated"] = int(story.attrib["data-dateupdate"])
                tags_dict["published"] = int(story.attrib["data-datesubmit"])
                tags_dict["language"] = tags.pop(1)
                if 'Chapters: ' not in tags[1]:
                    tags_dict['genre'] = tags.pop(1)
                else:
                    tags_dict["genre"] = "General"
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
        if "chapters" not in top_favs:
            print("------------------------------XXXXXXXXXX------------------------------")
            print(top_favs)
            print("------------------------------XXXXXXXXXX------------------------------")
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
        with open(out_file, "a+") as dump_file:
            dump_file.write( json.dumps(insertItems) + "\n" )

class ffnOutreachSender(scrapy.Spider):
    name = "outreach_sender"
    custom_settings = {
        "LOG_FILE": "C:/Users/obaid/Py Projects/ffarchive_py/ff_archive/ff_archive/spiders/output-sender.txt",
        "dont_filter": True
    }
    last_sent = {}
    queue = []
    rotate = [
        "ffn-authorPM",
        "ffn-authorPM2",
        "ffn-authorPM3",
        "ffn-authorPM4",
        "ffn-authorPM5"
    ]
    def start_requests(self):
        self.read()
        yield self.queue[0]
    def read(self):
        with open(out_file, "r") as dump_file:
            L = dump_file.readlines()
        if len(L) < 1:
            time.sleep(5)
            return self.read()
        for line in L:
            insertData = json.loads(line)
            A_ID = int(insertData["ffn_user_id"]) 
            if ( (A_ID in excludeAuthors) or (A_ID in existingAuthors) ):
                continue
            self.queue.append(self.reqs(insertData))
    def reqs(self,insertData):
        index = int(int((len(self.queue)/5*10)%10)/2)
        user = self.rotate[index]
        cookies = settings.creds[user]["cookies"]
        if ("insertData" in insertData):
            insertData = insertData["insertData"]
        return scrapy.Request(
            "https://www.fanfiction.net/pm2/post.php?uid=" + str(insertData["ffn_user_id"]),
            cookies = cookies,
            callback = self.pms,
            cb_kwargs={
                "insertData": insertData,
                "user": user
            }
        )
    def write(self):
        dumper = ""
        for req in self.queue:
            dumper += json.dumps(req.cb_kwargs["insertData"]) + "\n"
        with open(out_file, "w+") as dump_file:
            dump_file.write(dumper)
    def pms(self,response,insertData,user):
        if (len(response.css("form[name='fpost']")) > 0) and (insertData["ffn_user_id"] not in excludeAuthors) and (insertData["ffn_user_id"] not in existingAuthors):
            while (time.time() - self.last_sent.get(user,0)) <= 35:
                time.sleep(5)
                print("Sleep")
            self.last_sent[user] = time.time()
            return scrapy.FormRequest.from_response(
                response,
                formid ="fpost",
                formname = 'fpost',
                formdata = {
                    'subject'  : letter_subject.replace("###USERNAME###",insertData["ffn_username"]),
                    'message'  : letter.replace("###USERNAME###",insertData["ffn_username"])
                },
                cb_kwargs = {
                    "insertData": insertData,
                    "user": user
                },
                callback = self.submit
            )
    def submit (self, response, insertData, user):
        res = response.css('#xpreview.zhide + div + div::attr(class)').get()
        if res == "panel_success":
            dbInsert("ffn_outreach",insertData)
            print("Sent: " + insertData["ffn_username"])
            self.queue.pop(0)
            self.write()
        elif res == "panel_warning":
            print(response.css("#xpreview.zhide + div + div").get())
            print("From: " + user)
            print("Unsent: " + insertData["ffn_username"])
            pass
        else:
            print("Unknown Error Class: " + res)
        yield self.queue[0]