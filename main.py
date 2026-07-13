from flask import Flask, request, render_template_string
import sqlite3
import qrcode


app = Flask(__name__)


def create_database():
    conn = sqlite3.connect("elegxos_ypiresion.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prosopiko (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vathmos TEXT NOT NULL,
        onomateponymo TEXT NOT NULL,
        asm TEXT NOT NULL UNIQUE,
        tilefono TEXT NOT NULL,
        tilefono_syggeni TEXT NOT NULL,
        email TEXT NOT NULL,
        typos_oximatos TEXT,
        arithmos_kykloforias TEXT
    )
    """)

    conn.commit()
    conn.close()


form = """
<h2>ΕΓΓΡΑΦΗ ΠΡΟΣΩΠΙΚΟΥ</h2>

<form method="post">

Βαθμός:<br>
<input name="vathmos"><br><br>

Ονοματεπώνυμο:<br>
<input name="onomateponymo"><br><br>

ΑΣΜ:<br>
<input name="asm"><br><br>

Τηλέφωνο:<br>
<input name="tilefono"><br><br>

Τηλέφωνο Συγγενή:<br>
<input name="tilefono_syggeni"><br><br>

Email:<br>
<input name="email"><br><br>

Τύπος Οχήματος:<br>
<input name="typos_oximatos"><br><br>

Αριθμός Κυκλοφορίας:<br>
<input name="arithmos_kykloforias"><br><br>

<button type="submit">ΑΠΟΘΗΚΕΥΣΗ</button>

</form>
"""


@app.route("/", methods=["GET", "POST"])
def eggrafi():

    if request.method == "POST":

        data = (
            request.form["vathmos"],
            request.form["onomateponymo"],
            request.form["asm"],
            request.form["tilefono"],
            request.form["tilefono_syggeni"],
            request.form["email"],
            request.form["typos_oximatos"],
            request.form["arithmos_kykloforias"]
        )

        conn = sqlite3.connect("elegxos_ypiresion.db")
        cursor = conn.cursor()

        try:
            cursor.execute("""
            INSERT INTO prosopiko
            (
            vathmos,
            onomateponymo,
            asm,
            tilefono,
            tilefono_syggeni,
            email,
            typos_oximatos,
            arithmos_kykloforias
            )
            VALUES (?,?,?,?,?,?,?,?)
            """, data)

            conn.commit()

            return "Η εγγραφή ολοκληρώθηκε"

        except:
            return "Υπάρχει ήδη αυτό το ΑΣΜ"

        finally:
            conn.close()


    return render_template_string(form)



create_database()


if __name__ == "__main__":
    print("SERVER ΕΓΓΡΑΦΗΣ ΕΝΕΡΓΟΣ")
    app.run(host="0.0.0.0", port=5000)