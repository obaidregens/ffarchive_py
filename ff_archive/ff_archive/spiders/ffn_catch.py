import scrapy
import mysql.connector
import json
import time
import ff_archive.spiders.crawl_settings as crawl_settings
import sqlite3

lite_connection = sqlite3.connect("CharacterMaps.db")
liteDB = lite_connection.cursor()

settings = crawl_settings.settings()

data = '["375915","375929","375999","375985","376024","376007","375972","375978","376162","376054","376038","376082","376066","376140","376036","376101","376291","376307","376353","376288","376420","376603","376851","376809","376789","376855","376787","376833","376764","376821","385692","376923","376799","376838","376903","376745","376742","376734","376782","376736","376711","376709","376707","376731","376705","385635","385682","385675","376700","385668","385646","376791","376702","376692","385643","376697","376694","385629","376689","376662","376686","376683","376649","385627","385633","376638","376674","376654","376651","376636","376634","376632","376678","376630","376617","376615","385631","376664","376669","376582","376577","376619","376589","376579","385671","376592","376568","376566","376561","376584","376878","376596","376748","376608","385656","376640","376916","376574","376739","376804","376871","376862","376570","376860","376874","376864","376849","376845","376831","376867","376826","376819","376815","376623","377525","377571","377585","377420","385748","377481","377412","377406","377402","377392","377370","377344","377340","385783","377325","382561","377646","377650","377648","377682","377742","377826","381498","381500","381502","381504","381509","381519","381529","381639","381541","382233","382220","382225","382214","382425","382444","383190","383148","383134","383127","383143","383131","383138","383231","384190","384051","384153","384020","383783","383575","385076","385318","387955","387856","385484","386108","386070","385971","386316","386484","386536","386458","386452","386448","386505","386597","386695","386843","386930","386875","386845","386841","387075","387064","386851","386853","386849","387052","387046","387038","387036","386855","387028","387018","387010","387000","386993","386989","386987","386979","386977","386975","386973","386969","386965","386961","386957","386861","386951","386942","386928","386926","386920","386898","386886","386882","386880","387154","396891","387163","387317","387236","387234","387354","387346","387344","387342","387338","387333","387249","387327","387325","387313","387301","387287","387285","387283","387279","387273","387375","387265","387263","387257","387255","387527","387470","387497","387472","387466","387565","387573","387641","387660","387646","387814","387916","387776","387833","388150","388080","388091","388312","389304","389366","389556","389522","389526","390791","390795","390801","390799","390813","390811","390809","390807","391358","391354","391352","391344","391336","391332","391328","391326","391324","391322","391320","391318","391316","391314","391312","391288","390872","391556","391208","391169","391465","391383","391399","391172","391296","391483","391226","391246","390908","391132","391017","390912","390884","391063","391084","390896","390862","390824","390953","390822","390818","390923","390835","391636","391676","392159","392182","391850","391962","391956","391919","391748","392133","391885","392002","391987","391804","391968","391795","391793","391791","391906","391863","391771","391769","391767","391797","392401","392345","392374","392365","392653","392717","392831","392939","392865","392922","392885","392826","392911","392873","392899","393162","393004","396901","393036","393054","392995","393056","393086","393050","393145","393059","393027","393025","393043","393012","393066","393098","393000","393008","393075","393201","393206","393224","393203","394153","393931","393928","393889","393885","394474","393853","393849","393835","393833","393423","393831","393829","394423","394069","394321","394270","394372","393807","393441","393787","393785","393781","393779","393758","393753","393749","393747","393742","393740","393736","393734","393774","393744","393714","393712","393703","396869","393705","393685","393683","393687","393676","393674","393670","393678","393665","393663","393789","393661","396880","393760","393652","393667","393650","393640","393634","393630","393657","393617","393948","393587","393585","393612","396875","393575","393569","393690","393537","393532","393530","393539","393519","393515","393513","393490","393488","393589","393483","393481","393479","393477","393471","393467","393552","393597","393452","393450","393542","393454","393560","393496","393446","393435","393502","393425","394920","395292","395142","396443","396382","396467","396350","396656","396414","396762","396769","396938","396940","396949","397065","397076","397112","397177","397922","397695","397896","397653","397465","397109","397554","397649","397671","397461","397680","397368","397360","397389","397283","397328","397234","397340","397779","397703","397603","397515","397833","397195","397556","398439","398460","398524","398674","398516","398499","398504","398655","398547","398697","398642","398721","398627","398577","398945","398975","398870","398852","398823","398821","398819","398817","398815","398769","398807","398797","398771","398939","398941","399273","399271","399300","400295","399774","399816","399600","399504","400490","400386","400518","400217","400209","400253","400153","400281","400225","400143","400266","400437","400155","400200","400367","400237","400080","400161","400191","400168","400111","400063","400002","400000","400461","400145","399998","400058","400047","399982","399980","399978","400052","399973","400115","399971","400176","399975","399941","399939","399937","399992","399935","399933","399967","399294","399931","399925","399923","400037","399921","400098","399311","399883","399984","400403","399853","399851","399905","399791","399797","400124","400065","399789","400082","399793","399759","399757","399745","399754","399740","399742","399896","399738","399736","399855","399885","399351","399525","399298","399296","399498","399363","400306","399909","399710","399708","399718","399704","400016","399714","399702","399692","399688","399686","399684","399682","399678","399676","399800","399674","399672","399668","399670","399657","399655","399649","399643","399641","399639","399628","399626","399624","399622","399761","399589","399587","399583","399581","399579","399577","399575","399573","399571","399694","399865","399551","399549","399547","399545","399543","399307","399305","399434","399342","400560","400992","401005","400580","400725","400616","400662","400632","401291","400704","400747","400775","401228","401150","401148","401246","401152","401157","401138","401132","401360","401217","401128","401126","401124","401122","401099","401097","401267","401095","401074","401072","401070","401068","401395","401439","401142","401057","401065","401055","401053","401062","401076","401059","401042","401040","401038","401036","400990","401050","401047","401044","400988","400986","400984","400982","400980","400978","400976","400974","400965","400963","400961","400568","400933","400931","400903","400826","400967","401194","400798","400773","401315","401080","400771","400818","400769","400767","400745","400743","401486","400723","400702","400700","400698","401103","400681","400679","401165","401553","400800","400612","400602","400855","400600","400598","400596","400683","400935","400584","400905","400648","400578","400877","400576","400570","400604","400828"]'
ids = list(map(str,json.loads(data)))

