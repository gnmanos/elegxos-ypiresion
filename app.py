from flask import Flask, request, render_template_string
import sqlite3
import os

app = Flask(__name__)


DATABASE = "elegxos_ypiresion.db"


def init_db():

    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS prosopiko (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        vathmos TEXT NOT NULL,
        onomateponymo TEXT NOT NULL,
        asm TEXT NOT NULL,
        tilefono TEXT NOT NULL,
        tilefono_syggeni TEXT NOT NULL,
        email TEXT NOT NULL,

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

    conn.commit()
    conn.close()



form = """

<h2>ΕΛΕΓΧΟΣ ΥΠΗΡΕΣΙΩΝ</h2>

<h3>Εγγραφή Προσωπικού</h3>

<form method="post">

Βαθμός *<br>
<input name="vathmos" required><br><br>


Ονοματεπώνυμο *<br>
<input name="onomateponymo" required><br><br>


ΑΣΜ *<br>
<input name="asm" required><br><br>


Τηλέφωνο *<br>
<input name="tilefono" required><br><br>


Τηλέφωνο Συγγενή *<br>
<input name="tilefono_syggeni" required><br><br>


Email *<br>
<input type="email" name="email" required><br><br>


Τύπος Οχήματος<br>
<input name="typos_oximatos"><br><br>


Αριθμός Κυκλοφορίας<br>
<input name="arithmos_kykloforias"><br><br>


<button type="submit">
ΑΠΟΘΗΚΕΥΣΗ
</button>

</form>

"""



@app.route("/", methods=["GET","POST"])
def register():


    if request.method == "POST":


        conn = sqlite3.connect(DATABASE)

        cur = conn.cursor()


        cur.execute("""
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

        """,

        (

        request.form["vathmos"],
        request.form["onomateponymo"],
        request.form["asm"],
        request.form["tilefono"],
        request.form["tilefono_syggeni"],
        request.form["email"],
        request.form["typos_oximatos"],
        request.form["arithmos_kykloforias"]

        ))


        conn.commit()
        conn.close()


        return """

        <h2>Η εγγραφή ολοκληρώθηκε</h2>

        <a href="/">
        Νέα εγγραφή
        </a>

        """



    return render_template_string(form)




if __name__ == "__main__":


    init_db()


    print("ONLINE ΕΓΓΡΑΦΗ ΕΝΕΡΓΗ")


    port = int(os.environ.get("PORT",5000))


    app.run(
        host="0.0.0.0",
        port=port
    )