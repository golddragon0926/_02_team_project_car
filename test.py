import pymysql
import sys
sys.path.append('.')
from config.db_config import DB_CONFIG

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()
cursor.execute("""
    SELECT CONCAT(YEAR(price_date), '-', LPAD(MONTH(price_date), 2, '0')) AS 월, 
           AVG(price) AS 평균유가 
    FROM oil_price 
    WHERE fuel_code = 'GAS' 
    GROUP BY YEAR(price_date), MONTH(price_date),
             CONCAT(YEAR(price_date), '-', LPAD(MONTH(price_date), 2, '0'))
    ORDER BY 월
""")
for row in cursor.fetchall():
    print(row)
conn.close()