# SQL
sql_connection = mysql.connector.connect(
    host = "localhost",
    user = settings.db["user"],
    password = settings.db["password"],
    database = settings.db["name"]
)
db = sql_connection.cursor()

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
def sqlPlaceholder(a):
    return ",".join(['%s'] * len(a) )
def insertPairing(storyID,characters):
    if len(characters) < 2:
        return False
    db.execute("SELECT pairing_id,character_id FROM character_pairings")
    r = db.fetchall()
    characters = list(map(str,characters))
    characters.sort()
    n = {}
    for pairing_id,character_id in r:
        n[pairing_id] = n.get(pairing_id,[])
        n[pairing_id].append(character_id)
    pp = 0
    for pairing_id,characters_of in n.items():
        characters_of = list(map(str,characters_of))
        characters_of.sort()
        if characters == characters_of:
            pp = pairing_id
            break
    # Pairing ID Got
    if pp == 0:
        db.execute("SELECT MAX(pairing_id) AS m FROM character_pairings")
        existsPair = db.fetchone()
        pp = 1
        if existsPair is not None and existsPair[0] is not None:
            pp = int(existsPair[0])+1
        sql = "INSERT INTO character_pairings (pairing_id, character_id) VALUES " + ",".join( ["('" + str(pp) + "', %s)"] * len(characters) )
        db.execute(sql,characters)
    dbInsert(
        'pairing_relationships',
        {
            'pairing_id'    : pp,
            'book_id'       : storyID,
            'priority'      : 'major',
            'added_time'    : int(time.time())
        }
    )
    return int(pp)
def dbInsert(table,insertData):

    sql = "INSERT INTO " + table + " (" + ",".join(insertData.keys()) + ")" + " VALUES (" + sqlPlaceholder(insertData) + ")"
    db.execute(sql,list( insertData.values()))
    sql_connection.commit()
    return db.lastrowid
def find_fandom(fandom):
    sql = "SELECT fandom,category,characters FROM ffnMap WHERE fandom = ?"
    liteDB.execute(sql,[fandom])
    results = liteDB.fetchall()
    if len(results) == 0:
        return False
    return {
        "fandom":       results[0][0],
        "category":     results[0][1],
        "characters":   json.loads(results[0][2])
    }
def ensureTerm(term, taxonomy, parent=0):
    sql = """
    SELECT tt.term_id, tt.term_taxonomy_id
    FROM wp_terms AS t
    INNER JOIN wp_term_taxonomy as tt ON tt.term_id = t.term_id
    WHERE t.name = %s
    AND tt.parent = %s AND tt.taxonomy = %s
    ORDER BY t.term_id ASC
    LIMIT 1
    """
    db.execute(sql, [term, parent, taxonomy])
    term_row = db.fetchone()
    if term_row is not None:
        return int(term_row[0])
    
    insert1 = "INSERT INTO wp_terms (name,slug) VALUES (%s, %s)"
    db.execute(insert1,[term,term.lower().strip().replace(' ','-')])
    sql_connection.commit()
    term_id = db.lastrowid
    insert2 = "INSERT INTO wp_term_taxonomy (term_taxonomy_id,term_id,taxonomy,description,parent) VALUES (%s,%s, %s, %s, %s)"
    db.execute(insert2,[term_id,term_id,taxonomy,"",parent])
    sql_connection.commit()
    return int(term_id)
def connectTerm(storyID,termID):
    sql = "INSERT INTO wp_term_relationships (object_id,term_taxonomy_id) VALUES (%s, %s)"
    try:
        db.execute(sql,[storyID,termID])
        sql_connection.commit()
    except:
        pass
