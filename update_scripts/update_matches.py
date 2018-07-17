import MySQLdb
import bs4 as bs
import urllib3
import add_game_entry

db = MySQLdb.connect(host="localhost", user="root", passwd="harpic",
                     db="leading_trailing")
cursor = db.cursor()


def update_games(tourn):
    url = 'http://www.football-lineups.com/tourn/%s' % tourn
    user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0)\
                  Gecko/20100101 Firefox/36.0'}
    http = urllib3.PoolManager(2, user_agent)
    response = http.request('GET', url)
    soup = bs.BeautifulSoup(response.data, 'lxml')

    links = soup.find('article').find('td', 'TDmain')
    links = links.findAll('a')

    match_ids = []
    for link in links:
        if link['href'][:7] == '/match/':
            match_ids.append(int(link['href'][7:-1]))

    cursor.execute("select * from Matches;")
    current = cursor.fetchall()
    current = [d[0] for d in current]

    for match in match_ids:
        if match not in current:
            try:
                add_game_entry.create_match_record(match, tourn, db, cursor)
            except Exception as e:
                print(match)
                print('ERROR: '+ str(e))
                if 'MATCHERROR' in str(e):
                    continue
                else:
                    break


cursor.execute("select * from Competitions;")
competitions = cursor.fetchall()
competitions = [c[0] for c in competitions]

for c in competitions:
    update_games(c)
