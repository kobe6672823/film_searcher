import MySQLdb

def store_ranklist(list):
    "store the ranklist into mysql"

    conn=MySQLdb.connect(host="localhost",user="root",passwd="",db="film_searcher_db",charset="utf8")
    cursor = conn.cursor()
    
    for item in list:
        sql = "insert into imdb_info(imdb_num, rank, rating, title, votes) values(%s,%s,%s,%s,%s)"
        param = (item[4], item[0], item[1], item[2], item[3])
        cursor.execute(sql, param)
    #end of for

    print "succeed in storing the ranklist"
