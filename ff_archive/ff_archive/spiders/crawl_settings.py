import pathlib
import json

class settings:
    filename = str(pathlib.Path(__file__).parent.absolute()) + "/.settings"
    def __init__(self):
        self.crawl = {}
        self.db = {}
        self.creds = {}
        with open(settings.filename, "r") as dump_file:
            settings_dict = json.loads(dump_file.read())
        self.crawl = settings_dict['crawl']
        self.db = settings_dict['db']
        self.creds = settings_dict['creds']
    def save (self):
        with open(settings.filename, "w+") as dump_file:
            dump_file.write(json.dumps({
                "crawl": self.crawl,
                "db": self.db,
                "creds": self.creds
            }))