def updateTermsCount():
    sql = """
    UPDATE wp_term_taxonomy SET count = (
    SELECT COUNT(*) FROM wp_term_relationships rel 
        LEFT JOIN wp_posts po ON (po.ID = rel.object_id) 
        WHERE 
            rel.term_taxonomy_id = wp_term_taxonomy.term_taxonomy_id 
            AND 
            wp_term_taxonomy.taxonomy NOT IN ('link_category')
            AND 
            po.post_status IN ('publish')
    )
    """
    db.execute(sql)
    sql_connection.commit()

db.execute("SELECT import_user,story_id,import_story FROM import_stories WHERE story_id IN (" + sqlPlaceholder(ids) + ")",ids)
authorIds = {}
for row in db.fetchall():
    if str(row[0]) not in authorIds:
        authorIds[str(row[0])] = {
        }
    authorIds[str(row[0])][str(row[2])] = str(row[1])
class fixPairings(scrapy.Spider):
    name = "fixPairings"
    start_urls = [ ("https://www.fanfiction.net/u/" + str(author_ID)) for author_ID in authorIds.keys() ]
    def parse(self, response) :
        Author_ID = int(response.css("#content_wrapper_inner > a.pull-right:first-child").attrib["href"][8:-1])
        for storyBlock in response.css("div.z-list.mystories"):
            story = parseStory(storyBlock)
            if str(story["_id"]) not in authorIds[str(Author_ID)]:
                continue
            yield response.follow(
                storyBlock.css(".stitle::attr(href)").get(),
                callback=self.parseChapter,
                cb_kwargs = {
                    "story"            : story,
                    "Author_ID"        : Author_ID
                }
            )

    def parseChapter(self, response, story, Author_ID):
        storyID = authorIds[str(Author_ID)][str(story["_id"])]
        isCrossover = response.css('#pre_story_links > span > img[src="//ff74.b-cdn.net/static/fcons/arrow-switch.png"]').get() is not None
        if isCrossover:
            story["Tags"]["Fandom"] = response.css('#pre_story_links > span > a::text').get()[:-10].split(' + ')
        else:
            story["Tags"]["Category"] = response.css("#pre_story_links > span > a:first-of-type::text").get()
            story["Tags"]["Fandom"] = [response.css('#pre_story_links > span > a:last-child::text').get()]
        
        # Update
        character_fandoms = {}
        characterOfFandoms = {}
        fandomOfName = {}
        # First Confirm that Characters & Fandoms exist in Map. Else Reject
        for fandomName in story["Tags"]["Fandom"]:
            fandom = find_fandom(fandomName)
            if fandom == False:
                print(fandomName)
                print('Fandom not found')
                return
            fandomOfName[fandomName] = fandom
            for characterName in story["Tags"].get("All Characters",[]):
                if characterName not in fandom["characters"]:
                    continue
                character_fandoms[characterName] = fandom
                if (fandomName not in characterOfFandoms):
                    characterOfFandoms[fandomName] = []
                characterOfFandoms[fandomName].append(characterName)
        if sorted(list(character_fandoms.keys())) != sorted((story["Tags"].get("All Characters",[]))):
            print( ",".join(character_fandoms.keys()) + " != " + ",".join(story["Tags"]["All Characters"]) )
            return
        # Both of the above returns indicate that something has not been found in mapper
        
        # Delete Fandom, Characters And Pairing
        sql = """
        SELECT a.term_taxonomy_id FROM wp_term_relationships as a
        INNER JOIN wp_term_taxonomy as b ON
            b.term_id = a.term_taxonomy_id
        WHERE a.object_id = %s
        AND (
            b.taxonomy = 'character'
            OR (
                b.taxonomy = 'category'
                AND b.parent != 0
            )
        );
        """
        db.execute(sql,[storyID])
        deleting = [tup[0] for tup in db.fetchall()]
        if (len(deleting) > 0):
            db.execute(
                "DELETE FROM wp_term_relationships WHERE object_id = %s AND term_taxonomy_id IN(" + sqlPlaceholder(deleting) + ")"
            ,[storyID] + deleting)
        db.execute("DELETE FROM pairing_relationships WHERE book_id = %s",[str(storyID)])
        # Tags - Fandom
        characterIdOfName = {}
        for fandomName in story["Tags"]["Fandom"]:
            fandom = fandomOfName[fandomName]
            categoryID = ensureTerm(fandom["category"].capitalize(),'category')
            fandomID = ensureTerm(fandom["fandom"],'category',categoryID)
            connectTerm(storyID,fandomID)
            for characterName in characterOfFandoms.get(fandomName,[]):
                if characterName == "OC":
                    characterID = ensureTerm(characterName,'character',0)
                else:
                    characterID = ensureTerm(characterName,'character',fandomID)
                characterIdOfName[characterName] = characterID
                connectTerm(storyID,characterID)
                # Tags - Pairing
        for relationship in story["Tags"].get("Relationships",[]):
            relationshipCharacters = []
            for char in relationship:
                relationshipCharacters.append(characterIdOfName[char])
            insertPairing(storyID,relationshipCharacters)

        print("X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X")
        print("X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X")
        print(storyID)
        print("X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X")
        print("X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X-X")
        pass