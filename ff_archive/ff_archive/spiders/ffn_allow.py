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
excludeAuthors = [2277200,11062014,13365819,1936982,12441929,10036896,10123044,9023672,12805030,11887033,7834753,5320029,9784244,12846082,2206870,11176975,12199265,5248331,4166096,5894692,2690404,8342219,11165093,10548669,3620123,13638853,747613,2726003,4790465,13413785,5339762,8899921,2030994,7019604,9443441,6949450,2322071,1960803,13109630,13952026,10948791,4705276,1223404,755589,12630402,11608854,3844729,4718995,12022304,9664991,10079348,8130737,4991010,3844380,10162392,11021791,13704942,4817751,1860009,6596946,12339549,1220065,9595543,13161514,4247320,11121317,7351150,8591231,981797,2184316,1605171,4363318,5187430,8965444,5666630,2446972,12326154,5728664,6415261,6835171,9277092,10731959,638859,6716408,9400623,1909983,12727320,2836195,5460436,7494196,4469194,11271275,3165174,939828,12862990,13660621,2149875,5499201,13556346,812247,6783142,13476475,13265614,147648,2639910,4684913,866407,10558417,12358044,1576308,8957205,62350,12253703,5235093,1915327,3831521,1666976,8784056,1703367,1265079,227409,6778541,12345904,1806157,8543533,3712368,6396272,3714792,9916427,972483,10367009,6578485,13044979,2049212,3026205,431968,4098044,2441303,1463237,956214,5974530,914721,3515029,11509202,3005930,912889,715571,3189590,14018001,13403460,5696277,2794336,4677330,2303471,4724063,12345904,1806157,4098044,3005930,8024050,10654210,3926182,100353,107437,2879833,4280645,2407791,4743479,1251524,7336118,1586290,6807884,7217713,6629459,1465258,10036896,7469591,13612815,49515,6908767,5235608,2229598,10920921,6934403,2394023,31969,6500750,5705073,6626096,5415309,11649002,3460243,2468907,5023684,1386923,13385728,1084919,11300541,6125814,2321552,13827438,4036441,6365873,11142828,2240236,2996114,8182083,5346457,10005030,5698271,2020545,2455049,1864181,1404943,12058842,6737885,7037477,6473098,1304480,4788805,3148526,7997642,1318815,4453643,9436302,8427977,4219330,494464,4314892,2102558,386600,386600,11649582,11649582,13819943,13819943,14168398]
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
Hi! :)

We've created a site at Fanfiction Online {fanfiction (dot) online} for reading and writing fanfiction, since we feel FFN (and other sites) are really outdated and lack a lot of stuff.

We'd love if you could post your stories there. You can reach new readers, and since the site has far better reading, your current readers will read your fanfics more comfortably as well.

You might find it difficult to post on another site, so we've done all the heavy lifting for you :) All you have to do is link your FFN account and select the stories you want to import. It's as simple as that. The stories will be updated automatically whenever you update the fic on FFN.

Thanks! Let me know if you have any questions.
"""
letter_subject = "Hi! :)"

out_file = "C:/Users/obaid/Py Projects/ffarchive_py/ff_archive/ff_archive/spiders/UserData.jsonl"

class ffnAllowMessages(scrapy.Spider):

    name = "ffn_outreach"
    custom_settings = {
        "LOG_FILE": "C:/Users/obaid/Py Projects/ffarchive_py/ff_archive/ff_archive/spiders/output-get.txt"
    }
    start_urls = ["https://www.fanfiction.net/" + url + "?&srt=5&lan=1&r=10&t=3" for url in [
        "book/Harry-Potter/",
        # "anime/Naruto/",
        # "book/Twilight/",
        # "anime/Hetalia-Axis-Powers/",
        # "anime/Inuyasha/",
        # "tv/Supernatural/"
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
                tags = ''.join(story.css('.z-padtop2.xgray::text,.z-padtop2.xgray *::text').getall()).split(' - ')
                tags_dict = {}
                tags_dict["updated"] = int(story.attrib["data-dateupdate"])
                tags_dict["published"] = int(story.attrib["data-datesubmit"])
                tags_dict["fandom"] = tags.pop(0)
                if (tags_dict["fandom"] == "Crossover"):
                    tags_dict["fandom"] = tags.pop(0)
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
        "LOG_FILE": "C:/Users/obaid/Py Projects/ffarchive_py/ff_archive/ff_archive/spiders/output-sender.txt"
    }
    start_urls = []
    last_sent = 0
    queue = []
    cookies = settings.creds["ffn-authorPM"]["cookies"]
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
            self.queue.append(self.reqs(json.loads(line)))
    def reqs(self,insertData):
        if ("insertData" in insertData):
            insertData = insertData["insertData"]
        return scrapy.Request(
            "https://www.fanfiction.net/pm2/post.php?uid=" + str(insertData["ffn_user_id"]),
            cookies = self.cookies,
            callback = self.pms,
            cb_kwargs={
                "insertData": insertData
            }
        )
    def write(self):
        dumper = ""
        for req in self.queue:
            dumper += json.dumps(req.cb_kwargs["insertData"]) + "\n"
        with open(out_file, "w+") as dump_file:
            dump_file.write(dumper)
    def pms(self,response,insertData):
        if (len(response.css("form[name='fpost']")) > 0) and (insertData["ffn_user_id"] not in excludeAuthors):
            while (time.time() - self.last_sent) <= 30:
                time.sleep(10)
                print("Sleep")
            self.last_sent = time.time()
            return scrapy.FormRequest.from_response(
                response,
                formid ="fpost",
                formname = 'fpost',
                formdata = {
                    'subject'  : letter_subject,
                    'message'  : letter
                },
                cb_kwargs = {
                    "insertData": insertData
                },
                callback = self.submit
            )
    def submit (self, response, insertData):
        res = response.css('#xpreview.zhide + div + div::attr(class)').get()
        if res == "panel_success":
            dbInsert("ffn_outreach",insertData)
            print("Sent: " + insertData["ffn_username"])
            self.queue.pop(0)
            self.write()
        elif res == "panel_warning":
            print("Unsent: " + insertData["ffn_username"])
            pass
        else:
            print("Unknown Error Class: " + res)
        yield self.queue[0]