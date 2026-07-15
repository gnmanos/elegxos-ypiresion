from flask import Flask, request, session, redirect, render_template_string
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "elegxos_ypiresion_secret"

DATABASE = "elegxos_ypiresion.db"


def db():
    return sqlite3.connect(DATABASE)



def init_db():

    conn = db()
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

        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT

    )
    """)



    cur.execute("""
    CREATE TABLE IF NOT EXISTS ypiresies (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        imerominia TEXT,

        prosopiko_id INTEGER,

        ypiresia TEXT,

        katastasi TEXT DEFAULT 'ΕΝΕΡΓΗ',

        FOREIGN KEY(prosopiko_id) REFERENCES prosopiko(id)

    )
    """)



    cur.execute("SELECT COUNT(*) FROM users")


    count = cur.fetchone()[0]



    if count == 0:


        cur.execute("""
        INSERT INTO users
        (username,password,role)

        VALUES

        ('admin','1234','ADMIN')

        """)



        conn.commit()

    conn.close()



YPESIES = [

"ΣΚΟΠΟΣ Κ.Π. 1",
"ΣΚΟΠΟΣ Κ.Π. 2",
"ΣΚΟΠΟΣ Κ.Π. 3",
"ΣΚΟΠΟΣ Κ.Π. 4",

"Β. ΣΚΟΠΟΣ Κ.Π. 1",
"Β. ΣΚΟΠΟΣ Κ.Π. 2",
"Β. ΣΚΟΠΟΣ Κ.Π. 3",
"Β. ΣΚΟΠΟΣ Κ.Π. 4",

"ΠΕΡΙΠΟΛΟ 1",
"ΠΕΡΙΠΟΛΟ 2",
"ΠΕΡΙΠΟΛΟ 3",
"ΠΕΡΙΠΟΛΟ 4",

"Β. ΠΕΡΙΠΟΛΟΥ 1",
"Β. ΠΕΡΙΠΟΛΟΥ 2",
"Β. ΠΕΡΙΠΟΛΟΥ 3",
"Β. ΠΕΡΙΠΟΛΟΥ 4",

"ΑΟΤ 1",
"ΑΟΤ 2",
"ΑΟΤ 3",
"ΑΟΤ 4",

"Β. ΑΟΤ 1",
"Β. ΑΟΤ 2",
"Β. ΑΟΤ 3",
"Β. ΑΟΤ 4",

"ΘΑΛΑΜΟΦΥΛΑΚΑΣ 1",
"ΘΑΛΑΜΟΦΥΛΑΚΑΣ 2",
"ΘΑΛΑΜΟΦΥΛΑΚΑΣ 3",

"ΑΜ",

"ΟΡΓΑΝΟ ΥΠΗΡΕΣΙΑΣ ΛΟΧΟΥ",

"ΛΑΝΤΖΑ ΕΣΤΙΑΤΟΡΙΟΥ 1",
"ΛΑΝΤΖΑ ΕΣΤΙΑΤΟΡΙΟΥ 2",
"ΛΑΝΤΖΑ ΕΣΤΙΑΤΟΡΙΟΥ 3",
"ΛΑΝΤΖΑ ΕΣΤΙΑΤΟΡΙΟΥ 4",
"ΛΑΝΤΖΑ ΕΣΤΙΑΤΟΡΙΟΥ 5",
"ΛΑΝΤΖΑ ΕΣΤΙΑΤΟΡΙΟΥ 6",

"ΛΑΝΤΖΑ ΜΑΓΕΙΡΙΩΝ 1",
"ΛΑΝΤΖΑ ΜΑΓΕΙΡΙΩΝ 2",
"ΛΑΝΤΖΑ ΜΑΓΕΙΡΙΩΝ 3",
"ΛΑΝΤΖΑ ΜΑΓΕΙΡΙΩΝ 4"

]



# =========================
# ΣΕΛΙΔΑ ΧΡΗΣΤΗ
# =========================


user_page = """

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


Τύπος Οχήματος (Προαιρετικό)<br>
<input name="typos_oximatos"><br><br>


Αριθμός Κυκλοφορίας (Προαιρετικό)<br>
<input name="arithmos_kykloforias"><br><br>


<button>
ΑΠΟΘΗΚΕΥΣΗ
</button>


</form>

"""



@app.route("/", methods=["GET","POST"])
def register():

    if request.method == "POST":


        if not request.form["vathmos"].strip() \
        or not request.form["onomateponymo"].strip() \
        or not request.form["asm"].strip() \
        or not request.form["tilefono"].strip() \
        or not request.form["tilefono_syggeni"].strip() \
        or not request.form["email"].strip():

            return """
            <h2>Σφάλμα</h2>
            <h3>Τα πεδία με * είναι υποχρεωτικά</h3>
            <a href="/">Επιστροφή</a>
            """


        conn = db()
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


    return render_template_string(user_page)



# =========================
# LOGIN ADMIN
# =========================


login_page = """

