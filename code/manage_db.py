import MySQLdb

import urllib
import urllib2

import json

import time

def store_ranklist(list):
    "store the ranklist into mysql"

    conn=MySQLdb.connect(host="localhost",user="root",passwd="",db="film_searcher_db",charset="utf8")
    cursor = conn.cursor()
    
    for item in list:
        sql = "insert into imdb_info(imdb_num, rank, rating, title, votes, douban_id, has_detail) values(%s,%s,%s,%s,%s,%s,%s)"
        param = (item[4], item[0], item[1], item[2], item[3], 'null', 0)#douban_id need to be changed after search douban
        cursor.execute(sql, param)
    #end of for

    print "succeed in storing the ranklist"

    conn.commit()
    cursor.close()
    conn.close()
#end of def

def update_douban_id():
    "use the imdb to get douban_id from the douban api_v2, root url:https://api.douban.com/v2/movie/search?q=, and update the imdb_info table"

    url = 'https://api.douban.com/v2/movie/search?q='

    conn=MySQLdb.connect(host="localhost",user="root",passwd="",db="film_searcher_db",charset="utf8")
    cursor = conn.cursor()

    cursor.execute('select * from imdb_info')
    results = cursor.fetchall()
    for re in results:
        if re[5] == None:   #if current item has no douban_id
            imdb_num = re[0].encode()
            request_url = url + imdb_num
            response = urllib2.urlopen(request_url)
            page = response.read()
            decode_json = json.loads(page)
            if decode_json['total'] == 1:
                douban_id = decode_json['subjects'][0]['id']
                cursor.execute("update imdb_info set douban_id = %s where imdb_num = %s", (douban_id, imdb_num))
            #end of if
            time.sleep(2)   #in case of exceeding the api access limit: 40 times per minute, if exceed the limit, change the mac add to get a new ip addr
            conn.commit()
        #end of if
    #end of for
    print "succeed in updating the douban_id"
    
    cursor.close()
    conn.close()
#end of def

def get_douban_info():
    "use the douban_id in the imdb_info db, to get the detail info from douban, and store the info in douban_info db"

    url = 'https://api.douban.com/v2/movie/subject/'

    conn=MySQLdb.connect(host="localhost",user="root",passwd="",db="film_searcher_db",charset="utf8")
    cursor = conn.cursor()

    cursor.execute('select * from imdb_info')
    results = cursor.fetchall()
    for re in results:
        if re[6] == 0:  #if current item has no detail info from douban
            douban_id = re[5].encode()
            request_url = url + douban_id
            response = urllib2.urlopen(request_url)
            page = response.read()
            decode_json = json.loads(page)

            casts = []  #change the casts into a string split by ','
            for cast in decode_json['casts']:
                casts.append(cast['id'] or ' ')
                casts.append(cast['name'] or ' ')
            #end of for

            directors = []  #change the directors into a string split by ','
            for director in decode_json['directors']:
                directors.append(director['id'] or ' ')
                directors.append(director['name'] or ' ')
            #end of for

            sql = 'insert into douban_info(rating_average, douban_site, year, images_large, alt, douban_id, title,\
                   genres, countries, casts, original_title, summary, subtype, director) values(%s,"%s","%s","%s","%s",\
                   "%s","%s","%s","%s","%s","%s","%s","%s","%s")'\
                   % (decode_json['rating']['average'], decode_json['douban_site'] or ' ', decode_json['year'],\
                      decode_json['images']['large'], decode_json['alt'], decode_json['id'],\
                      decode_json['title'], '-'.join(decode_json['genres']) or ' ', '-'.join(decode_json['countries']) or ' ',\
                      '-'.join(casts), decode_json['original_title'], decode_json['summary'].replace('"', '\''),\
                      decode_json['subtype'], '-'.join(directors))
            cursor.execute(sql)
            cursor.execute("update imdb_info set has_detail = 1 where douban_id = %s", (douban_id))
        #end of if
    #end of for

    print "succeed in getting douban info"
#end of def
