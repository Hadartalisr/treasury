import mysql

cnx = mysql.connector.connect(user='Hadartal', password='Htal207992728',
                              host='127.0.0.1',
                              database='moneyHeist')


cnx.close()