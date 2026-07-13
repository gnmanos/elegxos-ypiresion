import sqlite3


def create_database():

    conn = sqlite3.connect("elegxos_ypiresion.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # Δημιουργία αρχικού ADMIN
    cursor.execute("""
    INSERT OR IGNORE INTO users
    (username, password, role)
    VALUES (?, ?, ?)
    """,
    (
        "admin",
        "1234",
        "ADMIN"
    ))

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
    print("Η βάση ενημερώθηκε")