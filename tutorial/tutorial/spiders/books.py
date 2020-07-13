import scrapy


class BooksCrawler(scrapy.Spider):
    name = "books"
    start_urls = [
        "https://www.fanfiction.net/book/Harry-Potter/?&srt=1&r=10",
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
            book_data = {
                'ID'            : int(book.css("a.stitle::attr(href)").get().split('/')[2]),
                'Title'         : book.css("a.stitle::text").get(),
                'Author ID'     : int(book.css("a[href^='/u']::attr(href)").get().split('/')[2]),
                'Author'        : book.css("a[href^='/u']::text").get(),
                'Description'   : book.css("div.z-indent.z-padtop::text").get(),
                'Tags'          : tags
            }

            first_time = book.css('.z-padtop2.xgray > span:nth-of-type(1)::attr(data-xutime)').get()
            second_time = book.css('.z-padtop2.xgray > span:nth-of-type(2)::attr(data-xutime)').get()
            if second_time is not None:
                book_data['Updated'] = int(first_time)
                book_data['Published'] = int(second_time)
            else:
                book_data['Published'] = int(first_time)

            yield book_data

        # next_page = response.css('li.next a::attr(href)').get()
        # if next_page is not None:
        #     next_page = response.urljoin(next_page)
        #     yield scrapy.Request(next_page, callback=self.parse)

# Run "scrapy crawl books -o books.json" to test