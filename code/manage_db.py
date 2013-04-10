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
        sql = "insert into imdb_info(imdb_num, rank, rating, title, votes, douban_id) values(%s,%s,%s,%s,%s,%s)"
        param = (item[4], item[0], item[1], item[2], item[3], 'null')#douban_id need to be changed after search douban
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

