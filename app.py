from flask import Flask, request, render_template_string
import sqlite3

app = Flask(__name__)

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


@app.route("/", methods=["GET", "POST"])
def register():

    if request.method == "POST":

       conn = sqlite3.connect("/tmp/elegxos_ypiresion.db")
        cur = conn.cursor()

        try:

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

            return """
            <h2>Η εγγραφή ολοκληρώθηκε</h2>
            <a href="/">Νέα εγγραφή</a>
            """

        except Exception as e:

            return f"""
            <h2>Σφάλμα</h2>
            <p>{e}</p>
            <a href="/">Επιστροφή</a>
            """

        finally:

            conn.close()

    return render_template_string(form)


if __name__ == "__main__":

    print("ONLINE ΕΓΓΡΑΦΗ ΕΝΕΡΓΗ")

    app.run(
        host="0.0.0.0",
        port=5000
    )