from flask import Flask, request, session, redirect, render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = "elegxos_ypiresion_secret"


def db():
    return sqlite3.connect("elegxos_ypiresion.db")


login_page = """
<h2>ADMIN LOGIN</h2>

<form method="post">

Username:<br>
<input name="username"><br><br>

Password:<br>
<input type="password" name="password"><br><br>

<button>ΕΙΣΟΔΟΣ</button>

</form>

<p>{{message}}</p>
"""


menu_page = """
<h2>ΠΙΝΑΚΑΣ ADMIN</h2>

<a href="/prosopiko">ΠΡΟΣΩΠΙΚΟ</a>
<br><br>
<a href="/logout">ΕΞΟΔΟΣ</a>
"""


list_page = """
<h2>ΠΡΟΣΩΠΙΚΟ</h2>

<table border="1" cellpadding="5">

<tr>
<th>ID</th>
<th>Βαθμός</th>
<th>Ονοματεπώνυμο</th>
<th>ΑΣΜ</th>
<th>Τηλέφωνο</th>
<th>Επεξεργασία</th>
</tr>

{% for p in data %}

<tr>
<td>{{p[0]}}</td>
<td>{{p[1]}}</td>
<td>{{p[2]}}</td>
<td>{{p[3]}}</td>
<td>{{p[4]}}</td>

<td>
<a href="/edit/{{p[0]}}">
ΤΡΟΠΟΠΟΙΗΣΗ
</a>
</td>

</tr>

{% endfor %}

</table>

<br>

<a href="/admin">Πίσω</a>
"""


edit_page = """
<h2>ΤΡΟΠΟΠΟΙΗΣΗ ADMIN</h2>

<form method="post">

Κατηγορία Ι:
<input name="katigoria" value="{{p[1] or ''}}"><br><br>

ΔΝ:
<input name="dn" value="{{p[2] or ''}}"><br><br>

Αριθμός Όπλου:
<input name="arithmos_oplou" value="{{p[3] or ''}}"><br><br>

Θέση στον Οπλοβαστό:
<input name="thesi_oplovastou" value="{{p[4] or ''}}"><br><br>

Παρών/Απών:
<input name="paron_apon" value="{{p[5] or ''}}"><br><br>

ΔΡΙΑ:
<input name="dria" value="{{p[6] or ''}}"><br><br>

Ομάδα:
<input name="omada" value="{{p[7] or ''}}"><br><br>

Παρατηρήσεις:
<input name="paratiriseis" value="{{p[8] or ''}}"><br><br>


<button>
ΑΠΟΘΗΚΕΥΣΗ
</button>

</form>

<br>

<a href="/prosopiko">Πίσω</a>
"""


@app.route("/", methods=["GET","POST"])
def login():

    message=""

    if request.method=="POST":

        conn=db()
        cur=conn.cursor()

        cur.execute("""
        SELECT role
        FROM users
        WHERE username=? AND password=?
        """,
        (
        request.form["username"],
        request.form["password"]
        ))

        user=cur.fetchone()

        conn.close()

        if user and user[0]=="ADMIN":
            session["admin"]=True
            return redirect("/admin")

        message="Λάθος στοιχεία"


    return render_template_string(
        login_page,
        message=message
    )


@app.route("/admin")
def admin():

    if not session.get("admin"):
        return redirect("/")

    return render_template_string(menu_page)



@app.route("/prosopiko")
def prosopiko():

    if not session.get("admin"):
        return redirect("/")


    conn=db()
    cur=conn.cursor()

    cur.execute("""
    SELECT id,vathmos,onomateponymo,asm,tilefono
    FROM prosopiko
    """)

    data=cur.fetchall()

    conn.close()

    return render_template_string(
        list_page,
        data=data
    )



@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):

    if not session.get("admin"):
        return redirect("/")


    conn=db()
    cur=conn.cursor()


    if request.method=="POST":

        cur.execute("""
        UPDATE prosopiko SET

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
    SELECT
    id,
    katigoria,
    dn,
    arithmos_oplou,
    thesi_oplovastou,
    paron_apon,
    dria,
    omada,
    paratiriseis

    FROM prosopiko
    WHERE id=?
    """,(id,))

    p=cur.fetchone()

    conn.close()


    return render_template_string(
        edit_page,
        p=p
    )



@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")



if __name__=="__main__":

    print("ADMIN SERVER ΕΝΕΡΓΟΣ")

    app.run(
        host="0.0.0.0",
        port=5001
    )