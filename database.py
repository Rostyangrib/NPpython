import mysql.connector
import json

DB_CONFIG = {
    'host': 'db',
    'user': 'root',
    'password': '123',
    'database': 'Films',
    'charset': 'utf8mb4'
}

def get_filtered_films(keyword, min_time, max_time):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM films WHERE 1=1"
    params = []

    if keyword:
        query += " AND title LIKE %s"
        params.append(f"%{keyword}%")
    if min_time:
        query += " AND JSON_UNQUOTE(JSON_EXTRACT(time, '$[0]')) >= %s"
        params.append(min_time)
    if max_time:
        query += " AND JSON_UNQUOTE(JSON_EXTRACT(time, '$[0]')) <= %s"
        params.append(max_time)

    cursor.execute(query, params)
    results = cursor.fetchall()
    #декод
    for film in results:
        film['description'] = json.loads(film['description'])
        film['time'] = json.loads(film['time'])

    cursor.close()
    conn.close()

    return results
