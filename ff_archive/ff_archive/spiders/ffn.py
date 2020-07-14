import scrapy
import pymongo

mongo = pymongo.MongoClient("mongodb://localhost:27017/")
ffn = mongo['ff_archive']['ffn']


class ffnCrawler(scrapy.Spider):
    max_books = 1000
    books_count = ffn.count_documents({})
    name = "ffn"
    start_urls = [
        "https://www.fanfiction.net/book/Harry-Potter/?&srt=5&r=10",
    ]

    def parse(self, response):
        for book in response.css('#content_wrapper_inner > div.z-list'):

            raw_tags = ''.join(book.css('.z-padtop2.xgray::text,.z-padtop2.xgray *::text').getall()).split(' - ')
            tags = {}
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
            # Existence Check
            ID = int(book.css("a.stitle::attr(href)").get().split('/')[2])
            existing = ffn.find_one({ "_id" : ID })
            if existing is not None :
                if len(existing['Chapters']) >= tags['Chapters']:
                    continue
            else :
                self.books_count += 1
            book_data = {
                '_id'           : ID,
                'Title'         : book.css("a.stitle::text").get(),
                'Author ID'     : int(book.css("a[href^='/u']::attr(href)").get().split('/')[2]),
                'Author Name'   : book.css("a[href^='/u']::text").get(),
                'Description'   : book.css("div.z-indent.z-padtop::text").get(),
                'Tags'          : tags,
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
                response.urljoin('/s/' + str(book_data['_id']) + '/1'),
                callback = self.parseChapter,
                cb_kwargs = {
                    "book"          : book_data,
                }
            )
        next_pg = response.xpath('//*[@id="content_wrapper_inner"]/center[1]/a[contains(text(),\'Next »\')]').attrib['href']
        if ( (next_pg is not None) & (self.books_count <= self.max_books) ):
            yield scrapy.Request(
                response.urljoin(next_pg),
                callback = self.parse
            )
    def parseChapter(self, response, book):
        cont = ''.join(response.css('#storytext > p').getall())
        book['Chapters'].append(cont)
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
            ffn.replace_one({'_id': book['_id']}, book, True )
            yield {'ID': book['_id'], 'count': self.books_count}

# Run "scrapy crawl ffn" to test