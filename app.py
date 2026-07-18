from flask import Flask, request, session, redirect, render_template_string
import os
import psycopg2

app = Flask(__name__)

app.secret_key = "elegxos_ypiresion_secret"


DATABASE_URL = os.environ.get("DATABASE_URL")



def db():

    return psycopg2.connect(DATABASE_URL)




def init_db():

    conn = db()
    cur = conn.cursor()


    cur.execute("""
    CREATE TABLE IF NOT EXISTS prosopiko (

        id SERIAL PRIMARY KEY,

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

        id SERIAL PRIMARY KEY,

        username TEXT,
        password TEXT,
        role TEXT

    )
    """)



    cur.execute("""
    CREATE TABLE IF NOT EXISTS ypiresies (

        id SERIAL PRIMARY KEY,

        imerominia TEXT,

        prosopiko_id INTEGER,

        ypiresia TEXT,

        katastasi TEXT DEFAULT 'ΕΝΕΡΓΗ',

        FOREIGN KEY(prosopiko_id)
        REFERENCES prosopiko(id)

    )
    """)



    cur.execute(
        "SELECT COUNT(*) FROM users"
    )


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


        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)

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



@app.route("/admin", methods=["GET","POST"])
def admin_login():

    message = ""


    if request.method == "POST":


        conn = db()
        cur = conn.cursor()



        cur.execute("""

        SELECT role

        FROM users

        WHERE username=%s AND password=%s

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



    search=request.args.get("search","")



    conn=db()

    cur=conn.cursor()



    if search:


        cur.execute("""

        SELECT *

        FROM prosopiko

        WHERE onomateponymo ILIKE %s

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



    data=cur.fetchall()



    conn.close()



    return render_template_string(

        list_page,

        data=data,
        search=search

    )
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):


    if not session.get("admin"):

        return redirect("/admin")



    conn=db()

    cur=conn.cursor()



    if request.method=="POST":


        cur.execute("""

        UPDATE prosopiko SET


        vathmos=%s,
        onomateponymo=%s,
        asm=%s,
        tilefono=%s,
        tilefono_syggeni=%s,
        email=%s,

        typos_oximatos=%s,
        arithmos_kykloforias=%s,

        katigoria=%s,
        dn=%s,
        arithmos_oplou=%s,
        thesi_oplovastou=%s,
        paron_apon=%s,
        dria=%s,
        omada=%s,
        paratiriseis=%s


        WHERE id=%s


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

        "SELECT * FROM prosopiko WHERE id=%s",

        (id,)

    )


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

        "DELETE FROM prosopiko WHERE id=%s",

        (id,)

    )


    conn.commit()

    conn.close()



    return redirect("/prosopiko")







# =========================
# ΗΜΕΡΗΣΙΕΣ ΥΠΗΡΕΣΙΕΣ
# =========================


@app.route("/ypiresies")
def ypiresies():


    if not session.get("admin"):

        return redirect("/admin")



    conn=db()

    cur=conn.cursor()



    cur.execute("""

    SELECT

    y.id,
    y.imerominia,
    p.onomateponymo,
    y.ypiresia,
    y.katastasi


    FROM ypiresies y


    JOIN prosopiko p

    ON y.prosopiko_id=p.id


    ORDER BY y.id DESC


    """)



    data=cur.fetchall()



    conn.close()



    return """

    <h2>ΗΜΕΡΗΣΙΕΣ ΥΠΗΡΕΣΙΕΣ</h2>


    <table border="1">

    <tr>

    <th>ΗΜΕΡΟΜΗΝΙΑ</th>
    <th>ΠΡΟΣΩΠΙΚΟ</th>
    <th>ΥΠΗΡΕΣΙΑ</th>
    <th>ΚΑΤΑΣΤΑΣΗ</th>

    </tr>


    """ + "".join(

    f"""

    <tr>

    <td>{x[1]}</td>

    <td>{x[2]}</td>

    <td>{x[3]}</td>

    <td>{x[4]}</td>

    </tr>

    """

    for x in data

    ) + """

    </table>

    <br>

    <a href="/panel">Πίσω</a>

    """






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