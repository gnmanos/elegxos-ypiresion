import sqlite3

conn = sqlite3.connect("elegxos_ypiresion.db")
cur = conn.cursor()

fields = [
    ("katigoria","TEXT"),
    ("dn","TEXT"),
    ("arithmos_oplou","TEXT"),
    ("thesi_oplovastou","TEXT"),
    ("paron_apon","TEXT"),
    ("dria","TEXT"),
    ("omada","TEXT"),
    ("paratiriseis","TEXT")
]

for name,typ in fields:
    try:
        cur.execute(
            f"ALTER TABLE prosopiko ADD COLUMN {name} {typ}"
        )
    except:
        pass

conn.commit()
conn.close()

print("Η βάση ενημερώθηκε")