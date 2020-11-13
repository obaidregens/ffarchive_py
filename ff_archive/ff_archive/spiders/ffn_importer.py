import os
import glob
import time
import datetime
import scrapy
import mysql.connector
import re
import json
import ff_archive.spiders.crawl_settings as crawl_settings
import sqlite3
import lxml.html.clean as clean

# HTML Cleaner
cleaner = clean.Cleaner(safe_attrs_only=True, safe_attrs=set(["style"]),page_structure=False)


settings = crawl_settings.settings()
lite_connection = sqlite3.connect("CharacterMaps.db")
liteDB = lite_connection.cursor()

sql_connection = mysql.connector.connect(
  host = "localhost",
  user = settings.db["user"],
  password = settings.db["password"],
  database = settings.db["name"]
)
db = sql_connection.cursor()
rating_map = {
    'K'         : 'General Audiences',
    'K+'        : 'Older Kids',
    'T'         : 'Teen & Up',
    'M'         : 'Mature'
}

a_imported = []
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
def str_word_count( string , format = 0 , charlist = '' ):
	if isinstance( string , str ):
		words = re.sub( '[^\w '+ charlist +']' , '' , string ) #Remove everything except alphanumeric, spaces and chars from charlist
		words = words.replace( '  ' , ' ' ).split( ' ' ) #Replacing double spaces with single space and creating list
		if format == 0:
			return len( words )
		elif format == 1:
			return words
		elif format == 2:
			result = {}
			for word in words:
				result[ string.find( word ) ] = word
			return result
	return False
def canImport(author, story):
    if (str(author) not in authorIds):
        return False
    if (authorIds[str(author)]["include"] == "all"):
        return True
    if (str(story) in authorIds[str(author)]["include"]):
        return True
    return False
