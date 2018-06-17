import MySQLdb
db = MySQLdb.connect(host="localhost",
                     user="root",
                     passwd="harpic",
                     db="leading_trailing")
cursor = db.cursor()

def insert(table_name, **kwargs):
    template = "replace into %s (%s) values (%s);"
    column_names = []
    values = []
    for k, v in kwargs.items():
        column_names.append(k)
        values.append(v)

    column_string = ""
    for n in column_names:
        column_string += n + ","
    column_string = column_string[:-1]

    value_string = ""
    for v in values:
        if(v == None):
            value = "NULL"
        elif type(v) is int:
            value = str(v)
        elif type(v) is float:
            value = str(v)
        else:
            try:
                value = "'" + str(v) + "'"
            except:
                value = "'" + str(v.encode('utf-8')) + "'"
        value_string += value + ","
    value_string = value_string[:-1]
    sql_insert = template % (table_name, column_string, value_string)
    try:
        cursor.execute(sql_insert)
        db.commit()
    except:
        print("ERROR", sql_insert)
