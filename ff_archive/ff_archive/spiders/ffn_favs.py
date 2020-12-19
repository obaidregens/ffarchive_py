import scrapy
import mysql.connector
import ff_archive.spiders.crawl_settings as crawl_settings
settings = crawl_settings.settings()

# SQL
sql_connection = mysql.connector.connect(
    host = "localhost",
    user = settings.db["user"],
    password = settings.db["password"],
    database = settings.db["name"],
    port = settings.db.get("port",3306)
)
db = sql_connection.cursor()

db.execute("SELECT import_user,user_id,import_story FROM import_stories WHERE import_favs = 0")
authorIds = {}
for row in db.fetchall():
    if not str(row[0]) in authorIds:
        authorIds[str(row[0])] = {
            "include"   : [],
            "user_id"   : row[1]
        }
    authorIds[str(row[0])]["include"].append(int(row[2]))

def parseStory(storyBlock):
    ID = int(storyBlock.css("a.stitle::attr(href)").get().split('/')[2])

    raw_tags_string = ''.join(storyBlock.css('.z-padtop2.xgray::text,.z-padtop2.xgray *::text').getall())

    # Remove Crossover
    if raw_tags_string[:12] == "Crossover - ":
        raw_tags_string = raw_tags_string[12:]
    # Remove Fandom
    raw_tags_string = raw_tags_string[len(storyBlock.attrib["data-category"]) + len(" - "):]

    raw_tags = raw_tags_string.split(' - ')
    tags = {}

    tags['Language'] = raw_tags.pop(1)
    if 'Chapters: ' not in raw_tags[1]:
        tags['Genre'] = raw_tags.pop(1).split('/')
    if 'Complete' == raw_tags[-1]:
        tags['Status'] = raw_tags.pop(-1)
    else:
        tags['Status'] = 'In Progress'
    for tag_is in raw_tags:
        if 'Updated: ' in tag_is or 'Published: ' in tag_is:
            pass
        elif ': ' in tag_is:
            tag_is_arr = tag_is.split(': ')
            if tag_is_arr[0] in ['Chapters','Words','Reviews','Favs','Follows']:
                tag_is_arr[1] = int(tag_is_arr[1].replace(',',''))
            tags[tag_is_arr[0]] = tag_is_arr[1]
        else:
            raw_characters = tag_is.split(']')
            if '' in raw_characters: raw_characters.remove('')
            tags['Relationships'] = []
            tags['Characters'] = []
            tags['All Characters'] = []
            for characters_piece in raw_characters:
                char_set = characters_piece.lstrip(' [').split(', ')
                if '[' in characters_piece:
                    tags['Relationships'].append(char_set)
                else:
                    tags['Characters'] = char_set
                tags['All Characters'] += char_set
    story_data = {
        '_id'           : ID,
        'Title'         : storyBlock.css("a.stitle::text").get(),
        'Description'   : storyBlock.css("div.z-indent.z-padtop::text").get(),
        'Tags'          : tags,
        'Chapters'      : []
    }
    first_time = storyBlock.css('.z-padtop2.xgray > span:nth-of-type(1)::attr(data-xutime)').get()
    second_time = storyBlock.css('.z-padtop2.xgray > span:nth-of-type(2)::attr(data-xutime)').get()
    if second_time is not None:
        story_data['Updated'] = int(first_time)
        story_data['Published'] = int(second_time)
    else:
        story_data['Published'] = int(first_time)
    return story_data


class uploadStats(scrapy.Spider):
    name = "upload_stats"
    custom_settings= {
        "DOWNLOAD_DELAY": 5
    }
    def start_requests(self):
        for uid,author in authorIds.items():
            yield scrapy.Request(
                "https://www.fanfiction.net/u/" + str(uid),
                callback = self.parseAuthor,
                cb_kwargs={
                    "author": author
                }
            )
    def parseAuthor(self, response, author):
        for storyBlock in response.css("div.z-list.mystories"):
            story = parseStory(storyBlock)
            if story["_id"] not in author["include"]:
                continue
            sql = """
            UPDATE import_stories
            SET import_favs=%s,import_follows=%s
            WHERE import_story=%s
            """
            db.execute(sql, [story["Tags"].get("Favs",0),story["Tags"].get('Follows',0),story["_id"]] )
    def closed(self, reason):
        sql_connection.commit()