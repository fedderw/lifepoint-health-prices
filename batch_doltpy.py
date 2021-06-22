from doltpy.cli import Dolt
import pandas as pd
import mysql.connector

repo = Dolt("D:\dolthub-hospital\hospital-price-transparency-v2")
repo.sql_server()

connection = mysql.connector.connect(
    user="root", host="127.0.0.1", port=3306, database="hospital-price-transparency-v2"
)
cursor = connection.cursor(buffered=True)

# Need to turn autocommit on because mysql.connector turns it off by default
cursor.execute("SET @@autocommit = 1")
cursor