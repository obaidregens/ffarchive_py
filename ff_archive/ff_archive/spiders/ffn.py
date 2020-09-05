import os
import glob
import time
import scrapy
import mysql.connector
import json
import ff_archive.spiders.crawl_settings as crawl_settings
settings = crawl_settings.settings()
sql_connection = mysql.connector.connect(
  host = "localhost",
  user = settings.db["user"],
  password = settings.db["password"],
  database = settings.db["name"]
)
db = sql_connection.cursor()

class ffnCrawler(scrapy.Spider):
    name = "ffn"
    max_pages = settings.crawl["max_pages"] or 1
    start_urls = settings.urls or []

    def __init__(self, name=None, **kwargs):
        _dir = settings.crawl['dump_dir'] or ""
        if (_dir == ''):
            _dir = os.getcwd()
        self.scraped = []
        file_list = glob.glob(os.path.join(_dir, '*.jsonl'))
        for filename in file_list:
            ufile = open(filename, 'r')
            lines = ufile.readlines() 
            for fileLine in lines:
                self.scraped.append(json.loads(fileLine)['_id'])
        self.current = []
    def book_ids_from_links(self,book_link):
        return int(book_link.split('/')[2])
    def parse(self, response):
        # Fandom Determination
        type_img = response.xpath('//*[@id="content_wrapper_inner"]/img[1]').attrib['src']
        if type_img == '//ff74.b-cdn.net/static/ficons/script.png':
            fandom = [response.xpath('//*[@id="content_wrapper_inner"]/span[2]/following-sibling::text()').get().rstrip()]
        elif type_img == '//ff74.b-cdn.net/static/fcons/arrow-switch.png':
            fandom = [
                response.xpath('//*[@id="content_wrapper_inner"]/a[1]/text()').get(),
                response.xpath('//*[@id="content_wrapper_inner"]/a[2]/text()').get()
            ]
        else:
            print('Unknown type')
            exit(0)
        # Get Existing
        all_book_ids = list(map( self.book_ids_from_links, response.css('#content_wrapper_inner > div.z-list > a.stitle::attr(href)').getall() ))
        
        db.execute("SELECT post_id,meta_value FROM wp_postmeta WHERE meta_key = 'ffn_book_id' AND meta_value IN (" + ','.join(['%s' for i in range(len(all_book_ids))]) + ")", all_book_ids )
        book_ids = {}
        post_ids = {}
        for key, value in dict(db.fetchall()).items():
            book_ids[int(value)] = int(key)
            post_ids[int(key)] = int(value)
        chapters_count = {}
        if post_ids:
            db.execute("SELECT post_parent FROM wp_posts WHERE post_parent IN (" + ','.join( map(str,post_ids.keys()) ) + ")")
            chapters_result = db.fetchall()
            for item in chapters_result:
                item_is = post_ids[int(item[0])]
                if item_is in chapters_count:
                    continue
                chapters_count[item_is] = chapters_result.count(item)

        for book in response.css('#content_wrapper_inner > div.z-list'):
            ID = int(book.css("a.stitle::attr(href)").get().split('/')[2])
            Author_ID = int(book.css("a[href^='/u']::attr(href)").get().split('/')[2])

            raw_tags = ''.join(book.css('.z-padtop2.xgray::text,.z-padtop2.xgray *::text').getall()).split(' - ')
            tags = {}

            tags['Fandom'] = fandom
            tags['Language'] = raw_tags.pop(1)
            if 'Chapters: ' not in raw_tags[1]:
                tags['Genre'] = raw_tags.pop(1).split('/')
            if 'Complete' == raw_tags[-1]:
                tags['Status'] = raw_tags.pop(-1)
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
            # Filter
            next_book = False
            for int_tag in ['Chapters','Words','Reviews','Favs','Follows']:
                limits = settings.crawl['filter'][int_tag] or []
                lfrom = limits[0] or 0
                lto = limits[1] or 90000000000
                if (int_tag not in tags):
                    tags[int_tag] = 0
                if (tags[int_tag] < lfrom or tags[int_tag] > lto ):
                    next_book = True
                    break

            # Existence Check
            if next_book == True:
                continue
            if ID in (self.current):
                continue
            elif ID in (settings.crawl["blocked"]['ids'] or []):
                continue
            elif Author_ID in (settings.crawl["blocked"]['authors'] or []):
                continue
            elif (ID in self.scraped):
                continue
            elif (ID not in book_ids):
                existing_chapters = 0
            elif (chapters_count[ID] < tags['Chapters']):
                existing_chapters = chapters_count[ID]
            else:
                continue
            self.current.append(ID)
            book_data = {
                '_id'           : ID,
                'Title'         : book.css("a.stitle::text").get(),
                'Author ID'     : Author_ID,
                'Author Name'   : book.css("a[href^='/u']::text").get(),
                'Description'   : book.css("div.z-indent.z-padtop::text").get(),
                'Tags'          : tags,
                'Exists'        : False if existing_chapters == 0 else book_ids[ID],
                'Chapters'      : []
            }
            first_time = book.css('.z-padtop2.xgray > span:nth-of-type(1)::attr(data-xutime)').get()
            second_time = book.css('.z-padtop2.xgray > span:nth-of-type(2)::attr(data-xutime)').get()
            if second_time is not None:
                book_data['Updated'] = int(first_time)
                book_data['Published'] = int(second_time)
            else:
                book_data['Published'] = int(first_time)

            yield scrapy.Request(
                response.urljoin('/s/' + str(book_data['_id']) + '/' + str(existing_chapters + 1) ),
                callback = self.parseChapter,
                cb_kwargs = {
                    "book"          : book_data,
                }
            )

        if (response.xpath('//*[@id="content_wrapper_inner"]/center[1]/b[1]/text()').get() is not None):
            pg = int(response.xpath('//*[@id="content_wrapper_inner"]/center[1]/b[1]/text()').get())
            next_pg_attr = response.xpath('//*[@id="content_wrapper_inner"]/center[1]/a[contains(text(),\'Next »\')]').attrib
            if ("href" in next_pg_attr) & (pg < self.max_pages):
                next_pg = next_pg_attr['href']
                yield scrapy.Request(
                    response.urljoin(next_pg),
                    callback = self.parse
                )
    def parseChapter(self, response, book):
        title = response.css('select#chap_select > option[selected]::text').get()
        if (title is None):
            title = '1. Chapter 1'
        title = title.lstrip('123456789')[2:]
        cont = ''.join(response.css('#storytext > p').getall())
        book['Chapters'].append({
            "title"     : title,
            "content"   : cont
        })
        next_btn = response.css('#chap_select + button.btn::attr(onclick)').get()
        if (next_btn is not None):
            yield scrapy.Request(
                response.urljoin(next_btn.replace('self.location=\'','').rstrip('\'')),
                callback = self.parseChapter,
                cb_kwargs = {
                    "book"          : book,
                }
            )
        else:
            with open((settings.crawl['dump_dir'] or "") + str(int(time.time())) + "-ffn.jsonl", "a+") as dump_file:
                dump_file.write( json.dumps(book) + '\n')
            yield {'ID': book['_id']}

# Run "scrapy crawl ffn" to test