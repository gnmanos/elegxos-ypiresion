from flask import Flask, request, render_template_string
import sqlite3


app = Flask(__name__)


form = """
<h2>ΕΛΕΓΧΟΣ ΥΠΗΡΕΣΙΩΝ</h2>

<h3>Εγγραφή Προσωπικού</h3>

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

<button>
ΑΠΟΘΗΚΕΥΣΗ
</button>

</form>
"""


@app.route("/", methods=["GET","POST"])
def register():

    if request.method == "POST":

        conn = sqlite3.connect(
            "elegxos_ypiresion.db"
        )

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


        return "Η εγγραφή ολοκληρώθηκε"


    return render_template_string(form)



if __name__ == "__main__":

    print("ONLINE ΕΓΓΡΑΦΗ ΕΝΕΡΓΗ")

    app.run(
        host="0.0.0.0",
        port=5000
    )