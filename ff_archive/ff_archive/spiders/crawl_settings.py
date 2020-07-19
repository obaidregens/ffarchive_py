import pathlib
import json

class settings:
    filename = str(pathlib.Path(__file__).parent.absolute()) + "/.settings"
    def __init__(self):
        self.urls = []
        self.crawl = {}
        self.db = {}
        self.creds = {}
        file_is = open(settings.filename, "r+")
        raw = file_is.read()
        if ( len(raw) <= 1):
            return
        self.urls = raw.split('\n')
        file_is.close()
        settings_dict = json.loads(self.urls.pop(0))
        self.crawl = settings_dict['crawl']
        self.db = settings_dict['db']
        self.creds = settings_dict['creds']
    def save(self):
        seperator = "\n"
        json_settings = json.dumps({
            "db"    : self.db,
            "crawl" : self.crawl,
            "creds" : self.creds
        })
        url = seperator.join(self.urls)
        f = open(settings.filename, "w")
        f.write(json_settings + seperator + url)
        f.close()
    def sample(self):
        seperator = "\n"
        json_settings = json.dumps({
            "db"    : {
                "name"      : "ffonline",
                "user"      : 'root',
                'password'  : ''
            },
            "crawl" : {
                'max_pages'             : 1,
                'dump_dir'              : '',
                'blocked'               : {
                    'ids'       : [],
                    'authors'   : []
                },
            },
            "creds" : {
                "ffn" : {
                    "email"      : "1",
                    "password"  : "cefe",
                    "cookies"   : {
                        "finn": "a",
                        "fknn": "b",
                        "funn": "c"
                    }
                }
            }
        })
        url = seperator.join([
            "https://www.fanfiction.net/book/Harry-Potter/?&srt=4&r=10"
        ])
        f = open(settings.filename, "w")
        f.write(json_settings + seperator + url)
        f.close()