<h2>ADMIN LOGIN</h2>


<form method="post">


Username<br>
<input name="username"><br><br>


Password<br>
<input type="password" name="password"><br><br>


<button>
ΕΙΣΟΔΟΣ
</button>


</form>


<p>{{message}}</p>

"""



admin_page = """

<h2>ΠΙΝΑΚΑΣ ADMIN</h2>


<a href="/prosopiko">
ΠΡΟΣΩΠΙΚΟ
</a>


<br><br>


<a href="/ypiresies">
ΗΜΕΡΗΣΙΕΣ ΥΠΗΡΕΣΙΕΣ
</a>


<br><br>


<a href="/logout">
ΕΞΟΔΟΣ
</a>


"""
list_page = """

<h2>ΠΡΟΣΩΠΙΚΟ ADMIN</h2>
<form method="get" action="/prosopiko">

Αναζήτηση Ονοματεπωνύμου:

<input name="search" value="{{search}}">

<button>
ΑΝΑΖΗΤΗΣΗ
</button>

<a href="/prosopiko">
ΚΑΘΑΡΙΣΜΟΣ
</a>

</form>

<br>

<table border="1" cellpadding="5">


<tr>

<th>ID</th>
<th>ΒΑΘΜΟΣ</th>
<th>ΟΝΟΜΑΤΕΠΩΝΥΜΟ</th>
<th>ΑΣΜ</th>
<th>ΤΗΛΕΦΩΝΟ</th>
<th>ΤΗΛ. ΣΥΓΓΕΝΗ</th>
<th>EMAIL</th>

<th>ΟΧΗΜΑ</th>
<th>ΑΡΙΘΜΟΣ ΚΥΚΛΟΦΟΡΙΑΣ</th>

<th>ΚΑΤΗΓΟΡΙΑ</th>
<th>ΔΝ</th>
<th>ΑΡΙΘΜΟΣ ΟΠΛΟΥ</th>
<th>ΘΕΣΗ ΟΠΛΟΒΑΣΤΟΥ</th>
<th>ΠΑΡΩΝ/ΑΠΩΝ</th>
<th>ΔΡΙΑ</th>
<th>ΟΜΑΔΑ</th>
<th>ΠΑΡΑΤΗΡΗΣΕΙΣ</th>

<th>ΕΝΕΡΓΕΙΕΣ</th>

</tr>


{% for p in data %}

<tr>

<td>{{p[0]}}</td>
<td>{{p[1]}}</td>
<td>{{p[2]}}</td>
<td>{{p[3]}}</td>
<td>{{p[4]}}</td>
<td>{{p[5]}}</td>
<td>{{p[6]}}</td>

<td>{{p[7]}}</td>
<td>{{p[8]}}</td>

<td>{{p[9]}}</td>
<td>{{p[10]}}</td>
<td>{{p[11]}}</td>
<td>{{p[12]}}</td>
<td>{{p[13]}}</td>
<td>{{p[14]}}</td>
<td>{{p[15]}}</td>
<td>{{p[16]}}</td>


<td>

<a href="/edit/{{p[0]}}">
ΤΡΟΠΟΠΟΙΗΣΗ
</a>

<br><br>

<a href="/delete/{{p[0]}}"
onclick="return confirm('Διαγραφή εγγραφής;')">

ΔΙΑΓΡΑΦΗ

</a>

</td>


</tr>


{% endfor %}


</table>


<br>

<a href="/panel">
Πίσω
</a>


"""





# =========================
# ΠΛΗΡΗΣ ΕΠΕΞΕΡΓΑΣΙΑ ADMIN
# =========================


edit_page = """

<h2>ΠΛΗΡΗΣ ΤΡΟΠΟΠΟΙΗΣΗ ΠΡΟΣΩΠΙΚΟΥ</h2>


<form method="post">


Βαθμός<br>
<input name="vathmos" value="{{p[1] or ''}}"><br><br>


Ονοματεπώνυμο<br>
<input name="onomateponymo" value="{{p[2] or ''}}"><br><br>


ΑΣΜ<br>
<input name="asm" value="{{p[3] or ''}}"><br><br>


Τηλέφωνο<br>
<input name="tilefono" value="{{p[4] or ''}}"><br><br>


Τηλέφωνο Συγγενή<br>
<input name="tilefono_syggeni" value="{{p[5] or ''}}"><br><br>


Email<br>
<input name="email" value="{{p[6] or ''}}"><br><br>


Τύπος Οχήματος<br>
<input name="typos_oximatos" value="{{p[7] or ''}}"><br><br>


