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
                'filter': {
                    'Favs'              : [0,5000000000000000],
                    'Chapters'          : [0,5000000000000000],
                    'Words'             : [0,5000000000000000],
                    'Reviews'           : [0,5000000000000000],
                    'Follows'           : [0,5000000000000000]
                }
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
                },
                "ffn-authorPM": {
                    "email": "norig98466@brosj.net",
                    "password": "fnjewknmfkmlkewr32u8jr8093j0940932",
                    "cookies": {
                        "finn": "553b2c2346349cc92f98f9c677b5d76dea4646ad27e74bb6e8c4a33366e87c0d",
                        "fknn": "e51518a5aa16709c6104e102e330d405a4cebb13bf0fb5d0d38f5b40d63d4a00",
                        "funn": "norig98466"
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

