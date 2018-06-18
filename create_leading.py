import insert


def create_lead(cursor, db, match_id):
    cursor.execute("select minute, home_score, away_score \
                from scores where match_id = %s \
                order by minute;" % match_id)
    score_data = cursor.fetchall()

    insert_dict = {'match_id': match_id}
    for i in range(-1, len(score_data)):
        if i == -1:
            start = 0
            end = score_data[i+1][0]
            hg = 0
            ag = 0
        elif score_data[i] is score_data[-1]:
            start = score_data[i][0]
            end = 91 if score_data[i][0] < 90 else score_data[i][0] + 2
            hg = score_data[i][1]
            ag = score_data[i][2]
        else:
            start = score_data[i][0]
            end = score_data[i+1][0]
            hg = score_data[i][1]
            ag = score_data[i][2]

        for time in range(start, end):
            insert_dict['minute'] = time
            insert_dict['home_score'] = hg
            insert_dict['away_score'] = ag
            insert.insert(cursor, db, 'extended_scores', **insert_dict)
