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
    SELECT COUNT(*) FROM users
    """)

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



# =====================
# ΣΕΛΙΔΑ ΧΡΗΣΤΗ
# =====================


user_page = """

<h2>ΕΛΕΓΧΟΣ ΥΠΗΡΕΣΙΩΝ</h2>

<h3>Εγγραφή Προσωπικού</h3>


<form method="post">


Βαθμός<br>
<input name="vathmos"><br><br>


Ονοματεπώνυμο<br>
<input name="onomateponymo"><br><br>


ΑΣΜ<br>
<input name="asm"><br><br>


Τηλέφωνο<br>
<input name="tilefono"><br><br>


Τηλέφωνο Συγγενή<br>
<input name="tilefono_syggeni"><br><br>


Email<br>
<input name="email"><br><br>


Τύπος Οχήματος<br>
<input name="typos_oximatos"><br><br>


Αριθμός Κυκλοφορίας<br>
<input name="arithmos_kykloforias"><br><br>


<button>
ΑΠΟΘΗΚΕΥΣΗ
</button>


</form>

"""



@app.route("/", methods=["GET","POST"])
def register():


    if request.method=="POST":


        conn=db()
        cur=conn.cursor()


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


    return render_template_string(user_page)
# =====================
# ADMIN
# =====================


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


<a href="/logout">
ΕΞΟΔΟΣ
</a>

"""



list_page = """

<h2>ΠΡΟΣΩΠΙΚΟ</h2>

<table border="1" cellpadding="5">

<tr>

<th>ID</th>
<th>ΒΑΘΜΟΣ</th>
<th>ΟΝΟΜΑΤΕΠΩΝΥΜΟ</th>
<th>ΑΣΜ</th>
<th>ΤΗΛ</th>
<th>EMAIL</th>
<th>ΟΧΗΜΑ</th>
<th>ΑΡΙΘΜΟΣ</th>
<th>ΕΠΕΞΕΡΓΑΣΙΑ</th>

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


<td>

<a href="/edit/{{p[0]}}">
ΤΡΟΠΟΠΟΙΗΣΗ
</a>

<br>

<a href="/delete/{{p[0]}}">
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



edit_page = """

<h2>ΤΡΟΠΟΠΟΙΗΣΗ ΠΡΟΣΩΠΙΚΟΥ</h2>


<form method="post">


Βαθμός<br>
<input value="{{p[1]}}" disabled><br><br>


Ονοματεπώνυμο<br>
<input value="{{p[2]}}" disabled><br><br>


ΑΣΜ<br>
<input value="{{p[3]}}" disabled><br><br>


Τηλέφωνο<br>
<input value="{{p[4]}}" disabled><br><br>


Email<br>
<input value="{{p[5]}}" disabled><br><br>


Τύπος Οχήματος<br>
<input name="typos_oximatos" value="{{p[6] or ''}}"><br><br>


Αριθμός Κυκλοφορίας<br>
<input name="arithmos_kykloforias" value="{{p[7] or ''}}"><br><br>


Κατηγορία Ι<br>
<input name="katigoria" value="{{p[8] or ''}}"><br><br>


ΔΝ<br>
<input name="dn" value="{{p[9] or ''}}"><br><br>


Αριθμός Όπλου<br>
<input name="arithmos_oplou" value="{{p[10] or ''}}"><br><br>


Θέση Οπλοβαστού<br>
<input name="thesi_oplovastou" value="{{p[11] or ''}}"><br><br>


Παρών / Απών<br>
<input name="paron_apon" value="{{p[12] or ''}}"><br><br>


ΔΡΙΑ<br>
<input name="dria" value="{{p[13] or ''}}"><br><br>


Ομάδα<br>
<input name="omada" value="{{p[14] or ''}}"><br><br>


Παρατηρήσεις<br>
<input name="paratiriseis" value="{{p[15] or ''}}"><br><br>


<button>
ΑΠΟΘΗΚΕΥΣΗ
</button>


</form>


<br>

<a href="/prosopiko">
Πίσω
</a>

"""



@app.route("/admin", methods=["GET","POST"])
def admin_login():


    message=""


    if request.method=="POST":


        conn=db()
        cur=conn.cursor()


        cur.execute("""

        SELECT role FROM users

        WHERE username=? AND password=?

        """,

        (

        request.form["username"],
        request.form["password"]

        ))


        user=cur.fetchone()


        conn.close()



        if user:


            session["admin"]=True

            return redirect("/panel")



        message="Λάθος στοιχεία"



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



    conn=db()
    cur=conn.cursor()


    cur.execute("""

    SELECT

id,
vathmos,
onomateponymo,
asm,
tilefono,
email,
typos_oximatos,
arithmos_kykloforias

FROM prosopiko

ORDER BY id DESC

    """)


    data=cur.fetchall()


    conn.close()


    return render_template_string(
        list_page,
        data=data
    )





@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):


    conn=db()
    cur=conn.cursor()



    if request.method=="POST":


        cur.execute("""

       UPDATE prosopiko SET

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



    cur.execute("""

    SELECT *

    FROM prosopiko

    WHERE id=?

    """,(id,))


    p=cur.fetchone()


    conn.close()


    return render_template_string(
        edit_page,
        p=p
    )



@app.route("/delete/<int:id>")
def delete(id):

    if not session.get("admin"):
        return redirect("/admin")

    conn=db()
    cur=conn.cursor()

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




if __name__=="__main__":


    init_db()


    port=int(os.environ.get("PORT",5000))


    app.run(
        host="0.0.0.0",
        port=port
    )