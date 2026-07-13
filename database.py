import sqlite3

conn = sqlite3.connect("elegxos_ypiresion.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS prosopiko (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    vathmos TEXT,
    onomateponymo TEXT,
    asm TEXT,
    tilefono TEXT,
    tilefono_syggeni TEXT,
    email TEXT,

    typos_oximatos TEXT,
    arithmos_kykloforias TEXT,

    katigoria TEXT,
    dn TEXT,
    arithmos_oplou TEXT,
    thesi_oplovastou TEXT,
    paron_apon TEXT,
    dria TEXT,
    omada TEXT,
    paratiriseis TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT,
    password TEXT,
    role TEXT
)
""")

cur.execute("""
SELECT COUNT(*)
FROM users
""")

if cur.fetchone()[0] == 0:

    cur.execute("""
    INSERT INTO users
    VALUES
    ('admin','1234','ADMIN')
    """)

conn.commit()
conn.close()

print("Η βάση δημιουργήθηκε")