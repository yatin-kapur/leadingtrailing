import MySQLdb
import pandas as pd

db = MySQLdb.connect(host="localhost", user="root", passwd="harpic",
                     db="leading_trailing")
cursor = db.cursor()

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
        home_lead = cursor.fetchall()[0][0]
        standings[home_team]['leading'] += home_lead
        standings[away_team]['trailing'] += home_lead

        # compute time spent trailing [home]
        cursor.execute(trail_query % match)
        home_trail = cursor.fetchall()[0][0]
        standings[away_team]['leading'] += home_trail
        standings[home_team]['trailing'] += home_trail


cursor.execute(team_query % 'FA_Premier_League_2017-2018')
teams = cursor.fetchall()
teams = [t[0] for t in teams]
standings = {t: {'gp': 0, 'pts': 0, 'gs': 0, 'ga': 0, 'gd': 0, 'leading': 0,
                 'trailing': 0} for t in teams}
cursor.execute(match_query % 'FA_Premier_League_2017-2018')
matches = cursor.fetchall()
matches = [m[0] for m in matches]
get_season_data(matches)

df = pd.DataFrame(standings)
df = df.transpose()
df.sort_values(by=['pts', 'gd', 'gs', 'ga'], ascending=[0, 0, 0, 1],
               inplace=True)
df = df[['gp', 'pts', 'gs', 'ga', 'gd', 'leading', 'trailing']]
print(df)