def book_ids_from_links(book_link):
    return int(book_link.split('/')[2])
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
def insertStory(story):
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

    author_ID = str(story["Author ID"])
    user_id = authorIds[author_ID]["user_id"]
    date = datetime.datetime.fromtimestamp(story["Published"]).strftime('%Y-%m-%d %H:%M:%S')
    modified = date
    if ("Updated" in story):
        modified = datetime.datetime.fromtimestamp(story["Updated"]).strftime('%Y-%m-%d %H:%M:%S')
    if (story["Existing"] == False):
        # Insert Story
        sql = "INSERT INTO wp_posts (post_author,post_date,post_date_gmt,post_content,post_title,post_excerpt,ping_status,to_ping,pinged,post_modified,post_modified_gmt,post_content_filtered,post_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        val = (user_id,date,date,"",story["Title"],story["Description"],'closed',"","",modified,modified,"",'book')
        db.execute(sql, val)
        sql_connection.commit()
        storyID = db.lastrowid
        metaVal = [
            (storyID,'author_name',story["Author Name"]),
            (storyID,'ffn_author_id',author_ID),
            (storyID,'ffn_book_id',story["_id"])
        ]
        # Add Tags
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
        # Tags - Language
        connectTerm(storyID,ensureTerm(story["Tags"]["Language"],'language'))
        # Tags - Status
        connectTerm(storyID,ensureTerm(story["Tags"]["Status"],'status'))
        # Tags - Rated
        connectTerm(storyID,ensureTerm(rating_map[story["Tags"]["Rated"]],'rating'))
        # Tags - Genre
        for genreName in story["Tags"].get("Genre",[]):
            connectTerm(storyID,ensureTerm(genreName,'genre'))
        # Tags - Pairing
        for relationship in story["Tags"].get("Relationships",[]):
            relationshipCharacters = []
            for char in relationship:
                relationshipCharacters.append(characterIdOfName[char])
            insertPairing(storyID,relationshipCharacters)
        updateImport = """
        UPDATE import_stories
        SET import_status='live', story_id=%s, import_time=%s, import_favs=%s,import_follows=%s
        WHERE import_from='ffn' AND import_story=%s 
        """
        db.execute(updateImport,[storyID,int(time.time()),story["Tags"].get("Favs",0),story["Tags"].get("Follows",0),story["_id"]])
    else:
        # Update Story Time as per FFN for Updating and Reimporting Stories
        storyID = int(story["Existing"])
        db.execute("""
        UPDATE wp_posts
        SET post_modified=%s, post_modified_gmt=%s
        WHERE ID=%s
        """,[modified,modified,storyID])
        metaVal = []
    if story["Reimport"] == True:
        # Set to Live
        updateImport = """
        UPDATE import_stories
        SET import_status='live'
        WHERE import_from='ffn'
        AND story_id = %s
        AND import_story=%s
        AND import_status='reimport' 
        """
        db.execute(updateImport,[ storyID, story["_id"] ])
        # Get current chapters
        sql = """
        SELECT b.meta_value,a.ID FROM wp_posts as a
        INNER JOIN wp_postmeta as b ON a.ID = b.post_id
        WHERE a.post_parent = %s
        AND a.post_type = 'chapter'
        AND b.meta_key = 'chapter_order'
        """
        db.execute(sql,[storyID])
        chapters = {int(tup[0]):int(tup[1]) for tup in db.fetchall()}
        toDelete = []
        for i in list(range(len(story["Chapters"]),len(chapters))):
            toDelete.append(chapters[i+1])
        if len(toDelete) > 0:
            db.execute("DELETE FROM wp_posts WHERE ID IN (" + sqlPlaceholder(len(toDelete)) + ")",toDelete)

        chapterIndex = 1
        for chapter in story["Chapters"]:
            if chapterIndex in chapters:
                db.execute(
                    "UPDATE wp_posts SET post_content = %s, post_title = %s WHERE ID = %s",
                    [chapter['content'],chapter['title'],chapters[chapterIndex]]
                )
                # Update Word Count
                db.execute(
                    "UPDATE wp_postmeta SET meta_value = %s WHERE meta_key = 'word-count' AND post_id = %s",
                    [chapter["wordCount"],chapters[chapterIndex]]
                )
            else:
                chapter_id = dbInsert("wp_posts",{
                    "post_author": user_id,
                    "post_date": modified,
                    "post_date_gmt": modified,
                    "post_content": chapter["content"],
                    "post_title": chapter["title"],
                    "post_excerpt": "",
                    "ping_status": "closed",
                    "to_ping": "",
                    "pinged": "",
                    "post_modified": modified,
                    "post_modified_gmt": modified,
                    "post_content_filtered": "",
                    "post_parent": storyID,
                    "post_type": "chapter"
                })
                metaVal.append((chapter_id,'word-count',chapter["wordCount"]))
                metaVal.append(( chapter_id, 'chapter_order', chapterIndex ))
            chapterIndex += 1
    else:
        # Chapter
        chapter_sql = "INSERT INTO wp_posts (post_author,post_date,post_date_gmt,post_content,post_title,post_excerpt,ping_status,to_ping,pinged,post_modified,post_modified_gmt,post_content_filtered,post_parent,post_type) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        chapterIndex = story.get("chapterStartAt",1)
        totalWords = 0
        for chapter in story["Chapters"]:
            # Insert Chapter
            chapter_val = (user_id,modified,modified,chapter["content"],chapter["title"],"",'closed',"","",modified,modified,"",storyID,'chapter')
            db.execute(chapter_sql, chapter_val)
            sql_connection.commit()
            chapterID = db.lastrowid
            # Add to Chapter Meta Value
            totalWords += chapter["wordCount"]
            metaVal.append((chapterID,'word-count',chapter["wordCount"]))
            metaVal.append((chapterID,'chapter_order',chapterIndex))
            chapterIndex += 1
    
    metaSql = "INSERT INTO wp_postmeta (post_id,meta_key,meta_value) VALUES (%s, %s, %s)"
    db.executemany(metaSql,metaVal)

    if story["Reimport"] == True or story["Existing"] == False:
        # Now Let's add a notification if all users stories have been done.
        a_imported.append(str(story["_id"]))
        if len(set(authorIds[str(author_ID)]["include"]) - set(a_imported)) < 1:
            db.execute(
                """
                INSERT INTO notifications (user_id,notification_type,type_of,type_of_id,type_by,type_by_id,email_status,timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                [user_id,'stories_imported','user',user_id,'ffn_user',author_ID,'none',time.time()]
            )
        sql_connection.commit()
    # Update Words
    db.execute("""
    SELECT SUM(wp_postmeta.meta_value) as c FROM wp_postmeta
    INNER JOIN wp_posts ON wp_posts.ID = wp_postmeta.post_id
    WHERE wp_postmeta.meta_key = 'word-count'
    AND wp_posts.post_parent = %s
    """,[storyID])
    word_count = int(db.fetchone()[0])
    db.execute("""
    UPDATE wp_postmeta
    SET meta_value = %s
    WHERE post_id=%s AND meta_key="word-count"
    """,[word_count,storyID])
    sql_connection.commit()
def sqlPlaceholder(l):
    return ",".join(['%s'] * l )
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
    sql = "INSERT INTO " + table + " (" + ",".join(insertData.keys()) + ")" + " VALUES (" + sqlPlaceholder(len(insertData)) + ")"
    db.execute(sql,list( insertData.values()))
    sql_connection.commit()
    return db.lastrowid

db.execute("SELECT import_user,user_id,import_story FROM import_stories WHERE import_status IN (%s,%s,%s)",['pending','live','reimport'])
authorIds = {}
for row in db.fetchall():
    if not str(row[0]) in authorIds:
        authorIds[str(row[0])] = {
            "include"   : [],
            "user_id"   : row[1]
        }
    authorIds[str(row[0])]["include"].append(str(row[2]))
class ffnImporter(scrapy.Spider):
    name = "ffn_importer"
    start_urls = [ ("https://www.fanfiction.net/u/" + str(author_ID)) for author_ID in authorIds.keys() ]

    def __init__(self, name=None, **kwargs):
        _dir = settings.crawl['dump_dir'] or ""
        if (_dir == ''):
            _dir = os.getcwd()
        self.current = []
    def parse(self, response):
        Author_ID = int(response.css("#content_wrapper_inner > a.pull-right:first-child").attrib["href"][8:-1])
        Author_Name = response.css("#content_wrapper_inner > a.pull-right:first-child + span::text").get().lstrip()

        db.execute("SELECT post_id FROM wp_postmeta WHERE meta_key = 'ffn_author_id' AND meta_value = %s", [Author_ID] )
        storyIds = [tup[0] for tup in db.fetchall()]
        ffnIds = {}
        storyChaptersExisting = {}
        importStatus = {}
        if (len(storyIds) > 0):
            storyIdsPlace = sqlPlaceholder(len(storyIds))
            db.execute(
                "SELECT story_id,import_story,import_status FROM import_stories " +
                "WHERE story_id IN(" + storyIdsPlace + ")"
            , storyIds )
            import_stories_list = db.fetchall()
            for row in import_stories_list:
                importStatus[int(row[0])] = row[2]
                ffnIds[row[0]] = row[1]

            db.execute("SELECT post_parent FROM wp_posts WHERE post_parent IN (" + storyIdsPlace + ")",storyIds)
            for tup in db.fetchall():
                theID = int(ffnIds[tup[0]])
                storyChaptersExisting[theID] = storyChaptersExisting.get(theID,0) + 1
        storyIdsLookup = {value : key for (key, value) in ffnIds.items()}
        for story in response.css("div.z-list.mystories"):
            storyData = parseStory(story)
            storyData["Author ID"] = Author_ID
            storyData["Author Name"] = Author_Name
            chapterStartAt = (storyChaptersExisting.get(int(storyData["_id"]),0)) + 1
            storyData["Reimport"] = False
            if importStatus.get(int( storyIdsLookup.get(int(storyData["_id"]),0) ),'dont_reimport') == "reimport":
                storyData["Reimport"] = True
                chapterStartAt = 1
            storyData["Existing"] = storyIdsLookup.get(int(storyData["_id"]),False)
            # The support for importing new chapters does exist, but that won't be used for now.
            # Thus the condition below
            # if (storyData["Existing"] != False):
            #     continue
            storyData["chapterStartAt"] = chapterStartAt
            if canImport(Author_ID,storyData["_id"]) == False:
                continue
            if (chapterStartAt > storyData["Tags"]["Chapters"]):
                continue
            self.current.append(storyData["_id"])
            yield response.follow(
                "/s/" + str(storyData["_id"]) + "/" + str(chapterStartAt),
                callback=self.parseChapter,
                cb_kwargs = {
                    "storyData"         : storyData
                }
            )
    def parseChapter(self, response, storyData):
        isCrossover = response.css('#pre_story_links > span > img[src="//ff74.b-cdn.net/static/fcons/arrow-switch.png"]').get() is not None
        if isCrossover:
            storyData["Tags"]["Fandom"] = response.css('#pre_story_links > span > a::text').get()[:-10].split(' + ')
        else:
            storyData["Tags"]["Category"] = response.css("#pre_story_links > span > a:first-of-type::text").get()
            storyData["Tags"]["Fandom"] = [response.css('#pre_story_links > span > a:last-child::text').get()]
        title = response.css('select#chap_select > option[selected]::text').get()
        if (title is None):
            title = '1. Chapter 1'
        chapterArr = title.split(". ",1)
        currentChapter = int(chapterArr[0])
        title = chapterArr[1]
        cont = ''.join(response.css('#storytext > p,#storytext > hr').getall())
        if len(cont) > 0:
            # Strip Div Tag Cleaner adds
            cont = cleaner.clean_html(cont)[5:-6]
            storyData['Chapters'].append({
                "title"     : title,
                "content"   : cont,
                "wordCount" : str_word_count( " ".join(response.css("#storytext > p::text").getall() )),
            })
            next_btn = response.css('#chap_select + button.btn::attr(onclick)').get()
            if storyData["Tags"]["Chapters"] > currentChapter and next_btn is not None:
                yield response.follow(
                    next_btn.replace('self.location=\'','').rstrip('\''),
                    callback = self.parseChapter,
                    cb_kwargs = {
                        "storyData"         : storyData,
                    }
                )
            else:
                insertStory(storyData)
    def closed(self, reason):
        updateTermsCount()
# Run "scrapy crawl ffn" to test