import MySQLdb
import bs4 as bs
import sys
import urllib3
import add_game_entry
import insert

db = MySQLdb.connect(host="localhost",
					 user="root",
					 passwd="mysqlpass",
					 db="leading_trailing")
cursor = db.cursor()


def update_games(tourn):
	url = 'http://www.football-lineups.com/tourn/%s' % tourn
	user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'}
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
				add_game_entry.create_match_record(match)
				entry = {'match_id': match, 'competition': tourn}
				insert.insert('Matches', **entry)
			except:
				print("Unexpected error:", sys.exc_info()[0])
				print(match)
				break

	db.commit()

update_games('World_Cup_Russia_2018')
