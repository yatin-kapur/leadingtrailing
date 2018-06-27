import MySQLdb
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.family'] = 'serif'
matplotlib.rcParams['font.serif'] = 'Palatino'

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

rounds_query = "select team, groups, round_of_16 \
    from russia_stages;"
cursor.execute(rounds_query)
qualified_data = cursor.fetchall()
qualified = {q[0]:q[2] for q in qualified_data}
groups = {q[0]:q[1] for q in qualified_data}

points = []
leading_time = []
trailing_time = []

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

    trail_query = "select  \
        sum(if(((e.home_score < e.away_score and m.home_team = '%s') or (e.home_score > e.away_score and m.away_team = '%s')), 1, 0)) \
        from extended_scores e \
        join matches m on m.match_id = e.match_id;" % (country, country)

    cursor.execute(trail_query)
    trail_time = int(cursor.fetchall()[0][0])
    trailing_time.append(trail_time)

df_qual = [qualified[c] for c in countries]
df_group = [groups[c] for c in countries]
df = pd.DataFrame({'country': countries,
                   'group': df_group,
                   'leading': leading_time,
                   'trailing': trailing_time,
                   'round_of_16': df_qual})

df.sort_values(by=['group', 'round_of_16', 'leading', 'trailing'], ascending=[True, False, False, True], inplace=True)
df.reset_index(inplace=True)
del df['index']

minus = [-x for x in df['trailing']]
group = 'Z'
for index, row in df.iterrows():
    if group != row['group']:
        plt.plot([index+3.5, index+3.5], [min(minus) + 20, max(df['leading'])], color='black', lw=0.3, alpha=0.8)
        group = row['group']
        plt.text(index+1.5, max(df['leading']) + 2, s=group)

    bottom = -row['trailing']
    alpha = 1 if row['round_of_16'] else 0.5
    plt.bar(index, row['trailing'], bottom=bottom, color='#ff5050', alpha=alpha)
    plt.bar(index, row['leading'], color='#29e869', alpha=alpha)


#alpha = {1: 1, 0: 0.3}
#plt.bar(list(range(0,32)), df['trailing'], bottom=minus, color='#ff5050')
#plt.bar(list(range(0,32)), df['leading'], color='#66ff66')
plt.plot([-0.5, -0.5], [min(minus)+20, max(df['leading'])], color='black', lw=0.3, alpha=0.8)
plt.xticks(list(range(0,32)), df['country'], rotation='vertical')
plt.ylabel('Minutes')
plt.title('Time Spent Leading & Trailing')

plt.show()
