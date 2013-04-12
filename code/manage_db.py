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

def print_douban_info(result):
    "print the douban_info store in the list: result"

    details = '''rating_average: %.1f
                 douban_site: %s
                 year: %s
                 image_large: %s
                 alt: %s
                 douban_id: %s
                 title: %s
                 genres: %s
                 countries: %s
                 casts: %s
                 original_title: %s
                 summary: %s
                 subtype: %s
                 directors: %s''' % \
                 (result[0], result[1].encode('utf-8'), result[2].encode('utf-8'),\
                 result[3].encode('utf-8'), result[4].encode('utf-8'), result[5].encode('utf-8'),\
                 result[6].encode('utf-8'), result[7].encode('utf-8'), result[8].encode('utf-8'),\
                 result[9].encode('utf-8'),result[10].encode('utf-8'),result[11].encode('utf-8'),\
                 result[12].encode('utf-8'), result[13].encode('utf-8'))
    print details
#end of def

def search_film():
    "a module for user to search film in db"

    help_info = '''----------------------------------------
                   options:
                   1: search a film by imdb_num
                   2: search a film by douban_id
                   3: search a film by film_name
                   q: quit
                   h: print the help info
                   ----------------------------------------
                   your choice: '''

    choice = raw_input(help_info)

    conn=MySQLdb.connect(host="localhost",user="root",passwd="",db="film_searcher_db",charset="utf8")
    cursor = conn.cursor()

    while (choice != 'q'):
        if (choice == '1'):
            input_num = raw_input('please input the imdb_num:')
            sql = 'select * from imdb_info where imdb_num = "%s"' % (input_num)
            result_num = cursor.execute(sql)
            if (result_num == 0):
                print 'no such film!'
            else:
                result = cursor.fetchone()
                print "title: %s\trank: %d\trating: %.2f\tvotes: %s\tdouban_id: %s" % (result[3], result[1], result[2], result[4], result[5])
                need_detail = raw_input('need detail info? (y/n): ')
                if (need_detail == 'y'):
                    sql = 'select * from douban_info where douban_id = "%s"' % (result[5])
                    result_num = cursor.execute(sql)
                    if (result_num == 0):
                        print 'no details!'
                    else:
                        result = cursor.fetchone()
                        print_douban_info(result)
                    #end of if
                #end of if
            #end of if
        elif (choice == '2'):
            input_num = raw_input('please input the douban_id:')
            sql = 'select * from douban_info where douban_id = "%s"' % (input_num)
            result_num = cursor.execute(sql)
            if (result_num == 0):
                print 'no such film!'
            else:
                result = cursor.fetchone()
                print_douban_info(result)
            #end of if
        elif (choice == '3'):
            film_name = raw_input('please input the film_name:')
            film_name_utf8 = film_name.decode('utf-8')
            sql = 'select * from douban_info where title = "%s"' % (film_name_utf8)
            result_num = cursor.execute(sql)
            if (result_num == 0):
                print 'no such film!'
            else:
                result = cursor.fetchone()
                print_douban_info(result)
            #end of if
        elif (choice == 'h'):
            choice = raw_input(help_info)
            continue
        elif (choice == 'q'):
            continue
        else:
            print 'incorrect input! tyr again!'
            choice = raw_input(help_info)
            continue
        #end of if

        choice = raw_input('yours choice: ')
    #end of while
