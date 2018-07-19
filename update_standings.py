import dbconfig
import MySQLdb
import insert
import pandas as pd

db_dict = dbconfig.read_db_config()
db = MySQLdb.connect(host=db_dict['host'],
                     user=db_dict['user'],
                     passwd=db_dict['password'],
                     db=db_dict['database'])

comp = 'FA_Premier_League_2008-2009'
# query to get all teams from a particular competition
team_query = """
            select distinct(home_team)
            from matches
            where 1=1
            and competition = '%s';
            """

# query to get all matches from particular competition
match_query = """
            select match_id
            from matches
            where 1=1
            and competition = '%s';
            """

# query to fetch final scores for games in particular games
scores_query = """
            select k.home_score, k.away_score, o.home_team, o.away_team
            from (select m.match_id, max(m.minute) as OK
                    from scores m where 1=1 and m.match_id = %s) as t
            join scores k on k.match_id = t.match_id
            join matches o on o.match_id = k.match_id
            where 1=1
            and t.OK = k.minute;
            """

# determines time that the home team was leading for
lead_query = """
            select
            sum(if((e.home_score > e.away_score), 1, 0))
            from extended_scores e
            join matches m on m.match_id = e.match_id
            where 1=1
            and m.match_id = %s;
            """

# determines time home team was trailing for
trail_query = """
            select
            sum(if((e.home_score < e.away_score), 1, 0))
            from extended_scores e
            join matches m on m.match_id = e.match_id
            where 1=1
            and m.match_id = %s;
            """


def get_season_data(matches):
    cursor = db.cursor()
    # iterate through matches and collect scores
    for match in matches:
        # get the final score of the game
        cursor.execute(scores_query % match)
        data = cursor.fetchall()[-1]
        # assign data to variables
        home_goal, away_goal, home_team, away_team = data

        # increment games played
        standings[home_team]['gp'] += 1
        standings[away_team]['gp'] += 1

        # determine who won and assign points
        if home_goal > away_goal:
            standings[home_team]['pts'] += 3
        elif home_goal < away_goal:
            standings[away_team]['pts'] += 3
        elif home_goal == away_goal:
            standings[home_team]['pts'] += 1
            standings[away_team]['pts'] += 1

        # add goals scored, against, and goal difference
        standings[home_team]['gs'] += home_goal
        standings[home_team]['ga'] += away_goal
        standings[home_team]['gd'] += home_goal - away_goal
        standings[away_team]['gs'] += away_goal
        standings[away_team]['ga'] += home_goal
        standings[away_team]['gd'] += away_goal - home_goal

        # compute time spent leading [home]
        cursor.execute(lead_query % match)
        home_lead = int(cursor.fetchall()[0][0])
        standings[home_team]['lead_time'] += home_lead
        standings[away_team]['trail_time'] += home_lead

        # compute time spent trailing [home]
        cursor.execute(trail_query % match)
        home_trail = int(cursor.fetchall()[0][0])
        standings[away_team]['lead_time'] += home_trail
        standings[home_team]['trail_time'] += home_trail


def get_teams(comp):
    cursor = db.cursor()
    # get all the teams from this competition
    cursor.execute(team_query % comp)
    teams = cursor.fetchall()
    teams = [t[0] for t in teams]

    return teams


def get_matches(comp):
    cursor = db.cursor()
    # get all matches from this season
    cursor.execute(match_query % comp)
    matches = cursor.fetchall()
    matches = [m[0] for m in matches]

    return matches


def fetch_and_update(matches, teams, comp):
    cursor = db.cursor()
    # call function to fill in data for matches
    get_season_data(matches)

    # set up data frame object
    df = pd.DataFrame(standings)
    df = df.transpose()
    df.sort_values(by=['pts', 'gd', 'gs', 'ga'], ascending=[0, 0, 0, 1],
                inplace=True)
    df = df[['gp', 'pts', 'gs', 'ga', 'gd', 'lead_time', 'trail_time', 'competition']]
    df = df.reset_index()
    df['lead_time_p90'] = df['lead_time'] / df['gp']
    df['trail_time_p90'] = df['trail_time'] / df['gp']
    df.columns = ['team', 'gp', 'pts', 'gs', 'ga', 'gd', 'lead_time', 'trail_time',
                'competition', 'lead_time_p90', 'trail_time_p90']

    # convert df to dictionary and insert them into sql database
    data_dict = df.to_dict('records')
    for entry in data_dict:
        insert.insert(cursor, db, 'Competition_Summary', **entry)


teams = get_teams(comp)
# initialize dictionary for team data
standings = {t: {'gp': 0, 'pts': 0, 'gs': 0, 'ga': 0, 'gd': 0, 'lead_time': 0,
                 'trail_time': 0, 'competition': comp}
             for t in teams}

matches = get_matches(comp)

fetch_and_update(matches, teams, comp)
