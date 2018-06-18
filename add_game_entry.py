import bs4 as bs
import insert
import urllib3
import re
import create_leading


def create_match_record(match_id, tourn, db, cursor):
    url = 'http://www.football-lineups.com/match/%s' % match_id
    user_agent = {'user-agent': 'Mozilla/5.0 (Windows NT 6.3; rv:36.0)\
                  Gecko/20100101 Firefox/36.0'}
    http = urllib3.PoolManager(2, user_agent)
    response = http.request('GET', url)
    soup = bs.BeautifulSoup(response.data, 'lxml')

    date = soup.find_all('a', {'href': re.compile('^/date/[0-9]')})[0]['href']
    date = date.split('/')[-2]

    teams = soup.find_all('span', {'id': 'titequip'})
    teams = [t.text.strip() for t in teams]
    home_team = teams[0]
    away_team = teams[1]

    goal_times = soup.find_all('td', {'width': '30', 'align': 'middle'})
    goal_times = [int(gt.text[:-1]) for gt in goal_times]
    score = soup.find_all('td', {'width': '25', 'align': 'middle'})
    score = [s.text for s in score]

    # check for 0-0
    final = soup.find_all('font', {'size': '+2'})
    home_final = int(final[2].text.strip())
    away_final = int(final[4].text.strip())

    goals = [[goal_times[i], int(score[i][0]), int(score[i][-1])]
             for i in range(0, len(score))
             if score[i] != ' ' and score[i] != '\xa0\xa0\xa0']
    if home_final == 0 and away_final == 0:
        goals = [[0, 0, 0], [90, 0, 0]]

    if goals == []:
        raise ValueError("This match has not completed yet")

    # insert into the match the data of this match
    match_dict = {'match_id': match_id, 'home_team': home_team,
                  'away_team': away_team, 'competition': tourn, 'date': date}
    insert.insert(cursor, db, 'Matches', **match_dict)

    # dictionary to load in scores
    insert_dict = {'match_id': match_id}
    for entry in goals:
        insert_dict['minute'] = entry[0]
        insert_dict['home_score'] = entry[1]
        insert_dict['away_score'] = entry[2]
        # call insert function
        insert.insert(cursor, db, 'Scores', **insert_dict)
        create_leading.create_lead(cursor, db, match_id)
