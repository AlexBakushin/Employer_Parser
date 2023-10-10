import psycopg2


conn = psycopg2.connect(
    host='localhost',
    database='test',
    user='postgres',
    password='2202'
)
try:
    with conn:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO user_acount VALUES (%s, %s)", (6, "Len"))
            cur.execute('SELECT * FROM user_acount')

            rows = cur.fetchall()

            for row in rows:
                print(row)

finally:
    conn.close()
