import MySQLdb
import matplotlib.pyplot as plt
#import insert

db = MySQLdb.connect(host="localhost", user="root", passwd="harpic",
                     db="leading_trailing")
cursor = db.cursor()

teams_query = "select home_team, away_team \
    from matches \
    where 1=1 \
    and competition = 'World_Cup_Russia_2018';"
cursor.execute(teams_query)
countries = cursor.fetchall()
countries = [c[0] for c in countries] + [c[1] for c in countries]
countries = list(set(countries))

rounds_query = "select team, round_of_16 \
    from russia_stages;"
cursor.execute(rounds_query)
qualified = cursor.fetchall()
qualified = {q[0]:q[1] for q in qualified}
print(qualified)

points = []
leading_time = []

#insert.insert(cursor, db, 'Russia_Stages', **{'team': country,
#                                                'round_of_16': 0,
#                                                'quarter_final': 0,
#                                                'semi_final': 0,
#                                                'final': 0,
#                                                'winner': 0})

for country in countries:
    points_query = "select \
        if((max(s.home_score) >  max(s.away_score) and m.home_team = '%s') or (max(s.home_score) < max(s.away_score) and m.away_team = '%s'), 3, 0) + \
        if((max(s.home_score) = max(s.away_score)) and (m.home_team = '%s'  or m.away_team = '%s'), 1, 0) points \
        from scores s \
        join matches m on m.match_id = s.match_id \
        where 1=1 \
        and m.competition = 'World_Cup_Russia_2018' \
        and m.home_team = '%s' or m.away_team = '%s' \
        group by s.match_id;" % (country, country, country, country, country, country)

    cursor.execute(points_query)
    point = cursor.fetchall()
    point = sum([p[0] for p in point])
    points.append(point)

    lead_query = "select  \
        sum(if(((e.home_score > e.away_score and m.home_team = '%s') or (e.home_score < e.away_score and m.away_team = '%s')), 1, 0)) \
        from extended_scores e \
        join matches m on m.match_id = e.match_id;" % (country, country)

    cursor.execute(lead_query)
    lead_time = int(cursor.fetchall()[0][0])
    leading_time.append(lead_time)

plt.show()
