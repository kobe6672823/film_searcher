import urllib
import urllib2
from BeautifulSoup import BeautifulSoup

def get_imdb_page(): 
    "get the top 250 page from http://www.imdb.com/chart/top, and return the page"

    url = 'http://www.imdb.com/chart/top'
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    values = {'name' : 'Michael Foord',
              'location' : 'Northampton',
	          'language' : 'Python' }
    headers = { 'User-Agent' : user_agent }
    data = urllib.urlencode(values)
    req = urllib2.Request(url, data, headers)
    response = urllib2.urlopen(req)
    imdb_page = response.read()
    print "succeed in fetching the url:%s" % (url)
    return imdb_page
#end of def

def resolve_imdb_page(imdb_page):
    "get all tables from the imdb_page"

    parser = BeautifulSoup(imdb_page)
    tables = parser.findAll('table')
    return tables
#end of def

def get_ranklist():
    "get ranklist from imdb_page"

    page = get_imdb_page()
    tables = resolve_imdb_page(page)

    for table in tables:
        if table.text.find('Rating') != -1:  #only the table containing the ranklist has the keyword: Rating
            rank_list_table = table
            break
        #end of if
    #end of for
    lines = rank_list_table.findAll('tr')   #all the lines in the table
    del lines[0]    #delete the first line which only contains the words: Rank   Rating  Title   Votes

    ranklist = []
    for line in lines:
        tds = line.findAll('td')
        rank = int(float(tds[0].contents[0].contents[0].text.encode()))
        rating = float(tds[1].contents[0].text.encode())
        title = tds[2].contents[0].contents[0].text.encode()
        votes = tds[3].contents[0].text.encode()
        imdb_num = tds[2].contents[0].contents[0]['href'].split('/')[2].encode()
        ranklist_itme = [rank, rating, title, votes, imdb_num]
        ranklist.append(ranklist_itme)
    #end of for
    print "succeed in getting the ranklist"
    return ranklist
#end of def
 
