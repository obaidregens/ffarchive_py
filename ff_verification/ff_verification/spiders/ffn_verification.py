import scrapy
import mysql.connector
import json
import time
import ff_verification.spiders.crawl_settings as crawl_settings
settings = crawl_settings.settings()

# SQL get unverified
sql_connection = mysql.connector.connect(
  host = "localhost",
  user = settings.db["user"],
  password = settings.db["password"],
  database = settings.db["name"]
)
db = sql_connection.cursor()

db.execute("SELECT verification_ID, connection_user FROM user_connections WHERE connection_from = 'ffn' AND status = 'unverified'")
user_v_ids = dict(db.fetchall())
db.execute("SELECT ID, code, issued FROM verification_codes WHERE ID IN (" + ",".join(map(str,user_v_ids.keys())) + ")")
user_codes = {}
_t = int(time.time())
for code_tuple in db.fetchall():
    if _t - int(code_tuple[2]) > (60 * 30):
        continue
    userid = user_v_ids[code_tuple[0]]
    user_codes[userid] = code_tuple[1]
def verify_connection(user):
    db.execute(
        "UPDATE user_connections SET status = %s,link_timestamp = %d WHERE connection_user = %s AND connection_from = %s AND status = %s",
        ['verified',_t,user,user,'ffn','unverified']
    )
    sql_connection.commit()

class ffnVerification(scrapy.Spider):
    name = "ffn_verification"
    start_urls = ["https://www.fanfiction.net/"]
    inbox_url = '/pm2/inbox.php'
    login_url = '/login.php?cache=bust'
    def parse(self, response):
        yield scrapy.Request(
            response.urljoin( self.inbox_url ),
            callback = self.inbox,
            cookies = settings.creds["ffn"]["cookies"]
        )
    def inbox(self, response):
        print(response.text)
        if (response.css('.gui_warning > a[href^="/login"]').get() is not None):
            yield scrapy.Request(
                response.urljoin( self.login_url ),
                callback = self.login,
            )
        else:
            conversation_links = response.css('#content_wrapper_inner > table .bubbledNNormal > a:nth-of-type(2)')
            yield from response.follow_all(
                conversation_links,
                callback = self.conversation,
                cookies = settings.creds["ffn"]["cookies"]
            )
    def conversation(self, response):
        last_msg = response.css('.round8.bubbledRight:last-child')
        code = last_msg.xpath('img[1]/following-sibling::text()').get()
        Author_ID = int(response.css('#gui_table2i > tbody > tr:nth-child(2) > td:nth-child(2) > a:nth-of-type(1)::attr(href)').get()[3:].rstrip('/'))
        if (Author_ID in user_codes & user_codes[Author_ID] == code ):
            verify_connection(Author_ID)

    def set_new_cookies(self, response):
        settings.creds["ffn"]["cookies"] = response.headers.getlist('Set-Cookie')
        settings.save()
        yield scrapy.Request(
            response.urljoin( self.login_url ),
            callback = self.login,
            cookies = settings.creds["ffn"]["cookies"]
        )
    def login(self, response):
        return scrapy.FormRequest.from_response(
            response,
            formname = 'login',
            formdata = {
                'email'     : settings.creds["ffn"]["email"],
                'password'  : settings.creds["ffn"]["password"]
            },
            callback = self.set_new_cookies
        )
