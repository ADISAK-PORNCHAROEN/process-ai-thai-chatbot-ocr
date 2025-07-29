import psycopg2

def getConnection():
    conn = psycopg2.connect(
        host="localhost",
        dbname="mydb",
        user="admin",
        password="simplePassword",
        port=5432
    )
    return conn

conn = getConnection()

cur = conn.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1024)
)            
""")
conn.commit()
cur.close()
conn.close()