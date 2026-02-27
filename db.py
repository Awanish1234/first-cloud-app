import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

conn = oracledb.connect(
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    dsn=os.getenv("DB_DSN")
)
print("✅ Connected to Oracle Cloud DB successfully!")
conn.close()