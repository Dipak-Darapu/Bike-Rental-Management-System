"""Database initialization script to create tables and load sample data."""
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

host = os.getenv("DB_HOST", "localhost")
port = int(os.getenv("DB_PORT", "3306"))
user = os.getenv("DB_USER", "root")
password = os.getenv("DB_PASSWORD", "")
database = os.getenv("DB_NAME", "bike_rental")

def init():
    try:
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
        )
        cursor = conn.cursor()
        print("Connected to MySQL server successfully!")

        with open("sql/schema.sql", "r", encoding="utf-8") as f:
            schema_sql = f.read()
        for statement in schema_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt)
        print("Schema applied successfully!")

        cursor.execute(f"USE {database}")
        cursor.execute("SELECT COUNT(*) FROM bikes")
        count = cursor.fetchone()[0]
        if count == 0:
            with open("sql/sample_data.sql", "r", encoding="utf-8") as f:
                sample_sql = f.read()
            for statement in sample_sql.split(";"):
                stmt = statement.strip()
                if stmt:
                    cursor.execute(stmt)
            conn.commit()
            print("Sample data inserted successfully!")
        else:
            print(f"Database already contains {count} bikes.")

        cursor.close()
        conn.close()
        print("Database initialization complete!")
        return True
    except Exception as e:
        print(f"MySQL Error: {e}")
        return False

if __name__ == "__main__":
    init()
