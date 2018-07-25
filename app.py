from flask import Flask, render_template, request
import json
import MySQLdb
import dbconfig

app = Flask(__name__)
db_dict = dbconfig.read_db_config()
db = MySQLdb.connect(host=db_dict['host'],
                     user=db_dict['user'],
                     passwd=db_dict['password'],
                     db=db_dict['database'])

@app.route('/')
def start_app():
    cursor = db.cursor()
    # get the years of the competitions loaded into this
    comps_query = """
                select *
                from competitions
                where 1=1
                and competition like '%-%'
                order by competition desc;
                """
    cursor.execute(comps_query)
    comps = cursor.fetchall()
    comps = [c[0].split('_')[-1] for c in comps]

    return render_template('home.html', comps=comps)


@app.route('/update_standings', methods=['POST'])
def update_standings():
    # get the competition data for requested season
    if request.method == 'POST':
        competition = 'FA_Premier_League_' + request.form['comp']
        query = """
                select team, pts, gp, gs, ga, gd, lead_time_p90, trail_time_p90
                from competition_summary
                where 1=1
                and competition = '%s'
                order by pts desc, gd desc;
                """ % competition
        cursor = db.cursor()
        cursor.execute(query)
        standings = cursor.fetchall()
        # organize standings into dictionaries
        standings = [{'team': d[0],
                      'pts': d[1],
                      'gp': d[2],
                      'gs': d[3],
                      'ga': d[4],
                      'gd': d[5],
                      'lead_time_p90': d[6],
                      'trail_time_p90': d[7]} for d in standings]

        return json.dumps({'data': standings})


def return_scores(team, matches, cursor):
    match_id = '(' + str(matches[0])
    for m in matches[1:]:
        match_id += ',' + str(m)

    match_id = match_id + ')'
    # get all matches
    query = """
            select match_id, home_score, away_score
            from scores
            where 1=1
            and match_id in %s
            order by minute desc;
            """ % (match_id)
    cursor.execute(query)
    scores = cursor.fetchall()
    return_scores = [{m: []} for m in matches]

    for i in range(0, 38):
        return_scores[i][matches[i]] = [[s[1], s[2]] for s in scores
                                         if s[0] == matches[i]][0]

    return return_scores


def return_extended_scores(team, matches, cursor):
    match_id = '(' + str(matches[0])
    for m in matches[1:]:
        match_id += ',' + str(m)

    match_id = match_id + ')'
    # get all the scores for one game
    query = """
            select m.match_id, s.minute,
            if((s.home_score > s.away_score and m.home_team = '%s') or (s.home_score < s.away_score and m.away_team = '%s'), 1, 0) as 'win',
            if((s.home_score = s.away_score), 2, 0) as 'draw',
            if((s.home_score < s.away_score and m.home_team = '%s') or (s.home_score > s.away_score and m.away_team = '%s'), 3, 0) as 'loss'
            from extended_scores s
            join matches m on m.match_id = s.match_id
            where 1=1
            and m.match_id in %s;
            """ % (team, team, team, team, match_id)
    cursor.execute(query)
    scores = cursor.fetchall()
    return_scores = [{m: []} for m in matches]

    for i in range(0, 38):
        return_scores[i][matches[i]] = ([[d[1], d[2]+d[3]+d[4]]
                                         for d in scores if d[0] == matches[i]])

    return return_scores


@app.route('/<string:team>/<string:comp>')
def get_team_profile(team, comp):
    # return team name that is without _s
    team = ' '.join(team.split('_'))
    comp = 'FA_Premier_League_' + comp
    # all matches for this team
    matches_query = """
                select match_id, home_team, away_team
                from matches
                where 1=1
                and competition = '%s'
                and (home_team = '%s' or away_team = '%s')
                order by date desc;
                """ % (comp, team, team)
    cursor = db.cursor()
    cursor.execute(matches_query)
    matches = cursor.fetchall()
    # reshaping data
    matches = [[m[0], m[1], m[2]] for m in matches]
    # getting the match ids
    match_ids = [m[0] for m in matches]
    team_list = [{'home': m[1], 'away': m[2]} for m in matches]
    extended_scores = return_extended_scores(team, match_ids, cursor)
    scores = return_scores(team, match_ids, cursor)

    return render_template('team.html', team=team, comp=comp, scores=scores,
                           extended_scores=extended_scores, team_list=team_list)


if __name__ == '__main__':
    app.run(debug=True)
