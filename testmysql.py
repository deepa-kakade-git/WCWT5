import pymysql

# MySQL Configuration
mysql_host = 'localhost'
mysql_user = 'wcwt5'
mysql_password = 'Tax1234!'
mysql_db = 'wcwt5db'

def connect_db():
    return pymysql.connect(host=mysql_host, user=mysql_user, password=mysql_password, db=mysql_db)


db = connect_db()
cursor = db.cursor()
cursor.execute("SELECT * FROM wcwt5_timesheetentrycode_lov")
print(type(cursor))

row=cursor.fetchone()
while row:
 print(row)
 row=cursor.fetchone()
 

db.close()