import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def getConnection():
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
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