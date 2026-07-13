from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)


page = """
<h2>ADMIN - ΣΤΟΙΧΕΙΑ ΠΡΟΣΩΠΙΚΟΥ</h2>

<form method="post">

{% for field,value in fields %}

{{field}}:<br>
<input name="{{field}}" value="{{value}}"><br><br>

{% endfor %}

<button>
ΑΠΟΘΗΚΕΥΣΗ
</button>

</form>
"""


@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):

    conn = sqlite3.connect(
        "elegxos_ypiresion.db"
    )

    cur = conn.cursor()


    if request.method == "POST":

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

        return "Η τροποποίηση αποθηκεύτηκε"


    cur.execute("""
    SELECT
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


    data = cur.fetchone()

    conn.close()


    names = [
        "katigoria",
        "dn",
        "arithmos_oplou",
        "thesi_oplovastou",
        "paron_apon",
        "dria",
        "omada",
        "paratiriseis"
    ]


    fields = zip(names,data)


    return render_template_string(
        page,
        fields=fields
    )


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5002
    )