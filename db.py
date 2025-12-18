# db.py
import psycopg2
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# ==============================
# LOAD ENV
# ==============================
load_dotenv()

# ==============================
# DATABASE CONNECTION
# ==============================
def get_connection():
    return psycopg2.connect(
        host=os.getenv("PG_HOST", "localhost"),
        port=os.getenv("PG_PORT", "5432"),
        database=os.getenv("PG_DB", "CQMS"),
        user=os.getenv("PG_USER", "postgres"),
        password=os.getenv("PG_PASSWORD", "123"),
    )

# ==============================
# INITIALIZE DATABASE
# ==============================
def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Drop existing tables (clean start)
    cur.execute("DROP TABLE IF EXISTS ticket_comments CASCADE;")
    cur.execute("DROP TABLE IF EXISTS queries CASCADE;")
    cur.execute("DROP TABLE IF EXISTS users CASCADE;")

    # USERS TABLE
    cur.execute("""
        CREATE TABLE users (
            username VARCHAR(100) PRIMARY KEY,
            hashed_password TEXT NOT NULL,
            role VARCHAR(20) NOT NULL
        );
    """)

    # QUERIES TABLE
    cur.execute("""
        CREATE TABLE queries (
            query_id SERIAL PRIMARY KEY,
            username VARCHAR(100),
            mail_id VARCHAR(255),
            mobile_number VARCHAR(20),
            query_heading TEXT,
            query_description TEXT,
            priority VARCHAR(10),
            status VARCHAR(20),
            assigned_to VARCHAR(100),
            sla_hours INT,
            query_created_time TIMESTAMP,
            query_closed_time TIMESTAMP
        );
    """)

    # TICKET COMMENTS TABLE
    cur.execute("""
        CREATE TABLE ticket_comments (
            id SERIAL PRIMARY KEY,
            query_id INT REFERENCES queries(query_id),
            commented_by VARCHAR(100),
            comment TEXT,
            sentiment VARCHAR(20),
            commented_at TIMESTAMP
        );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Tables created successfully!")

# ==============================
# LOAD CSV INTO QUERIES
# ==============================
def load_csv_into_queries(csv_path):
    df = pd.read_csv(csv_path)

    # Replace NaN with None
    df = df.where(pd.notnull(df), None)

    # Convert datetime columns safely
    for col in ["query_created_time", "query_closed_time"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    conn = get_connection()
    cur = conn.cursor()

    insert_sql = """
        INSERT INTO queries (
            mail_id,
            mobile_number,
            query_heading,
            query_description,
            status,
            query_created_time,
            query_closed_time
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s);
    """

    for _, row in df.iterrows():
        created_time = row.get("query_created_time")
        closed_time = row.get("query_closed_time")

        # 🔑 FIX: NaT → None
        if pd.isna(created_time):
            created_time = None
        if pd.isna(closed_time):
            closed_time = None

        cur.execute(
            insert_sql,
            (
                row.get("mail_id"),
                row.get("mobile_number"),
                row.get("query_heading"),
                row.get("query_description"),
                row.get("status"),
                created_time,
                closed_time,
            ),
        )

    conn.commit()
    cur.close()
    conn.close()
    print("✅ CSV loaded successfully without any errors!")

# ==============================
# MAIN
# ==============================
if __name__ == "__main__":
    init_db()
    load_csv_into_queries(
        r"D:\Py_start\Python\project_SN\cqms_sholingan\new2\data\synthetic_client_queries.csv"
    )
