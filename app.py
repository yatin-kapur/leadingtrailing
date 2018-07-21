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

    return render_template('index.html', comps=comps)


@app.route('/update_standings', methods=['POST'])
def update_standings():
    if request.method == 'POST':
        competition = 'FA_Premier_League_' + request.form['comp']
        print(competition)
        query = """
                select team, pts, gp, gs, ga, gd, lead_time_p90, trail_time_p90
                from competition_summary
                where 1=1
                and competition = '%s'
                order by pts desc;
                """ % competition
        cursor = db.cursor()
        cursor.execute(query)
        standings = cursor.fetchall()

        return json.dumps({'data': standings})


if __name__ == '__main__':
    app.run(debug=True)