Αριθμός Κυκλοφορίας<br>
<input name="arithmos_kykloforias" value="{{p[8] or ''}}"><br><br>



Κατηγορία Ι<br>
<input name="katigoria" value="{{p[9] or ''}}"><br><br>


ΔΝ<br>
<input name="dn" value="{{p[10] or ''}}"><br><br>


Αριθμός Όπλου<br>
<input name="arithmos_oplou" value="{{p[11] or ''}}"><br><br>


Θέση Οπλοβαστού<br>
<input name="thesi_oplovastou" value="{{p[12] or ''}}"><br><br>


Παρών / Απών<br>
<input name="paron_apon" value="{{p[13] or ''}}"><br><br>


ΔΡΙΑ<br>
<input name="dria" value="{{p[14] or ''}}"><br><br>


Ομάδα<br>
<input name="omada" value="{{p[15] or ''}}"><br><br>


Παρατηρήσεις<br>
<input name="paratiriseis" value="{{p[16] or ''}}"><br><br>



<button>
ΑΠΟΘΗΚΕΥΣΗ
</button>


</form>


"""


# =========================
# ADMIN LOGIN
# =========================


@app.route("/admin", methods=["GET","POST"])
def admin_login():

    message = ""


    if request.method == "POST":


        conn = db()
        cur = conn.cursor()


        cur.execute("""

        SELECT role

        FROM users

        WHERE username=? AND password=?

        """,

        (

        request.form["username"],
        request.form["password"]

        ))


        user = cur.fetchone()


        conn.close()



        if user and user[0] == "ADMIN":

            session["admin"] = True

            return redirect("/panel")


        message = "Λάθος στοιχεία"



    return render_template_string(

        login_page,

        message=message

    )



@app.route("/panel")
def panel():

    if not session.get("admin"):

        return redirect("/admin")


    return render_template_string(admin_page)





@app.route("/prosopiko")
def prosopiko():

    if not session.get("admin"):

        return redirect("/admin")


    search = request.args.get("search","")


    conn = db()
    cur = conn.cursor()


    if search:

        cur.execute("""

        SELECT *

        FROM prosopiko

        WHERE onomateponymo LIKE ?

        ORDER BY id DESC

        """,

        ("%"+search+"%",)

        )

    else:

        cur.execute("""

        SELECT *

        FROM prosopiko

        ORDER BY id DESC

        """)


    data = cur.fetchall()


    conn.close()


    return render_template_string(

        list_page,

        data=data,
        search=search

    )


    cur.execute("""

    SELECT *

    FROM prosopiko

    ORDER BY id DESC

    """)


    data = cur.fetchall()


    conn.close()


    return render_template_string(

        list_page,

        data=data

    )
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):

    if not session.get("admin"):

        return redirect("/admin")


    conn = db()
    cur = conn.cursor()


    if request.method == "POST":


        cur.execute("""

        UPDATE prosopiko SET


        vathmos=?,
        onomateponymo=?,
        asm=?,
        tilefono=?,
        tilefono_syggeni=?,
        email=?,
        typos_oximatos=?,
        arithmos_kykloforias=?,

        katigoria=?,
        dn=?,
        arithmos_oplou=?,
        thesi_oplovastou=?,
        paron_apon=?,
        dria=?,
        omada=?,
        paratiriseis=?


        WHERE id=?


        """,

        (

        request.form["vathmos"],
        request.form["onomateponymo"],
        request.form["asm"],
        request.form["tilefono"],
        request.form["tilefono_syggeni"],
        request.form["email"],
        request.form["typos_oximatos"],
        request.form["arithmos_kykloforias"],

        request.form["katigoria"],
        request.form["dn"],
        request.form["arithmos_oplou"],
        request.form["thesi_oplovastou"],
        request.form["paron_apon"],
        request.form["dria"],
        request.form["omada"],
        request.form["paratiriseis"],

        id

        ))


        conn.commit()
        conn.close()


        return redirect("/prosopiko")



    cur.execute(

        "SELECT * FROM prosopiko WHERE id=?",

        (id,)

    )


    p = cur.fetchone()


    conn.close()


    return render_template_string(

        edit_page,

        p=p

    )





@app.route("/delete/<int:id>")
def delete(id):


    if not session.get("admin"):

        return redirect("/admin")


    conn = db()
    cur = conn.cursor()


    cur.execute(

        "DELETE FROM prosopiko WHERE id=?",

        (id,)

    )


    conn.commit()

    conn.close()


    return redirect("/prosopiko")





@app.route("/logout")
def logout():

    session.clear()

    return redirect("/admin")





if __name__ == "__main__":


    init_db()


    port = int(os.environ.get("PORT",5000))


    app.run(

        host="0.0.0.0",

        port=port

    )