import streamlit as st
import pandas as pd
import qrcode
from io import BytesIO
from datetime import datetime
import sqlite3
import os
import json

# PDF
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import Image

# =========================
# ΡΥΘΜΙΣΗ ΣΕΛΙΔΑΣ
# =========================

st.set_page_config(
    layout="wide",
    page_title="Σύστημα Διαχείρισης Προσωπικού & Υπηρεσιών",
    page_icon="🪖"
)


# =========================
# DATABASE
# =========================

DB_NAME = "database.db"


def init_database():

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS personnel (
        asm TEXT PRIMARY KEY,
        data TEXT NOT NULL
    )
    """)


    cur.execute("""
    CREATE TABLE IF NOT EXISTS duties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        asm TEXT NOT NULL,
        duty TEXT NOT NULL,
        UNIQUE(date, asm)
    )
    """)

    try:
        cur.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_duty
            ON duties(date, asm)
            """
        )
    except:
        pass

    cur.execute("""
    CREATE TABLE IF NOT EXISTS weapons (
        asm TEXT PRIMARY KEY,
        weapon_type TEXT,
        presence TEXT,
        absent_reason TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS special_status_types (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        short_name TEXT,
        stay_inside INTEGER DEFAULT 0
    )
    """)

    try:
        cur.execute(
            "ALTER TABLE special_status_types ADD COLUMN stay_inside INTEGER DEFAULT 0"
        )
    except sqlite3.OperationalError:
        pass

    cur.executemany(
        """
        INSERT OR IGNORE INTO special_status_types
        (
            name,
            short_name
        )
        VALUES (?,?)
        """,
        [
            ("ΑΔΕΙΑ", "ΑΔ"),
            ("ΑΝΑΡΡΩΤΙΚΗ ΑΔΕΙΑ", "ΑΝΑΡ"),
            ("ΣΤΕΠ", "ΣΤΕΠ"),
            ("ΝΟΣΟΚΟΜΕΙΟ", "ΝΟΣ"),
            ("ΕΛΕΥΘΕΡΟΣ ΥΠΗΡΕΣΙΑΣ", "ΕΥ"),
        ]
    )

    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        short_name TEXT,
        service_times TEXT,
        active INTEGER DEFAULT 1
    )
    """)

    try:
        cur.execute("""
            ALTER TABLE services
            ADD COLUMN service_times TEXT
        """)
    except:
        pass

    settings = [

        ("monada","625 Μ/Π ΤΠ"),
        ("loxos","1ος ΛΟΧΟΣ Ν/Σ"),
        ("alxias","ΤΑΤΣΗΣ ΧΑΡΙΛΑΟΣ"),
        ("diktis","ΜΑΝΟΣ ΙΩΑΝΝΗΣ"),
        ("aksos_oplismou",""),
        ("alxias_rank","ΑΛΧΙΑΣ"),
        ("diktis_rank","ΛΟΧΑΓΟΣ"),
        ("aksos_oplismou_rank","ΑΞΚΟΣ ΟΠΛΙΣΜΟΥ"),
        ("aksos_imatismou","ΑΞΚΟΣ ΙΜΑΤΙΣΜΟΥ"),
        ("aksos_imatismou_rank",""),
        ("ypxkos_kiniseos","ΥΠΞΚΟΣ ΚΙΝΗΣΕΩΣ"),
        ("ypxkos_kiniseos_rank",""),
        ("diktis_monadas",""),
        ("diktis_monadas_rank",""),
        ("emblem", "")

    ]  


    for key,value in settings:

        cur.execute(
            """
            INSERT OR IGNORE INTO settings
            (key,value)
            VALUES (?,?)
            """,
            (key,value)
        )

    conn.commit()
    conn.close()
def save_personnel(asm,data):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR REPLACE INTO personnel
        (asm,data)
        VALUES (?,?)
        """,
        (
            asm,
            json.dumps(
                data,
                ensure_ascii=False
            )
        )
    )

    conn.commit()
    conn.close()

def save_weapon_status(
    asm,
    weapon_type,
    presence,
    absent_reason
):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO weapons
        (
            asm,
            weapon_type,
            presence,
            absent_reason
        )
        VALUES (?,?,?,?)
        ON CONFLICT(asm) DO UPDATE SET
            weapon_type=excluded.weapon_type,
            presence=excluded.presence,
            absent_reason=excluded.absent_reason
        """,
        (
            asm,
            weapon_type,
            presence,
            absent_reason
        )
    )

    conn.commit()
    conn.close()

def get_weapon_status(asm):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT weapon_type, presence, absent_reason
        FROM weapons
        WHERE asm=?
        """,
        (asm,)
    )

    row = cur.fetchone()

    conn.close()

    if row:
        return {
            "weapon_type": row[0],
            "presence": row[1],
            "absent_reason": row[2]
        }

    return {
        "weapon_type": "G3A3",
        "presence": "ΠΑΡΟΝ",
        "absent_reason": ""
    }

def load_personnel():

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "SELECT asm,data FROM personnel"
    )

    rows = cur.fetchall()

    conn.close()

    result={}

    for asm,data in rows:

        result[asm]=json.loads(data)


    return result



def load_duties():

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "SELECT date,asm,duty FROM duties"
    )

    rows = cur.fetchall()

    conn.close()


    duties = {}

    for date, asm, duty in rows:

        if date not in duties:
            duties[date] = {}

        duties[date][asm] = duty


    return duties

def load_special_statuses():

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            name,
            short_name
        FROM special_status_types
        ORDER BY name
    """)

    rows = cur.fetchall()

    conn.close()

    return {
        name: short_name
        for name, short_name in rows
    }

def get_services():

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT name
        FROM services
        WHERE active=1
        ORDER BY id
        """
    )

    services = [
        row[0]
        for row in cur.fetchall()
    ]

    conn.close()

    return services

def add_service(
    name,
    short_name,
    service_times
):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO services
        (
            name,
            short_name,
            service_times
        )
        VALUES (?,?,?)
        """,
        (
            name,
            short_name,
            service_times
        )
    )

    conn.commit()
    conn.close()

def save_duty(date, asm, duty):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO duties
        (date, asm, duty)
        VALUES (?,?,?)
        ON CONFLICT(date,asm)
        DO UPDATE SET
            duty=excluded.duty
        """,
        (
            date,
            asm,
            duty
        )
    )

    conn.commit()
    conn.close()

def insert_default_services():

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()


    cur.execute(
        "SELECT COUNT(*) FROM services"
    )

    count = cur.fetchone()[0]


    if count == 0:

        for service in POSSIBLE_DUTIES + SPECIAL_STATUSES:

            cur.execute(
                """
                INSERT INTO services
                (
                    name,
                    short_name
                )
                VALUES (?,?)
                """,
                (
                    service,
                    DUTY_SHORT.get(service,"")
                )
            )


    conn.commit()
    conn.close()

def load_services():

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id,name,short_name,service_times
        FROM services
        WHERE active=1
        ORDER BY id
        """
    )

    rows = cur.fetchall()

    conn.close()

    return rows

def update_service(
    service_id,
    name,
    short_name,
    service_times
):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE services
        SET name=?,
            short_name=?,
            service_times=?
        WHERE id=?
        """,
        (
            name,
            short_name,
            service_times,
            service_id
        )
    )

    conn.commit()
    conn.close()


def delete_service(service_id):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        UPDATE services
        SET active=0
        WHERE id=?
        """,
        (service_id,)
    )

    conn.commit()
    conn.close()    

def delete_duty(date_key, asm):

    conn = sqlite3.connect(DB_NAME)

    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM duties
        WHERE date=? AND asm=?
        """,
        (
            date_key,
            asm
        )
    )

    conn.commit()

    conn.close()   

# =========================
# SESSION STATE
# =========================


if "personnel" not in st.session_state:

    st.session_state.personnel = load_personnel()



if "duties" not in st.session_state or st.session_state.duties is None:
    st.session_state.duties = load_duties()


if "special_statuses" not in st.session_state:
    st.session_state.special_statuses = {}    



if "edit_asm" not in st.session_state:

    st.session_state.edit_asm=None



# =========================
# ΥΠΗΡΕΣΙΕΣ
# =========================


POSSIBLE_DUTIES=[

"ΚΕΝΤΡΙΚΗ ΠΥΛΗ Νο1",
"ΒΟΗΘΟΣ ΚΕΝΤΡΙΚΗΣ ΠΥΛΗΣ Νο1",
"ΚΕΝΤΡΙΚΗ ΠΥΛΗ Νο2",
"ΒΟΗΘΟΣ ΚΕΝΤΡΙΚΗΣ ΠΥΛΗΣ Νο2",
"ΚΕΝΤΡΙΚΗ ΠΥΛΗ Νο3",
"ΒΟΗΘΟΣ ΚΕΝΤΡΙΚΗΣ ΠΥΛΗΣ Νο3",
"ΚΕΝΤΡΙΚΗ ΠΥΛΗ Νο4",
"ΒΟΗΘΟΣ ΚΕΝΤΡΙΚΗΣ ΠΥΛΗΣ Νο4",

"ΠΕΡΙΠΟΛΟ Νο1",
"ΒΟΗΘΟΣ ΠΕΡΙΠΟΛΟΥ Νο1",
"ΠΕΡΙΠΟΛΟ Νο2",
"ΒΟΗΘΟΣ ΠΕΡΙΠΟΛΟΥ Νο2",
"ΠΕΡΙΠΟΛΟ Νο3",
"ΒΟΗΘΟΣ ΠΕΡΙΠΟΛΟΥ Νο3",
"ΠΕΡΙΠΟΛΟ Νο4",
"ΒΟΗΘΟΣ ΠΕΡΙΠΟΛΟΥ Νο4",

"ΑΟΤ Νο1",
"ΒΟΗΘΟΣ ΑΟΤ Νο1",
"ΑΟΤ Νο2",
"ΒΟΗΘΟΣ ΑΟΤ Νο2",
"ΑΟΤ Νο3",
"ΒΟΗΘΟΣ ΑΟΤ Νο3",
"ΑΟΤ Νο4",
"ΒΟΗΘΟΣ ΑΟΤ Νο4",

"ΘΑΛΑΜΟΦΥΛΑΚΑΣ Νο1",
"ΒΟΗΘΟΣ ΘΑΛΑΜΟΦΥΛΑΚΑ Νο1",
"ΘΑΛΑΜΟΦΥΛΑΚΑΣ Νο2",
"ΒΟΗΘΟΣ ΘΑΛΑΜΟΦΥΛΑΚΑ Νο2",
"ΘΑΛΑΜΟΦΥΛΑΚΑΣ Νο3",
"ΒΟΗΘΟΣ ΘΑΛΑΜΟΦΥΛΑΚΑ Νο3",

"ΛΑΝΤΖΑ 1 (Εστιατόρια)",
"ΛΑΝΤΖΑ 2 (Εστιατόρια)",
"ΛΑΝΤΖΑ 3 (Εστιατόρια)",

"ΛΑΝΤΖΑ 1 (Μαγειρεία)",
"ΛΑΝΤΖΑ 2 (Μαγειρεία)",
"ΛΑΝΤΖΑ 3 (Μαγειρεία)",
"ΛΑΝΤΖΑ 4 (Μαγειρεία)",

"ΑΜ",
"ΟΡΓΑΝΟ ΥΠΗΡΕΣΙΑΣ ΛΟΧΟΥ",

"ΗΣΑ1",
"ΗΣΑ2",
"ΗΣΑ3",

"ΥΠΑΡΧΙΦΥΛΑΚΑΣ"

]


SPECIAL_STATUSES=[

"ΤΙΜΩΡΗΜΕΝΟΣ",
"ΕΥ",
"ΑΔΕΙΑ",
"ΝΟΣΟΚΟΜΕΙΟ",
"ΣΤΕΠ",
"ΕΘΕΛΟΝΤΙΚΑ ΕΝΤΟΣ"

]
DUTY_SHORT = {

    "ΚΕΝΤΡΙΚΗ ΠΥΛΗ Νο1":"ΚΠ1",
    "ΚΕΝΤΡΙΚΗ ΠΥΛΗ Νο2":"ΚΠ2",
    "ΚΕΝΤΡΙΚΗ ΠΥΛΗ Νο3":"ΚΠ3",
    "ΚΕΝΤΡΙΚΗ ΠΥΛΗ Νο4":"ΚΠ4",

    "ΒΟΗΘΟΣ ΚΕΝΤΡΙΚΗΣ ΠΥΛΗΣ Νο1":"ΒΚΠ1",
    "ΒΟΗΘΟΣ ΚΕΝΤΡΙΚΗΣ ΠΥΛΗΣ Νο2":"ΒΚΠ2",
    "ΒΟΗΘΟΣ ΚΕΝΤΡΙΚΗΣ ΠΥΛΗΣ Νο3":"ΒΚΠ3",
    "ΒΟΗΘΟΣ ΚΕΝΤΡΙΚΗΣ ΠΥΛΗΣ Νο4":"ΒΚΠ4",

    "ΠΕΡΙΠΟΛΟ Νο1":"ΠΕΡ1",
    "ΠΕΡΙΠΟΛΟ Νο2":"ΠΕΡ2",
    "ΠΕΡΙΠΟΛΟ Νο3":"ΠΕΡ3",
    "ΠΕΡΙΠΟΛΟ Νο4":"ΠΕΡ4",

    "ΒΟΗΘΟΣ ΠΕΡΙΠΟΛΟΥ Νο1":"ΒΠΕΡ1",
    "ΒΟΗΘΟΣ ΠΕΡΙΠΟΛΟΥ Νο2":"ΒΠΕΡ2",
    "ΒΟΗΘΟΣ ΠΕΡΙΠΟΛΟΥ Νο3":"ΒΠΕΡ3",
    "ΒΟΗΘΟΣ ΠΕΡΙΠΟΛΟΥ Νο4":"ΒΠΕΡ4",

    "ΑΟΤ Νο1":"ΑΟΤ1",
    "ΑΟΤ Νο2":"ΑΟΤ2",
    "ΑΟΤ Νο3":"ΑΟΤ3",
    "ΑΟΤ Νο4":"ΑΟΤ4",

    "ΒΟΗΘΟΣ ΑΟΤ Νο1":"ΒΑΟΤ1",
    "ΒΟΗΘΟΣ ΑΟΤ Νο2":"ΒΑΟΤ2",
    "ΒΟΗΘΟΣ ΑΟΤ Νο3":"ΒΑΟΤ3",
    "ΒΟΗΘΟΣ ΑΟΤ Νο4":"ΒΑΟΤ4",

    "ΘΑΛΑΜΟΦΥΛΑΚΑΣ Νο1":"Θ1",
    "ΘΑΛΑΜΟΦΥΛΑΚΑΣ Νο2":"Θ2",
    "ΘΑΛΑΜΟΦΥΛΑΚΑΣ Νο3":"Θ3",

    "ΒΟΗΘΟΣ ΘΑΛΑΜΟΦΥΛΑΚΑ Νο1":"ΒΘ1",
    "ΒΟΗΘΟΣ ΘΑΛΑΜΟΦΥΛΑΚΑ Νο2":"ΒΘ2",
    "ΒΟΗΘΟΣ ΘΑΛΑΜΟΦΥΛΑΚΑ Νο3":"ΒΘ3",

    "ΑΜ":"ΑΜ",
    "ΟΡΓΑΝΟ ΥΠΗΡΕΣΙΑΣ ΛΟΧΟΥ":"ΟΡΓ",
    "ΥΠΑΡΧΙΦΥΛΑΚΑΣ":"ΥΠ",

    "ΗΣΑ1":"ΗΣΑ1",
    "ΗΣΑ2":"ΗΣΑ2",
    "ΗΣΑ3":"ΗΣΑ3",

    "ΛΑΝΤΖΑ 1 (Εστιατόρια)":"ΛΕ1",
    "ΛΑΝΤΖΑ 2 (Εστιατόρια)":"ΛΕ2",
    "ΛΑΝΤΖΑ 3 (Εστιατόρια)":"ΛΕ3",

    "ΛΑΝΤΖΑ 1 (Μαγειρεία)":"ΛΜ1",
    "ΛΑΝΤΖΑ 2 (Μαγειρεία)":"ΛΜ2",
    "ΛΑΝΤΖΑ 3 (Μαγειρεία)":"ΛΜ3",
    "ΛΑΝΤΖΑ 4 (Μαγειρεία)":"ΛΜ4",

    "ΑΔΕΙΑ":"ΑΔ",
    "ΕΥ":"ΕΥ",
    "ΝΟΣΟΚΟΜΕΙΟ":"ΝΟΣ",
    "ΤΙΜΩΡΗΜΕΝΟΣ":"ΤΙΜ",
    "ΣΤΕΠ":"ΣΤΕΠ",
    "ΕΘΕΛΟΝΤΙΚΑ ΕΝΤΟΣ":"ΕΘΕΛ"
}


COUNTABLE_DUTIES = set(POSSIBLE_DUTIES)

init_database()

insert_default_services()
# =========================
# PDF FONT
# =========================


def load_font():

    pdfmetrics.registerFont(
        TTFont(
            "Arial",
            "fonts/arial.ttf"
        )
    )

    pdfmetrics.registerFont(
        TTFont(
            "Arial-Bold",
            "fonts/arialbd.ttf"
        )
    )

    return "Arial"


PDF_FONT=load_font()


# =========================
# ΚΑΤΑΣΤΑΣΗ ΥΠΗΡΕΣΙΩΝ PDF
# =========================


def create_service_pdf(filename, report_date):


    conn=sqlite3.connect(DB_NAME)
    cur=conn.cursor()


    def setting(k):

        cur.execute(
            "SELECT value FROM settings WHERE key=?",
            (k,)
        )

        r=cur.fetchone()

        return r[0] if r else ""


    monada=setting("monada")
    loxos=setting("loxos")
    alxias=setting("alxias")
    diktis=setting("diktis")
    alxias_rank=setting("alxias_rank")
    diktis_rank=setting("diktis_rank")


    conn.close()



    pdf=SimpleDocTemplate(
    filename,
    pagesize=A4,
    rightMargin=10,
    leftMargin=10,
    topMargin=10,
    bottomMargin=10
)



    style=ParagraphStyle(
    "Arial",
    fontName=PDF_FONT,
    fontSize=12,
    leading=14
)


    title_style=ParagraphStyle(
    "title",
    fontName=PDF_FONT,
    alignment=TA_CENTER,
    fontSize=12,
    leading=14
)


    left=ParagraphStyle(
        "left",
        fontName=PDF_FONT,
        alignment=TA_LEFT,
        fontSize=12
    )


    right=ParagraphStyle(
        "right",
        fontName=PDF_FONT,
        alignment=TA_RIGHT,
        fontSize=12
    )



    elements=[]



    header=Table(
        [
            [
                Paragraph(monada,left),
                Paragraph(loxos,right)
            ]
        ],
        colWidths=[240,240]
    )


    header.setStyle(
        TableStyle(
            [
                ("VALIGN",(0,0),(-1,-1),"TOP"),
                ("LEFTPADDING",(0,0),(-1,-1),0),
                ("RIGHTPADDING",(0,0),(-1,-1),0),
                ("TOPPADDING",(0,0),(-1,-1),0),
                ("BOTTOMPADDING",(0,0),(-1,-1),0)
            ]
        )
    )


    elements.append(header)


    elements.append(
        Spacer(1,15)
    )


    elements.append(
        Paragraph(
            f"<b><u>ΚΑΤΑΣΤΑΣΗ ΥΠΗΡΕΣΙΩΝ ΤΗΣ {report_date.strftime('%d/%m/%Y')}</u></b>",
            title_style
        )
    )


    elements.append(
        Spacer(1,20)
    )



    duties_day=st.session_state.duties.get(
        str(report_date),
        {}
    )



    def person(service):

        for asm,duty in duties_day.items():

            if duty==service:

                info=st.session_state.personnel.get(
                    asm,
                    {}
                )

                return (
                    info.get("Βαθμός","")
                    +" "+
                    info.get("Ονοματεπώνυμο","")
                )

        return ""

    assigned_services = []

    services = load_services()

    for service in services:

        service_name = service[1]
        service_times = service[3]

        for asm, duty in duties_day.items():

            if duty == service_name:

                assigned_services.append(
                    (
                        service_name,
                        service_times,
                        asm
                    )
                )

    table_data = [
        [
            "Α/Α",
            "ΥΠΗΡΕΣΙΑ",
            "ΩΡΕΣ",
            "ΒΑΘΜΟΣ",
            "ΟΝΟΜΑΤΕΠΩΝΥΜΟ"
        ]
    ]

    aa = 1

    for service_name, service_times, asm in assigned_services:

        info = st.session_state.personnel.get(
            asm,
            {}
        )

        table_data.append(
            [
                str(aa),
                service_name,
                service_times or "",
                info.get("Βαθμός", ""),
                info.get("Ονοματεπώνυμο", "")
            ]
        )

        aa += 1

    def cell(x):

        return Paragraph(
            str(x),
            ParagraphStyle(
                "cell",
                fontName=PDF_FONT,
                fontSize=10,
                leading=12,
                alignment=TA_CENTER,
                wordWrap="CJK"
            )
        )



    table_data=[
        [
            cell(x)
            for x in row
        ]
        for row in table_data
    ]



    main_table = Table(
        table_data,
        colWidths=[
            30,   # Α/Α
            130,  # Υπηρεσία
            90,   # Ώρες
            60,   # Βαθμός
            220   # Ονοματεπώνυμο
        ]
    )

    main_table.setStyle(
        TableStyle(
            [
                ("GRID", (0,0), (-1,-1), 0.5, None),

                ("FONTNAME", (0,0), (-1,-1), PDF_FONT),

                ("FONTSIZE",(0,0),(-1,-1),12),

                ("ALIGN", (0,0), (-1,-1), "CENTER"),

                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),

                ("BACKGROUND", (0,0), (-1,0), "#d9d9d9")
            ]
        )
    )


    elements.append(main_table)


    elements.append(
        Spacer(1,10)
    )



    sign_table=Table(
        [
            [
                "-Ο-",
                "",
                "-Ο-"
            ],
            [
                "ΑΛΧΙΑΣ ΛΟΧΟΥ",
                "",
                "ΔΚΤΗΣ ΛΟΧΟΥ"
            ],
            [
                "",
                "",
                ""
            ],
            [
                alxias,
                "",
                diktis
            ],
            [
                alxias_rank,
                "",
                diktis_rank
            ]

        ],
        colWidths=[180,180,180]
    )



    sign_table.setStyle(
        TableStyle(
            [
                ("ALIGN",(0,0),(-1,-1),"CENTER"),
                ("FONTNAME",(0,0),(-1,-1),PDF_FONT),
                ("FONTSIZE",(0,0),(-1,-1),10)
            ]
        )
    )


    elements.append(sign_table)



    pdf.build(elements)

def create_thalamizomenon_pdf(filename, report_date):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()


    def setting(k):

        cur.execute(
            "SELECT value FROM settings WHERE key=?",
            (k,)
        )

        r = cur.fetchone()

        return r[0] if r else ""


    monada = setting("monada")
    loxos = setting("loxos")
    alxias = setting("alxias")
    diktis = setting("diktis")
    alxias_rank = setting("alxias_rank")
    diktis_rank = setting("diktis_rank")


    conn.close()



    pdf = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=25,
        leftMargin=25,
        topMargin=20,
        bottomMargin=20
    )


    elements=[]



    left_style = ParagraphStyle(
        "left_th",
        fontName=PDF_FONT,
        alignment=TA_LEFT,
        fontSize=10
    )


    right_style = ParagraphStyle(
        "right_th",
        fontName=PDF_FONT,
        alignment=TA_RIGHT,
        fontSize=10
    )


    title_style = ParagraphStyle(
        "title_th",
        fontName=PDF_FONT,
        alignment=TA_CENTER,
        fontSize=12
    )


    cell_style = ParagraphStyle(
        "cell_th",
        fontName=PDF_FONT,
        fontSize=8,
        leading=9,
        alignment=TA_CENTER
    )



    header = Table(
        [
            [
                Paragraph(monada,left_style),
                Paragraph(loxos,right_style)
            ]
        ],
        colWidths=[270,270]
    )


    header.setStyle(
        TableStyle(
            [
                ("VALIGN",(0,0),(-1,-1),"TOP")
            ]
        )
    )


    elements.append(header)


    elements.append(
        Spacer(1,15)
    )


    elements.append(
        Paragraph(
            f"<b><u>ΚΑΤΑΣΤΑΣΗ ΘΑΛΑΜΙΖΟΜΕΝΩΝ ΤΗΣ {report_date.strftime('%d/%m/%Y')}</u></b>",
            title_style
        )
    )


    elements.append(
        Spacer(1,15)
    )



    duties_day = st.session_state.duties.get(
        str(report_date),
        {}
    )

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    SELECT id, name, service_times
    FROM services
    WHERE active=1
    ORDER BY id
    """)

    all_services = cur.fetchall()

    conn.close()


    assigned_services = []

    for service_id, service_name, service_times in all_services:

        assigned_asm = None

        for asm, duty in duties_day.items():

            if duty == service_name:
                assigned_asm = asm
                break

        if assigned_asm:
            assigned_services.append(
                (
                    service_name,
                    service_times,
                    assigned_asm
                )
            )

    special_inside = []

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT name
        FROM special_status_types
        WHERE stay_inside=1
    """)

    for row in cur.fetchall():
        special_inside.append(row[0])

    conn.close()

    table_data = [

        [
            "Α/Α",
            "ΒΑΘΜΟΣ",
            "ΟΝΟΜΑΤΕΠΩΝΥΜΟ",
            "ΔΡΙΑ",
            "ΤΗΛΕΦΩΝΟ",
            "ΠΑΡ/ΣΕΙΣ"
        ]

    ]



    aa = 1



    for asm,info in st.session_state.personnel.items():


        duty = duties_day.get(
            asm,
            ""
        )

        special_status = ""

        if duty in special_inside:
            special_status = duty


        show_person = False


        # Όσοι έχουν υπηρεσία
        if duty:
            show_person = True


        # Όσοι έχουν ειδική κατάσταση που μένει μέσα
        if special_status in special_inside:
            show_person = True

        if show_person:

            paratirisi = ""

            if special_status in special_inside:
                paratirisi = special_status

            table_data.append(

                [

                    Paragraph(str(aa),cell_style),

                    Paragraph(info.get("Βαθμός",""),cell_style),

                    Paragraph(info.get("Ονοματεπώνυμο",""),cell_style),

                    Paragraph(info.get("ΔΡΙΑ",""),cell_style),

                    Paragraph(info.get("Τηλέφωνο",""),cell_style),

                    Paragraph(
                        special_status if special_status in special_inside else "",
                        cell_style
                    )

                ]

            )


            aa += 1




    table = Table(
        table_data,
        colWidths=[
            35,   # Α/Α
            70,   # ΒΑΘΜΟΣ
            150,  # ΟΝΟΜΑΤΕΠΩΝΥΜΟ
            60,   # ΔΡΙΑ (μικρότερη)
            100,  # ΤΗΛΕΦΩΝΟ (μεγαλύτερη)
            80    # ΠΑΡ/ΣΕΙΣ
        ],
        repeatRows=1
    )


    table.setStyle(

        TableStyle(

            [

                ("GRID",(0,0),(-1,-1),0.5,None),

                ("ALIGN",(0,0),(-1,-1),"CENTER"),

                ("VALIGN",(0,0),(-1,-1),"MIDDLE")

            ]

        )

    )


    elements.append(table)


    elements.append(
        Spacer(1,20)
    )



    sign_table = Table(

        [

            [
                "-Ο-",
                "",
                "-Ο-"
            ],

            [
                "ΑΛΧΙΑΣ ΛΟΧΟΥ",
                "",
                "ΔΚΤΗΣ ΛΟΧΟΥ"
            ],

            [
                "",
                "",
                ""
            ],

            [
                alxias,
                "",
                diktis
            ],

            [
                alxias_rank,
                "",
                diktis_rank
            ]

        ],

        colWidths=[180,180,180]

    )


    sign_table.setStyle(

        TableStyle(

            [

                ("ALIGN",(0,0),(-1,-1),"CENTER"),

                ("FONTNAME",(0,0),(-1,-1),PDF_FONT)

            ]

        )

    )


    elements.append(sign_table)


    pdf.build(elements)

def create_dianykterefseon_pdf(filename, report_date):

    from reportlab.lib import colors

    pdf = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=35,
        bottomMargin=35
    )


    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()


    def setting(k):

        cur.execute(
            "SELECT value FROM settings WHERE key=?",
            (k,)
        )

        r = cur.fetchone()

        return r[0] if r else ""


    monada = setting("monada")
    loxos = setting("loxos")
    alxias = setting("alxias")
    diktis = setting("diktis")
    alxias_rank = setting("alxias_rank")
    diktis_rank = setting("diktis_rank")


    conn.close()


    elements = []


    title_style = ParagraphStyle(
        "title_dian",
        fontName=PDF_FONT,
        alignment=TA_CENTER,
        fontSize=12,
        leading=14
    )


    normal_style = ParagraphStyle(
        "normal_dian",
        fontName=PDF_FONT,
        fontSize=9,
        leading=11
    )


    cell_style = ParagraphStyle(
        "cell_dian",
        fontName=PDF_FONT,
        fontSize=8,
        leading=9,
        alignment=TA_CENTER
    )


    # ΚΕΦΑΛΙΔΑ

    header = Table(
        [
            [
                Paragraph(monada, normal_style),
                Paragraph(
                    loxos,
                    ParagraphStyle(
                        "right_loxos",
                        fontName=PDF_FONT,
                        alignment=TA_RIGHT,
                        fontSize=9,
                        leading=11
                    )
                )
            ]
        ],
        colWidths=[250,250]
    )


    header.setStyle(
        TableStyle(
            [
                ("ALIGN",(0,0),(0,0),"LEFT"),
                ("ALIGN",(1,0),(1,0),"RIGHT")
            ]
        )
    )


    elements.append(header)


    elements.append(
        Spacer(1,20)
    )


    elements.append(
        Paragraph(
            f"<b><u>ΚΑΤΑΣΤΑΣΗ ΔΙΑΝΥΚΤΕΡΕΥΣΕΩΝ ΤΗΣ {report_date.strftime('%d/%m/%Y')}</u></b>",
            title_style
        )
    )


    elements.append(
        Spacer(1,20)
    )


    # ΥΠΗΡΕΣΙΕΣ ΗΜΕΡΑΣ

    duties_day = st.session_state.duties.get(
        str(report_date),
        {}
    )


    data = [

        [
            "Α/Α",
            "ΒΑΘΜΟΣ",
            "ΟΝΟΜΑΤΕΠΩΝΥΜΟ",
            "ΔΡΙΑ",
            "ΤΗΛΕΦΩΝΟ",
            "ΠΑΡ/ΣΕΙΣ"
        ]

    ]


    aa = 1


    for asm, info in st.session_state.personnel.items():


        duty = duties_day.get(
            asm,
            ""
        )


        if (

            duty == ""

            and info.get("ΔΝ","") == "ΝΑΙ"

            and info.get("ΕΥ","") != "ΝΑΙ"

            and info.get("ΕΘΕΛ","") != "ΝΑΙ"

            and info.get("ΤΙΜ","") != "ΝΑΙ"

            and info.get("ΑΔ","") != "ΝΑΙ"

            and info.get("ΣΤΕΠ","") != "ΝΑΙ"

            and info.get("ΝΟΣ","") != "ΝΑΙ"

        ):


            data.append(

                [

                    Paragraph(str(aa),cell_style),

                    Paragraph(
                        info.get("Βαθμός",""),
                        cell_style
                    ),

                    Paragraph(
                        info.get("Ονοματεπώνυμο",""),
                        cell_style
                    ),

                    Paragraph(
                        info.get("ΔΡΙΑ",""),
                        cell_style
                    ),

                    Paragraph(
                        info.get("Τηλέφωνο",""),
                        cell_style
                    ),

                    Paragraph(
                        "",
                        cell_style
                    )

                ]

            )


            aa += 1



    table = Table(
        data,
        repeatRows=1,
        colWidths=[
            35,
            55,
            180,
            70,
            80,
            70
        ]
    )


    table.setStyle(
        TableStyle(
            [

                ("GRID",
                 (0,0),
                 (-1,-1),
                 0.5,
                 colors.black),

                ("ALIGN",
                 (0,0),
                 (-1,-1),
                 "CENTER"),

                ("VALIGN",
                 (0,0),
                 (-1,-1),
                 "MIDDLE")

            ]
        )
    )


    elements.append(table)


    elements.append(
        Spacer(1,40)
    )


    # ΥΠΟΓΡΑΦΕΣ

    sign_table = Table(
        [
            [
                "-Ο-",
                "",
                "-Ο-"
            ],
            [
                "ΑΛΧΙΑΣ ΛΟΧΟΥ",
                "",
                "ΔΚΤΗΣ ΛΟΧΟΥ"
            ],
            [
                "",
                "",
                ""
            ],
            [
                alxias,
                "",
                diktis
            ],
            [
                alxias_rank,
                "",
                diktis_rank
            ]
        ],
        colWidths=[180,180,180]
    )


    sign_table.setStyle(
        TableStyle(
            [
                ("ALIGN",(0,0),(-1,-1),"CENTER"),
                ("FONTNAME",(0,0),(-1,-1),PDF_FONT)
            ]
        )
    )


    elements.append(sign_table)


    pdf.build(elements)

def create_exodouxon_pdf(filename, report_date):

    from reportlab.lib import colors

    pdf = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=35,
        leftMargin=35,
        topMargin=35,
        bottomMargin=35
    )

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    def setting(k):
        cur.execute(
            "SELECT value FROM settings WHERE key=?",
            (k,)
        )
        r = cur.fetchone()
        return r[0] if r else ""

    monada = setting("monada")
    loxos = setting("loxos")
    alxias = setting("alxias")
    diktis = setting("diktis")
    alxias_rank = setting("alxias_rank")
    diktis_rank = setting("diktis_rank")

    conn.close()

    elements = []

    title_style = ParagraphStyle(
        "title_exod",
        fontName=PDF_FONT,
        alignment=TA_CENTER,
        fontSize=12,
        leading=14
    )

    normal_style = ParagraphStyle(
        "normal_exod",
        fontName=PDF_FONT,
        fontSize=9,
        leading=11
    )

    cell_style = ParagraphStyle(
        "cell_exod",
        fontName=PDF_FONT,
        fontSize=8,
        leading=9,
        alignment=TA_CENTER
    )


    header = Table(
        [
            [
                Paragraph(monada, normal_style),
                Paragraph(
                    loxos,
                    ParagraphStyle(
                        "right_loxos_exod",
                        fontName=PDF_FONT,
                        alignment=TA_RIGHT,
                        fontSize=9,
                        leading=11
                    )
                )
            ]
        ],
        colWidths=[250,250]
    )

    header.setStyle(
        TableStyle(
            [
                ("ALIGN",(0,0),(0,0),"LEFT"),
                ("ALIGN",(1,0),(1,0),"RIGHT")
            ]
        )
    )

    elements.append(header)

    elements.append(Spacer(1,20))


    elements.append(
        Paragraph(
            f"<b><u>ΚΑΤΑΣΤΑΣΗ ΕΞΟΔΟΥΧΩΝ ΤΗΣ {report_date.strftime('%d/%m/%Y')}</u></b>",
            title_style
        )
    )

    elements.append(Spacer(1,20))


    duties_day = st.session_state.duties.get(
        str(report_date),
        {}
    )


    data = [
        [
            "Α/Α",
            "ΒΑΘΜΟΣ",
            "ΟΝΟΜΑΤΕΠΩΝΥΜΟ",
            "ΔΡΙΑ",
            "ΤΗΛΕΦΩΝΟ",
            "ΠΑΡ/ΣΕΙΣ"
        ]
    ]


    aa = 1


    for asm, info in st.session_state.personnel.items():

        duty = duties_day.get(
            asm,
            ""
        )


        if (

            duty == ""

            and info.get("ΔΝ","") == "ΟΧΙ"

            and info.get("ΕΥ","") != "ΝΑΙ"
            and info.get("ΕΘΕΛ","") != "ΝΑΙ"
            and info.get("ΤΙΜ","") != "ΝΑΙ"
            and info.get("ΑΔ","") != "ΝΑΙ"
            and info.get("ΣΤΕΠ","") != "ΝΑΙ"
            and info.get("ΝΟΣ","") != "ΝΑΙ"

        ):

            data.append(
                [
                    Paragraph(str(aa),cell_style),

                    Paragraph(
                        info.get("Βαθμός",""),
                        cell_style
                    ),

                    Paragraph(
                        info.get("Ονοματεπώνυμο",""),
                        cell_style
                    ),

                    Paragraph(
                        info.get("ΔΡΙΑ",""),
                        cell_style
                    ),

                    Paragraph(
                        info.get("Τηλέφωνο",""),
                        cell_style
                    ),

                    Paragraph(
                        "",
                        cell_style
                    )
                ]
            )

            aa += 1



    table = Table(
        data,
        repeatRows=1,
        colWidths=[
            35,
            55,
            180,
            70,
            80,
            70
        ]
    )


    table.setStyle(
        TableStyle(
            [
                ("GRID",(0,0),(-1,-1),0.5,colors.black),
                ("ALIGN",(0,0),(-1,-1),"CENTER"),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE")
            ]
        )
    )


    elements.append(table)

    elements.append(Spacer(1,40))


    sign_table = Table(
        [
            ["-Ο-","","-Ο-"],
            ["ΑΛΧΙΑΣ ΛΟΧΟΥ","","ΔΚΤΗΣ ΛΟΧΟΥ"],
            ["","",""],
            [alxias,"",diktis],
            [alxias_rank,"",diktis_rank]
        ],
        colWidths=[180,180,180]
    )


    sign_table.setStyle(
        TableStyle(
            [
                ("ALIGN",(0,0),(-1,-1),"CENTER"),
                ("FONTNAME",(0,0),(-1,-1),PDF_FONT)
            ]
        )
    )


    elements.append(sign_table)

    pdf.build(elements)

import calendar

def create_interview_pdf(filename, asm, person_info):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    def setting(k):

        cur.execute(
            "SELECT value FROM settings WHERE key=?",
            (k,)
        )

        r = cur.fetchone()

        return r[0] if r else ""


    monada = setting("monada")
    loxos = setting("loxos")
    diktis = setting("diktis")
    diktis_rank = setting("diktis_rank")

    conn.close()



    pdf = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=30,
        bottomMargin=30
    )


    normal = ParagraphStyle(
        "normal",
        fontName=PDF_FONT,
        fontSize=12,
        leading=15,
        alignment=TA_LEFT
    )


    title = ParagraphStyle(
        "title",
        fontName=PDF_FONT,
        fontSize=12,
        leading=15,
        alignment=TA_CENTER
    )


    center = ParagraphStyle(
        "center",
        fontName=PDF_FONT,
        fontSize=12,
        alignment=TA_CENTER
    )


    elements = []


    # ΤΙΤΛΟΣ

    elements.append(
        Paragraph(
            "<b><u>ΚΑΡΤΕΛΑ ΣΤΟΙΧΕΙΩΝ<br/>"
            "ΤΑΥΤΟΤΗΤΑΣ ΚΑΙ ΣΥΝΕΝΤΕΥΞΗΣ ΣΤΕΛΕΧΩΝ – ΟΒΑ – ΟΠΛΙΤΩΝ<br/>"
            "ΘΗΤΕΙΑΣ ΑΠΟ ΤΟ ΔΚΤΗ ΜΟΝΑΔΑΣ – ΥΠΟΜΟΝΑΔΑΣ</u></b>",
            title
        )
    )


    elements.append(
        Spacer(1,20)
    )


    # ΦΩΤΟΓΡΑΦΙΑ - ΜΟΝΑΔΑ

    photo_table = Table(
        [
            [
                Paragraph(
                    "ΦΩΤΟΓΡΑΦΙΑ",
                    ParagraphStyle(
                        "photo_text",
                        fontName=PDF_FONT,
                        fontSize=10,
                        alignment=TA_CENTER
                    )
                ),
                Paragraph(
                    f"{monada}/{loxos}",
                    ParagraphStyle(
                        "right_unit",
                        fontName=PDF_FONT,
                        fontSize=12,
                        alignment=TA_RIGHT
                    )
                )
            ]
        ],
        colWidths=[90,360],
        rowHeights=[90]
    )


    photo_table.setStyle(
        TableStyle(
            [
                ("BOX",(0,0),(0,0),1,None),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                ("ALIGN",(0,0),(0,0),"CENTER"),
                ("ALIGN",(1,0),(1,0),"RIGHT")
            ]
        )
    )


    elements.append(photo_table)


    elements.append(
        Spacer(1,20)
    )


    # ΣΤΟΙΧΕΙΑ

    fields = [

        ("1. ΒΑΘΜΟΣ:", person_info.get("Βαθμός","")),

        ("2. ΟΝΟΜΑΤΕΠΩΝΥΜΟ:", person_info.get("Ονοματεπώνυμο","")),

        ("3. ΟΝΟΜΑ ΠΑΤΕΡΑ:", person_info.get("Πατρώνυμο","")),

        ("4. ΟΝΟΜΑ ΜΗΤΕΡΑΣ:", person_info.get("Μητρώνυμο","")),

        ("5. ΤΟΠΟΣ ΚΑΤΑΓΩΓΗΣ:", person_info.get("Τόπος Καταγωγής","")),

        ("6. ΤΟΠΟΣ ΔΙΑΜΟΝΗΣ:", person_info.get("Τόπος Διαμονής","")),

        ("7. ΤΗΛΕΦΩΝΑ ΟΙΚΙΑΣ ΣΥΓΓΕΝΩΝ:", person_info.get("Τηλέφωνο Συγγενή","")),

        ("8. ΕΠΑΓΓΕΛΜΑ:", person_info.get("Επάγγελμα (ως πολίτης)","")),

        ("9. ΕΙΔΙΚΕΣ ΓΝΩΣΕΙΣ:", person_info.get("Ειδικές Γνώσεις","")),

        ("10. ΓΡΑΜΜΑΤΙΚΕΣ ΓΝΩΣΕΙΣ:", person_info.get("Γραμματικές Γνώσεις","")),

        ("11. ΞΕΝΕΣ ΓΛΩΣΣΕΣ:", person_info.get("Ξένες Γλώσσες","")),

        ("12. ΕΙΔΙΚΟΤΗΤΑ ΣΤΟ ΣΤΡΑΤΟ:",""),

        ("13. ΑΣΜ:", asm),

        ("14. ΗΜΕΡΟΜΗΝΙΑ ΕΙΣΟΔΟΥ ΣΤΗ ΜΟΝΑΔΑ:", person_info.get("Ημερομηνία Εισόδου στη Μονάδα","")),

        ("15. ΚΑΤΑΣΤΑΣΗ ΥΓΕΙΑΣ:", person_info.get("Κατάσταση Υγείας","")),

        ("16. ΟΙΚΟΓΕΝΕΙΑΚΗ ΚΑΤΑΣΤΑΣΗ:", person_info.get("Οικογενειακή Κατάσταση","")),

        ("17. ΟΙΚΟΝΟΜΙΚΗ ΚΑΤΑΣΤΑΣΗ:", person_info.get("Οικονομική Κατάσταση","")),

        ("18. ΙΔΙΑΙΤΕΡΑ ΠΡΟΒΛΗΜΑΤΑ ΠΟΥ ΤΟ ΑΠΑΣΧΟΛΟΥΝ:", person_info.get("Ιδιαίτερα Προβλήματα","")),

        ("19. ΠΟΙΝΕΣ:",""),

        ("20. ΑΔΕΙΕΣ:",""),

        ("21. ΣΥΜΠΕΡΑΣΜΑΤΑ ΑΠΟ ΤΗ ΣΥΝΕΝΤΕΥΞΗ:","")

    ]


    for label,value in fields:

        elements.append(
            Paragraph(
                f"{label} {value}",
                normal
            )
        )



    elements.append(
        Spacer(1,30)
    )


    # ΥΠΟΓΡΑΦΗ

    sign_table = Table(
        [
            ["","","-Ο-"],
            ["","","ΔΚΤΗΣ ΛΟΧΟΥ"],
            ["","",""],
            ["","","" + diktis],
            ["","",diktis_rank]
        ],
        colWidths=[120,120,180]
    )


    sign_table.setStyle(
        TableStyle(
            [
                ("ALIGN",(0,0),(-1,-1),"CENTER"),
                ("FONTNAME",(0,0),(-1,-1),PDF_FONT),
                ("FONTSIZE",(0,0),(-1,-1),12)
            ]
        )
    )


    elements.append(sign_table)


    pdf.build(elements)

def create_vehicle_passes_pdf(filename):

    from reportlab.platypus import (
        SimpleDocTemplate,
        Table,
        TableStyle,
        Paragraph,
        Spacer,
        PageBreak,
        Image
    )

    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    def setting(k):

        cur.execute(
            "SELECT value FROM settings WHERE key=?",
            (k,)
        )

        r = cur.fetchone()

        return r[0] if r else ""

    monada = setting("monada")

    emblem_path = setting("emblem")

    stratopedo_tel = setting("stratopedo_tel")

    conn.close()

    pdf = SimpleDocTemplate(
        filename,
        pagesize=A4
    )

    center = ParagraphStyle(
        "center",
        fontName=PDF_FONT,
        alignment=TA_CENTER,
        fontSize=9
    )

    left = ParagraphStyle(
        "left",
        fontName=PDF_FONT,
        alignment=TA_LEFT,
        fontSize=9
    )

    elements = []

    vehicle_personnel = []

    for asm, info in st.session_state.personnel.items():

        if (
            info.get("Τύπος Οχήματος","")
            and info.get("Χρώμα Οχήματος","")
            and info.get("Αρ. Κυκλοφορίας","")
        ):

            vehicle_personnel.append(
                (asm, info)
            )

    if not vehicle_personnel:

        elements.append(
            Paragraph(
                "Δεν βρέθηκαν οχήματα",
                center
            )
        )

        pdf.build(elements)
        return

    for asm, info in vehicle_personnel:

        table_data = [

            [
                Paragraph(
                    "<b>ΔΕΛΤΙΟ ΕΙΣΟΔΟΥ<br/>ΟΧΗΜΑΤΟΣ</b>",
                    center
                ),
                Paragraph(
                    "ΑΑΔ:",
                    left
                )
            ],

            [
                Paragraph(
                    f"ΤΥΠΟΣ ΟΧΗΜΑΤΟΣ:<br/><b>{info.get('Τύπος Οχήματος','')}</b>",
                    center
                ),
                Paragraph(
                    f"ΧΡΩΜΑ ΟΧΗΜΑΤΟΣ:<br/><b>{info.get('Χρώμα Οχήματος','')}</b>",
                    center
                )
            ],

            [
                Paragraph(
                    f"ΗΜΕΡΟΜΗΝΙΑ ΕΚΔΟΣΗΣ:<br/><b>{datetime.now().strftime('%d/%m/%Y')}</b>",
                    center
                ),
                Paragraph(
                    f"ΑΡ. ΚΥΚΛΟΦΟΡΙΑΣ:<br/><b>{info.get('Αρ. Κυκλοφορίας','')}</b>",
                    center
                )
            ],

            [
                Image(emblem_path, width=3*cm, height=3*cm)
                if emblem_path and os.path.exists(emblem_path)
                else Paragraph("ΕΜΒΛΗΜΑ", center),
                ""
            ],

            [
                Paragraph(
                    f"ΒΑΘΜΟΣ: {info.get('Βαθμός','')}",
                    left
                ),
                ""
            ],

            [
                Paragraph(
                    f"ΟΝΟΜΑΤΕΠΩΝΥΜΟ: {info.get('Ονοματεπώνυμο','')}",
                        left
                ),
                ""
            ],

        ]

        t = Table(
            table_data,
            colWidths=[4*cm, 4*cm],
            rowHeights=[
                1.5*cm,   # ΔΕΛΤΙΟ ΕΙΣΟΔΟΥ
                1.5*cm,   # ΤΥΠΟΣ - ΧΡΩΜΑ
                1.5*cm,   # ΗΜΕΡΟΜΗΝΙΑ - ΚΥΚΛΟΦΟΡΙΑ
                3.5*cm,   # ΕΜΒΛΗΜΑ
                1.5*cm,   # ΒΑΘΜΟΣ
                1.5*cm    # ΟΝΟΜΑΤΕΠΩΝΥΜΟ
]
        )

        t.setStyle(
            TableStyle(
                [

                    ("GRID",(0,0),(-1,-1),2,colors.black),

                    ("SPAN",(0,3),(1,3)),
                    ("SPAN",(0,4),(1,4)),
                    ("SPAN",(0,5),(1,5)),

                    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),

                    ("ALIGN",(0,0),(-1,-1),"CENTER")

                ]
            )
        )

        elements.append(t)

        elements.append(PageBreak())

        back_text = f"""
Εκδίδουσα Αρχή: {monada}/2ο Γραφείο<br/>

1. Το παρόν δελτίο είναι στρατιωτικό έγγραφο.<br/>

2. Ισχύει μόνο για τα οχήματα του Στρατιωτικού και πολιτικού προσωπικού του Στρδου.<br/>

3. Το παρόν τοποθετείται στο παρμπρίζ του οχήματος κατά την είσοδο αλλά και καθ’ όλο το χρόνο στάθμευσης του εντός του Στρατοπέδου.<br/>

4. Ο ανευρίσκων το παρόν υποχρεούται να το παραδώσει στις Αστυνομικές ή Στρατιωτικές Αρχές ή να επικοινωνήσει με το {stratopedo_tel}.<br/>

5. Ο κάτοχος υποχρεούται να τηρεί τους κανόνες ασφαλείας του Στρδου και να δέχεται τους προβλεπόμενους ελέγχους.<br/>

6. Το παρόν δελτίο από μόνο του δεν παρέχει το δικαίωμα εισόδου στο Στρδο.<br/>

Ημερομηνία Έκδοσης: {datetime.now().strftime("%d/%m/%Y")}



<br/><br/>

<center>
Θεωρήθηκε<br/>
-Ο-<br/>
Στρατοπεδάρχης
</center>
"""

        back_table = Table(
            [
                [
                    Paragraph(back_text, left)
                ]
            ],
            colWidths=[8*cm],
            rowHeights=[11*cm]
        )

        back_table.setStyle(
            TableStyle(
                [
                    ("GRID",(0,0),(-1,-1),2,colors.black),
                    ("VALIGN",(0,0),(-1,-1),"TOP")
                ]
            )
        )

        elements.append(back_table)

        elements.append(PageBreak())

    pdf.build(elements)

def create_tampeles_foriamon_pdf(filename):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()


    def setting(k):

        cur.execute(
            "SELECT value FROM settings WHERE key=?",
            (k,)
        )

        r = cur.fetchone()

        return r[0] if r else ""


    monada = setting("monada")
    loxos = setting("loxos")
    emblem = setting("emblem")


    conn.close()


    pdf = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )


    style = ParagraphStyle(
        "Arial",
        fontName=PDF_FONT,
        fontSize=8,
        leading=9
    )


    center = ParagraphStyle(
        "center",
        fontName=PDF_FONT,
        fontSize=8,
        alignment=TA_CENTER
    )


    left = ParagraphStyle(
        "left",
        fontName=PDF_FONT,
        fontSize=8,
        alignment=TA_LEFT
    )


    right = ParagraphStyle(
        "right",
        fontName=PDF_FONT,
        fontSize=8,
        alignment=TA_RIGHT
    )


    elements=[]
    cards=[]

    for asm,info in st.session_state.personnel.items():


        emblem_img=""

        if emblem and os.path.exists(emblem):

            emblem_img = Image(
                emblem,
                width=32,
                height=32
            )


        table_data=[

            [
                Paragraph(
                    monada,
                    left
                ),

                emblem_img,

                Paragraph(
                    loxos,
                    right
                )
            ],


            [
                Paragraph(
                    "ΒΑΘΜΟΣ:",
                    left
                ),

                Paragraph(
                    info.get("Βαθμός",""),
                    center
                ),

                ""
            ],


            [
                Paragraph(
                    "ΟΝΟΜΑΤΕΠΩΝΥΜΟ:",
                    left
                ),

                Paragraph(
                    info.get("Ονοματεπώνυμο",""),
                    center
                ),

                ""
            ],


            [
                Paragraph(
                    "ΑΣΜ:",
                    left
                ),

                Paragraph(
                    asm,
                    center
                ),

                ""
            ],


            [
                Paragraph(
                    "ΑΡ. ΟΠΛΟΥ:",
                    left
                ),

                Paragraph(
                    info.get("Αριθμός Όπλου",""),
                    center
                ),

                ""
            ]

        ]


        table = Table(
            table_data,
            colWidths=[
                100,
                150,
                147
            ],
            rowHeights=[
                35,   # 1η γραμμή (έμβλημα + μονάδα + λόχος)
                16,   # ΒΑΘΜΟΣ
                18,   # ΟΝΟΜΑΤΕΠΩΝΥΜΟ
                15,   # ΑΣΜ
                15    # ΑΡ. ΟΠΛΟΥ
            ]
        )


        table.setStyle(
            TableStyle(
                [

                    ("SPAN",(1,1),(2,1)),
                    ("SPAN",(1,2),(2,2)),
                    ("SPAN",(1,3),(2,3)),
                    ("SPAN",(1,4),(2,4)),


                    ("GRID",(0,0),(-1,-1),2,None),

                    ("BOX",(0,0),(-1,-1),3,None),


                    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),


                    ("ALIGN",(0,0),(-1,-1),"CENTER")

                ]
            )
        )


        cards.append(
            table
        )

    for card in cards:

        page_table = Table(
            [[card]],
            colWidths=[
                397
            ],
            hAlign="CENTER"
        )


        page_table.setStyle(
            TableStyle(
                [

                    (
                        "VALIGN",
                        (0,0),
                        (-1,-1),
                        "TOP"
                    ),

                    (
                        "LEFTPADDING",
                        (0,0),
                        (-1,-1),
                        10
                    ),

                    (
                        "RIGHTPADDING",
                        (0,0),
                        (-1,-1),
                        10
                    ),

                    (
                        "TOPPADDING",
                        (0,0),
                        (-1,-1),
                        5
                    ),

                    (
                        "BOTTOMPADDING",
                        (0,0),
                        (-1,-1),
                        5
                    )

                ]
            )
        )


        elements.append(
            KeepTogether(
                page_table
            )
        )


        elements.append(
            Spacer(1,15)
        )

    elements.insert(
        0,
        Spacer(1,10)
    )

    pdf.build(elements)

def create_deltia_theseos_pdf(filename):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()


    def setting(k):

        cur.execute(
            "SELECT value FROM settings WHERE key=?",
            (k,)
        )

        r = cur.fetchone()

        return r[0] if r else ""


    monada = setting("monada")
    loxos = setting("loxos")
    emblem = setting("emblem")


    conn.close()


    pdf = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20
    )


    style = ParagraphStyle(
        "Arial",
        fontName=PDF_FONT,
        fontSize=8,
        leading=9
    )


    center = ParagraphStyle(
        "center",
        fontName=PDF_FONT,
        fontSize=8,
        alignment=TA_CENTER
    )


    left = ParagraphStyle(
        "left",
        fontName=PDF_FONT,
        fontSize=8,
        alignment=TA_LEFT
    )


    right = ParagraphStyle(
        "right",
        fontName=PDF_FONT,
        fontSize=8,
        alignment=TA_RIGHT
    )


    elements=[]
    cards=[]

    for asm,info in st.session_state.personnel.items():


        emblem_img=""

        if emblem and os.path.exists(emblem):

            emblem_img = Image(
                emblem,
                width=60,
                height=60
            )


        table_data=[

            [
                Paragraph(
                    monada,
                    left
                ),

                emblem_img,

                Paragraph(
                    loxos,
                    right
                )
            ],


            [
                Paragraph(
                    "ΒΑΘΜΟΣ:",
                    left
                ),

                Paragraph(
                    info.get("Βαθμός",""),
                    center
                ),

                ""
            ],


            [
                Paragraph(
                    "ΟΝΟΜΑΤΕΠΩΝΥΜΟ:",
                    left
                ),

                Paragraph(
                    info.get("Ονοματεπώνυμο",""),
                    center
                ),

                ""
            ],


            [
                Paragraph(
                    "ΑΣΜ:",
                    left
                ),

                Paragraph(
                    asm,
                    center
                ),

                ""
            ],


            [
                Paragraph(
                    "ΑΡ. ΟΠΛΟΥ:",
                    left
                ),

                Paragraph(
                    info.get("Αριθμός Όπλου",""),
                    center
                ),

                ""
            ]

        ]


        table = Table(
            table_data,
            colWidths=[
                110,
                160,
                155
            ],
            rowHeights=[
                70,
                45,
                65,
                45,
                58
            ]
        )


        table.setStyle(
            TableStyle(
                [

                    ("SPAN",(1,1),(2,1)),
                    ("SPAN",(1,2),(2,2)),
                    ("SPAN",(1,3),(2,3)),
                    ("SPAN",(1,4),(2,4)),


                    ("GRID",(0,0),(-1,-1),2,None),

                    ("BOX",(0,0),(-1,-1),3,None),


                    ("VALIGN",(0,0),(-1,-1),"MIDDLE"),


                    ("ALIGN",(0,0),(-1,-1),"CENTER")

                ]
            )
        )


        cards.append(
            table
        )

    for card in cards:

        page_table = Table(
            [[card]],
            colWidths=[
                397
            ],
            hAlign="CENTER"
        )


        page_table.setStyle(
            TableStyle(
                [

                    (
                        "VALIGN",
                        (0,0),
                        (-1,-1),
                        "TOP"
                    ),

                    (
                        "LEFTPADDING",
                        (0,0),
                        (-1,-1),
                        10
                    ),

                    (
                        "RIGHTPADDING",
                        (0,0),
                        (-1,-1),
                        10
                    ),

                    (
                        "TOPPADDING",
                        (0,0),
                        (-1,-1),
                        5
                    ),

                    (
                        "BOTTOMPADDING",
                        (0,0),
                        (-1,-1),
                        5
                    )

                ]
            )
        )


        elements.append(
            KeepTogether(
                page_table
            )
        )


        elements.append(
            Spacer(1,15)
        )

    elements.insert(
        0,
        Spacer(1,10)
    )

    pdf.build(elements)

def create_tampeles_sakou_imatismou_pdf(filename):

    elements = []
    cards = []

    pdf = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=15,
        leftMargin=15,
        topMargin=15,
        bottomMargin=15
    )


    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()


    cur.execute(
        "SELECT asm, data FROM personnel"
    )

    people = cur.fetchall()

    cur.execute(
        "SELECT value FROM settings WHERE key='emblem'"
    )

    result = cur.fetchone()

    emblem_path = result[0] if result else ""


    conn.close()



    center_style = ParagraphStyle(
        "center",
        fontName=PDF_FONT,
        fontSize=7,
        leading=7,
        alignment=TA_CENTER
    )



    for person in people:


        asm = person[0]

        data = json.loads(
            person[1]
        )


        vathmos = data.get(
            "Βαθμός",
            ""
        )

        onomatep = data.get(
            "Ονοματεπώνυμο",
            ""
        )

        if emblem_path and os.path.exists(emblem_path):

            emblem_img = Image(
                emblem_path,
                width=18,
                height=18
            )

        else:

            emblem_img = Paragraph(
                "",
                center_style
            )



        name_text = Paragraph(
            f"{vathmos} {onomatep}",
            center_style
        )


        asm_text = Paragraph(
            f"ΑΣΜ: {asm}",
            center_style
        )



        table = Table(
            [
                [
                    emblem_img,
                    name_text
                ],
                [
                    "",
                    asm_text
                ]
            ],
            colWidths=[
                25,
                74
            ],
            rowHeights=[
                32,
                25
            ]
        )



        table.setStyle(
            TableStyle(
                [

                    (
                        "SPAN",
                        (0,0),
                        (0,1)
                    ),


                    (
                        "BOX",
                        (0,0),
                        (-1,-1),
                        3,
                        None
                    ),


                    (
                        "ALIGN",
                        (0,0),
                        (-1,-1),
                        "CENTER"
                    ),


                    (
                        "VALIGN",
                        (0,0),
                        (-1,-1),
                        "MIDDLE"
                    ),


                    (
                        "FONTNAME",
                        (0,0),
                        (-1,-1),
                        PDF_FONT
                    )

                ]
            )
        )



        cards.append(
            table
        )

    for i in range(0, len(cards), 3):

        row = []

        for j in range(3):

            if i + j < len(cards):
                row.append(
                    cards[i+j]
                )
            else:
                row.append(
                    ""
                )


        page_table = Table(
            [
                row
            ],
            colWidths=[
                120,
                120,
                120
            ]
        )


        page_table.setStyle(
            TableStyle(
                [
                    (
                        "VALIGN",
                        (0,0),
                        (-1,-1),
                        "TOP"
                    )
                ]
            )
        )


        elements.append(
            KeepTogether(
                page_table
            )
        )


        elements.append(
            Spacer(
                1,
                8
            )
        )

    pdf.build(
        elements
    )

def create_monthly_service_report_pdf(
    filename,
    selected_month,
    selected_year
):

    month_names = {
        1:"ΙΑΝΟΥΑΡΙΟΥ",
        2:"ΦΕΒΡΟΥΑΡΙΟΥ",
        3:"ΜΑΡΤΙΟΥ",
        4:"ΑΠΡΙΛΙΟΥ",
        5:"ΜΑΙΟΥ",
        6:"ΙΟΥΝΙΟΥ",
        7:"ΙΟΥΛΙΟΥ",
        8:"ΑΥΓΟΥΣΤΟΥ",
        9:"ΣΕΠΤΕΜΒΡΙΟΥ",
        10:"ΟΚΤΩΒΡΙΟΥ",
        11:"ΝΟΕΜΒΡΙΟΥ",
        12:"ΔΕΚΕΜΒΡΙΟΥ"
    }

    pdf = SimpleDocTemplate(
        filename,
        pagesize=landscape(A4),
        leftMargin=10,
        rightMargin=10,
        topMargin=10,
        bottomMargin=10
    )

    elements=[]

    title_style=ParagraphStyle(
        "title",
        fontName=PDF_FONT,
        alignment=TA_CENTER,
        fontSize=10
    )

    elements.append(
        Paragraph(
            f"ΕΛΕΓΧΟΣ ΥΠΗΡΕΣΙΩΝ ΜΗΝΟΣ {month_names[selected_month]} {selected_year}",
            title_style
        )
    )

    elements.append(
        Spacer(1,10)
    )

    days_in_month = calendar.monthrange(
        selected_year,
        selected_month
    )[1]

    headers=["ΑΣΜ"]

    for day in range(1,days_in_month+1):
        headers.append(str(day))

    headers.append("ΣΥΝΟΛΟ")

    table_data=[headers]

    duty_map = {

        "ΚΕΝΤΡΙΚΗ ΠΥΛΗ Νο1":"ΚΠ1",
        "ΚΕΝΤΡΙΚΗ ΠΥΛΗ Νο2":"ΚΠ2",
        "ΚΕΝΤΡΙΚΗ ΠΥΛΗ Νο3":"ΚΠ3",
        "ΚΕΝΤΡΙΚΗ ΠΥΛΗ Νο4":"ΚΠ4",

        "ΒΟΗΘΟΣ ΚΕΝΤΡΙΚΗΣ ΠΥΛΗΣ Νο1":"ΒΚΠ1",
        "ΒΟΗΘΟΣ ΚΕΝΤΡΙΚΗΣ ΠΥΛΗΣ Νο2":"ΒΚΠ2",
        "ΒΟΗΘΟΣ ΚΕΝΤΡΙΚΗΣ ΠΥΛΗΣ Νο3":"ΒΚΠ3",
        "ΒΟΗΘΟΣ ΚΕΝΤΡΙΚΗΣ ΠΥΛΗΣ Νο4":"ΒΚΠ4",

        "ΠΕΡΙΠΟΛΟ Νο1":"ΠΕΡ1",
        "ΠΕΡΙΠΟΛΟ Νο2":"ΠΕΡ2",
        "ΠΕΡΙΠΟΛΟ Νο3":"ΠΕΡ3",
        "ΠΕΡΙΠΟΛΟ Νο4":"ΠΕΡ4",

        "ΒΟΗΘΟΣ ΠΕΡΙΠΟΛΟΥ Νο1":"ΒΠΕΡ1",
        "ΒΟΗΘΟΣ ΠΕΡΙΠΟΛΟΥ Νο2":"ΒΠΕΡ2",
        "ΒΟΗΘΟΣ ΠΕΡΙΠΟΛΟΥ Νο3":"ΒΠΕΡ3",
        "ΒΟΗΘΟΣ ΠΕΡΙΠΟΛΟΥ Νο4":"ΒΠΕΡ4",

        "ΑΟΤ Νο1":"ΑΟΤ1",
        "ΑΟΤ Νο2":"ΑΟΤ2",
        "ΑΟΤ Νο3":"ΑΟΤ3",
        "ΑΟΤ Νο4":"ΑΟΤ4",

        "ΒΟΗΘΟΣ ΑΟΤ Νο1":"ΒΑΟΤ1",
        "ΒΟΗΘΟΣ ΑΟΤ Νο2":"ΒΑΟΤ2",
        "ΒΟΗΘΟΣ ΑΟΤ Νο3":"ΒΑΟΤ3",
        "ΒΟΗΘΟΣ ΑΟΤ Νο4":"ΒΑΟΤ4",

        "ΘΑΛΑΜΟΦΥΛΑΚΑΣ Νο1":"Θ1",
        "ΘΑΛΑΜΟΦΥΛΑΚΑΣ Νο2":"Θ2",
        "ΘΑΛΑΜΟΦΥΛΑΚΑΣ Νο3":"Θ3",

        "ΒΟΗΘΟΣ ΘΑΛΑΜΟΦΥΛΑΚΑ Νο1":"ΒΘ1",
        "ΒΟΗΘΟΣ ΘΑΛΑΜΟΦΥΛΑΚΑ Νο2":"ΒΘ2",
        "ΒΟΗΘΟΣ ΘΑΛΑΜΟΦΥΛΑΚΑ Νο3":"ΒΘ3",

        "ΑΜ":"ΑΜ",
        "ΥΠΑΡΧΙΦΥΛΑΚΑΣ":"ΥΠ",
        "ΟΡΓΑΝΟ ΥΠΗΡΕΣΙΑΣ ΛΟΧΟΥ":"ΟΥΛ",

        "ΗΣΑ1":"ΗΣΑ1",
        "ΗΣΑ2":"ΗΣΑ2",
        "ΗΣΑ3":"ΗΣΑ3",

        "ΕΘΕΛΟΝΤΙΚΑ ΕΝΤΟΣ":"ΕΘΕΛ"
    }

    special_map = {}

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
        SELECT
            name,
            short_name
        FROM special_status_types
    """)

    for name, short_name in cur.fetchall():
        special_map[name] = short_name

    conn.close()

    excluded = list(special_map.keys())

    excluded.extend([
        "ΕΥ",
        "ΤΙΜΩΡΗΜΕΝΟΣ"
    ])

    for asm in sorted(st.session_state.personnel.keys()):

        row=[asm]
        total=0

        for day in range(1,days_in_month+1):

            date_key=f"{selected_year}-{selected_month:02d}-{day:02d}"

            duty=""

            if date_key in st.session_state.duties:

                duty=st.session_state.duties[date_key].get(
                    asm,
                    ""
                )

            short_name = duty_map.get(
                duty,
                special_map.get(
                    duty,
                    ""
                )
            )

            row.append(short_name)

            if duty and duty not in special_map:
                total += 1

        row.append(str(total))

        table_data.append(row)

    col_widths=[45]

    for _ in range(days_in_month):
        col_widths.append(16)

    col_widths.append(30)

    table=Table(
        table_data,
        colWidths=col_widths,
        repeatRows=1
    )

    table.setStyle(
        TableStyle(
            [
                ("GRID",(0,0),(-1,-1),0.4,None),
                ("FONTNAME",(0,0),(-1,-1),PDF_FONT),
                ("FONTSIZE",(0,0),(-1,-1),5),
                ("ALIGN",(0,0),(-1,-1),"CENTER"),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE")
            ]
        )
    )

    elements.append(table)

    pdf.build(elements)

# =========================
# ΦΟΡΜΑ ΠΡΟΣΩΠΙΚΟΥ
# =========================

def create_weapons_pdf(filename, report_date):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    def setting(k):
        cur.execute(
            "SELECT value FROM settings WHERE key=?",
            (k,)
        )

        r = cur.fetchone()

        return r[0] if r else ""

    monada = setting("monada")
    loxos = setting("loxos")
    diktis = setting("diktis")
    diktis_rank = setting("diktis_rank")
    aksos_oplismou = setting("aksos_oplismou")
    aksos_oplismou_rank = setting("aksos_oplismou_rank")

    conn.close()


    pdf = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=25,
        leftMargin=25,
        topMargin=20,
        bottomMargin=20
    )


    elements = []


    header_style = ParagraphStyle(
        "weapon_header",
        fontName=PDF_FONT,
        fontSize=8,
        leading=9,
        alignment=TA_LEFT
    )

    style = ParagraphStyle(
        "weapon_cell",
        fontName=PDF_FONT,
        fontSize=8,
        leading=9,
        alignment=TA_CENTER
    )


    title_style = ParagraphStyle(
        "weapon_title",
        fontName=PDF_FONT,
        fontSize=12,
        alignment=TA_CENTER
    )

    name_style = ParagraphStyle(
        "weapon_name",
        fontName=PDF_FONT,
        fontSize=8,
        leading=9,
        alignment=TA_CENTER
    )

    header = Table(
        [
            [
                "",
                "",
                "",
                Paragraph(monada, header_style)
            ],
            [
                "",
                "",
                "",
                Paragraph(loxos, header_style)
            ],
            [
                "",
                "",
                "",
                Paragraph(report_date.strftime("%d/%m/%Y"), header_style)
            ]
        ],
        colWidths=[150,150,130,90]
    )


    header.setStyle(
        TableStyle(
            [
                ("ALIGN",(0,0),(-1,-1),"LEFT"),
                ("VALIGN",(0,0),(-1,-1),"TOP")
            ]
        )
    )


    elements.append(header)

    elements.append(
        Spacer(1,15)
    )

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 
            asm,
            weapon_type,
            presence,
            absent_reason
        FROM weapons
        """
    )

    weapons_data = cur.fetchall()

    weapons_data = sorted(
        weapons_data,
        key=lambda x: (
            0 if x[1] == "G3A4" else 1,
            int(
                st.session_state.personnel.get(
                    x[0],
                    {}
                ).get(
                    "Θέση Οπλοβαστού",
                    999
                )
            )
        )
    )

    conn.close()

    table_data = [

        [
            "Α/Α",
            "ΒΑΘΜΟΣ",
            "ΟΝΟΜΑΤΕΠΩΝΥΜΟ",
            Paragraph(
                "ΤΥΠΟΣ<br/>ΟΠΛΟΥ",
                style
            ),

            Paragraph(
                "ΑΡΙΘΜΟΣ<br/>ΟΠΛΟΥ",
                style
            ),
            Paragraph(
                "ΘΕΣΗ ΣΤΟΝ<br/>ΟΠΛΟΒΑΣΤΟ",
                style
            ),
            "ΠΑΡ/ΣΕΙΣ"
        ]

    ]


    aa = 1

    last_type = None
    category_rows = []

    for asm, weapon_type, presence, absent_reason in weapons_data:


        if weapon_type != last_type:

            table_data.append(
                [
                    Paragraph(
                    weapon_type,
                        style
                    ),
                    "",
                    "",
                    "",
                    "",
                    ""
                ]
            )

            category_rows.append(
                len(table_data)-1
            )

            aa = 1

            last_type = weapon_type


        info = st.session_state.personnel.get(
            asm,
            {}
        )


        if presence == "ΑΠΟΝ":
            remarks = absent_reason
        else:
            remarks = "ΠΑΡΟΝ"


        table_data.append(

            [
                Paragraph(str(aa), style),
                Paragraph(info.get("Βαθμός",""), name_style),
                Paragraph(info.get("Ονοματεπώνυμο",""), name_style),
                Paragraph(weapon_type, style),
                Paragraph(info.get("Αριθμός Όπλου",""), style),
                Paragraph(info.get("Θέση Οπλοβαστού",""), style),
                Paragraph(remarks, style)
            ]

        )


        aa += 1

    table = Table(
    table_data,
    colWidths=[
        35,   # Α/Α
        55,   # ΒΑΘΜΟΣ
        135,  # ΟΝΟΜΑΤΕΠΩΝΥΜΟ
        75,   # ΤΥΠΟΣ ΟΠΛΟΥ
        65,   # ΑΡΙΘΜΟΣ ΟΠΛΟΥ
        85,   # ΘΕΣΗ ΟΠΛΟΒΑΣΤΟΥ
        55    # ΠΑΡ/ΣΕΙΣ
    ],
    repeatRows=1
    )

    styles = [

        ("GRID",(0,0),(-1,-1),0.5,None),

        ("ALIGN",(0,0),(-1,-1),"CENTER"),

        ("VALIGN",(0,0),(-1,-1),"MIDDLE")

    ]


    for r in category_rows:

        styles.append(
            ("SPAN",(0,r),(-1,r))
        )

    table.setStyle(
        TableStyle(styles)
    )


    elements.append(table)


    elements.append(
        Spacer(1,20)
    )

    sign_table = Table(
        [
            [
                "-Ο-",
                "",
                "-Ο-"
            ],

            [
                "ΑΞΚΟΣ ΟΠΛΙΣΜΟΥ",
                "",
                "ΔΚΤΗΣ ΛΟΧΟΥ"
            ],

            [
                "",
                "",
                ""
            ],

            [
                aksos_oplismou,
                "",
                diktis
            ],

            [
                aksos_oplismou_rank,
                "",
                diktis_rank
            ]

        ],
        colWidths=[180,180,180]
    )


    sign_table.setStyle(
        TableStyle(
            [
                ("ALIGN",(0,0),(-1,-1),"CENTER"),
                ("FONTNAME",(0,0),(-1,-1),PDF_FONT)
            ]
        )
    )


    elements.append(sign_table)


    pdf.build(elements)

def create_absent_weapons_pdf(filename, report_date):

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    def setting(k):
        cur.execute(
            "SELECT value FROM settings WHERE key=?",
            (k,)
        )

        r = cur.fetchone()
    
        return r[0] if r else ""
    
    monada = setting("monada")
    loxos = setting("loxos")
    diktis = setting("diktis")
    diktis_rank = setting("diktis_rank")
    aksos_oplismou = setting("aksos_oplismou")
    aksos_oplismou_rank = setting("aksos_oplismou_rank")
    
    conn.close()
    
    
    pdf = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=25,
        leftMargin=25,
        topMargin=20,
        bottomMargin=20
    )
    
    
    elements = []
    
    
    header_style = ParagraphStyle(
        "weapon_header",
        fontName=PDF_FONT,
        fontSize=8,
        leading=9,
        alignment=TA_LEFT
    )
    
    style = ParagraphStyle(
        "weapon_cell",
        fontName=PDF_FONT,
        fontSize=8,
        leading=9,
        alignment=TA_CENTER
    )
    
    
    title_style = ParagraphStyle(
        "weapon_title",
        fontName=PDF_FONT,
        fontSize=12,
        alignment=TA_CENTER
    )
    
    name_style = ParagraphStyle(
        "weapon_name",
        fontName=PDF_FONT,
        fontSize=8,
        leading=9,
        alignment=TA_CENTER
    )
    
    header = Table(
        [
            [
                "",
                "",
                "",
                Paragraph(monada, header_style)
            ],
            [
                "",
                "",
                "",
                Paragraph(loxos, header_style)
            ],
            [
                "",
                "",
                "",
                Paragraph(report_date.strftime("%d/%m/%Y"), header_style)
            ]
        ],
        colWidths=[150,150,130,90]
    )
    
    
    header.setStyle(
        TableStyle(
            [
                ("ALIGN",(0,0),(-1,-1),"LEFT"),
                ("VALIGN",(0,0),(-1,-1),"TOP")
            ]
        )
    )
    
    
    elements.append(header)
    
    elements.append(
        Spacer(1,15)
    )

    elements.append(
        Paragraph(
            f"<b><u>ΚΑΤΑΣΤΑΣΗ ΑΠΟΝΤΩΝ ΟΠΛΩΝ ΤΗΣ {report_date.strftime('%d/%m/%Y')}</u></b>",
            title_style
        )
    )

    elements.append(
        Spacer(1,15)
    )
    
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    cur.execute(
        """
        SELECT 
            asm,
            weapon_type,                
            presence,
            absent_reason
        FROM weapons
        """
    )
    
    all_weapons_data = cur.fetchall()

    weapons_data = [
        w for w in all_weapons_data
        if w[2] == "ΑΠΟΝ"
    ]

    weapons_data = sorted(
        weapons_data,
        key=lambda x: (
            0 if x[1] == "G3A4" else 1,
                int(
                st.session_state.personnel.get(
                    x[0],
                    {}
                ).get(
                    "Θέση Οπλοβαστού",
                    999
                )
            )
        )
    )
    
    conn.close()
    
    table_data = [
    
        [
            "Α/Α",
            "ΒΑΘΜΟΣ",
            "ΟΝΟΜΑΤΕΠΩΝΥΜΟ",
            Paragraph(
                "ΤΥΠΟΣ<br/>ΟΠΛΟΥ",
                style
            ),
            Paragraph(
                "ΑΡΙΘΜΟΣ<br/>ΟΠΛΟΥ",
                style
            ),
            Paragraph(
                "ΘΕΣΗ ΣΤΟΝ<br/>ΟΠΛΟΒΑΣΤΟ",
                style
            ),
            "ΠΑΡ/ΣΕΙΣ"
        ]

    ]
    
    
    aa = 1
    category_rows = []


    for weapon_type in ["G3A4", "G3A3"]:

        table_data.append(
            [
                Paragraph(
                    weapon_type,
                    style
                ),
                "",
                "",
                "",
                "",
                ""
            ]
        )

        category_rows.append(
            len(table_data)-1
        )

        aa = 1


        for asm, w_type, presence, absent_reason in weapons_data:

            if w_type != weapon_type:
                continue

            info = st.session_state.personnel.get(
                asm,
                {}
            )


            table_data.append(

                [
                    Paragraph(str(aa), style),
                    Paragraph(info.get("Βαθμός",""), name_style),
                    Paragraph(info.get("Ονοματεπώνυμο",""), name_style),
                    Paragraph(w_type, style),
                    Paragraph(info.get("Αριθμός Όπλου",""), style),
                    Paragraph(info.get("Θέση Οπλοβαστού",""), style),
                    Paragraph(absent_reason, style)
                ]

            )


            aa += 1
    
    table = Table(
    table_data,
    colWidths=[
        35,   # Α/Α
        55,   # ΒΑΘΜΟΣ
        135,  # ΟΝΟΜΑΤΕΠΩΝΥΜΟ
        75,   # ΤΥΠΟΣ ΟΠΛΟΥ
        65,   # ΑΡΙΘΜΟΣ ΟΠΛΟΥ
        85,   # ΘΕΣΗ ΟΠΛΟΒΑΣΤΟΥ
        55    # ΠΑΡ/ΣΕΙΣ
    ],
    repeatRows=1
    )
    
    styles = [
    
        ("GRID",(0,0),(-1,-1),0.5,None),
    
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
    
        ("VALIGN",(0,0),(-1,-1),"MIDDLE")
    
    ]

    for r in category_rows:

        styles.append(
            ("SPAN",(0,r),(-1,r))
        )

    table.setStyle(
        TableStyle(styles)
    )    
    
    elements.append(table)
    
    elements.append(
        Spacer(1,20)
    )

    present_g3a4 = 0
    present_g3a3 = 0

    absent_g3a4 = 0
    absent_g3a3 = 0


    for asm, weapon_type, presence, absent_reason in all_weapons_data:

        if weapon_type == "G3A4":

            if presence == "ΠΑΡΟΝ":
                present_g3a4 += 1

            elif presence == "ΑΠΟΝ":
                absent_g3a4 += 1


        elif weapon_type == "G3A3":

            if presence == "ΠΑΡΟΝ":
                present_g3a3 += 1

            elif presence == "ΑΠΟΝ":
                absent_g3a3 += 1


    total_g3a4 = present_g3a4 + absent_g3a4
    total_g3a3 = present_g3a3 + absent_g3a3


    summary_table = Table(

        [
            [
                "",
                "G3A4",
                "G3A3"
            ],

            [
                "ΧΡΕΩΜΕΝΑ ΣΤΟΝ ΘΑΛΑΜΟΦΥΛΑΚΑ",
                str(present_g3a4),
                str(present_g3a3)                ],

            [
                "ΑΠΟΝΤΑ",
                str(absent_g3a4),
                str(absent_g3a3)
            ],

            [
                "ΣΥΝΟΛΟ",
                str(total_g3a4),
                str(total_g3a3)
            ]

        ],

        colWidths=[250,120,120]

    )


    summary_table.setStyle(

        TableStyle(

            [
                ("GRID",(0,0),(-1,-1),0.5,None),
                ("ALIGN",(0,0),(-1,-1),"CENTER"),
                ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
                ("FONTNAME",(0,0),(-1,-1),PDF_FONT)
            ]

        )

    )


    elements.append(summary_table)

    elements.append(
        Spacer(1,20)
    )

    sign_table = Table(
        [
            [
                "-Ο-",
                "",
                "-Ο-"
            ],
    
            [
                "ΑΞΚΟΣ ΟΠΛΙΣΜΟΥ",
                "",
                "ΔΚΤΗΣ ΛΟΧΟΥ"
            ],
    
            [
                "",
                "",
                ""
            ],
    
            [
                aksos_oplismou,
                "",
                diktis
            ],

            [
                aksos_oplismou_rank,
                "",
                diktis_rank
            ]
    
        ],
        colWidths=[180,180,180]
    )
    
    
    sign_table.setStyle(
        TableStyle(
            [
                ("ALIGN",(0,0),(-1,-1),"CENTER"),
                ("FONTNAME",(0,0),(-1,-1),PDF_FONT)
            ]
        )
    )
    
    
    elements.append(sign_table)
    
    
    pdf.build(elements)

def render_registration_form(
        is_admin=False,
        existing_data=None,
        asm_to_edit=None
):

    if existing_data is None:
        existing_data={}


    with st.form(
        key=f"form_{asm_to_edit if asm_to_edit else 'new'}"
    ):


        st.subheader(
            "📋 Στοιχεία Προσωπικού"
        )


        col1,col2=st.columns(2)



        with col1:

            vathmos=st.text_input(
                "Βαθμός",
                value=existing_data.get("Βαθμός","")
            )


            onomatep=st.text_input(
                "Ονοματεπώνυμο",
                value=existing_data.get("Ονοματεπώνυμο","")
            )

            patronymo=st.text_input(
                "Πατρώνυμο",
                value=existing_data.get("Πατρώνυμο","")
            )

            mitronymo=st.text_input(
                "Μητρώνυμο",
                value=existing_data.get("Μητρώνυμο","")
            )

            topos=st.text_input(
                "Τόπος Καταγωγής",
                value=existing_data.get("Τόπος Καταγωγής","")
            )
            
            topos_diamonis=st.text_input(
                "Τόπος Διαμονής",
                value=existing_data.get("Τόπος Διαμονής","")
            )

            til_syggeni=st.text_input(
                "Τηλέφωνα Οικίας – Συγγενών",
                value=existing_data.get("Τηλέφωνο Συγγενή","")
            )

            epaggelma=st.text_input(
                "Επάγγελμα (ως πολίτης)",
                value=existing_data.get("Επάγγελμα (ως πολίτης)","")
            )

            eidikes_gnoseis=st.text_input(
                "Ειδικές Γνώσεις",
                value=existing_data.get("Ειδικές Γνώσεις","")
            )

            grammatikes_gnoseis=st.text_input(
                "Γραμματικές Γνώσεις",
                value=existing_data.get("Γραμματικές Γνώσεις","")
            )

            xenes_glosses=st.text_input(
                "Ξένες Γλώσσες",
                value=existing_data.get("Ξένες Γλώσσες","")
            )

        with col2:


            tilefono=st.text_input(
                "Τηλέφωνο",
                value=existing_data.get("Τηλέφωνο","")
            )


            email=st.text_input(
                "Email",
                value=existing_data.get("Email","")
            )

            typos_oxim=st.text_input(
                "Τύπος Οχήματος",
                value=existing_data.get("Τύπος Οχήματος","")
            )

            vehicle_color=st.text_input(
                "Χρώμα Οχήματος",
                value=existing_data.get("Χρώμα Οχήματος","")
            )

            ar_kykl=st.text_input(
                "Αρ. Κυκλοφορίας",
                value=existing_data.get("Αρ. Κυκλοφορίας","")
            )

            asm=st.text_input(
                "ΑΣΜ",
                value=asm_to_edit if asm_to_edit else ""
            )
            
            imerominia_eisodou=st.date_input(
                "Ημερομηνία Εισόδου στη Μονάδα",
                value=datetime.now()
            )           
            
            katastasi_ygeias=st.text_input(
                "Κατάσταση Υγείας",
                value=existing_data.get("Κατάσταση Υγείας","")
            )
                        
            oikogeneiaki_katastasi=st.text_input(
                "Οικογενειακή Κατάσταση",
                value=existing_data.get("Οικογενειακή Κατάσταση","")
            )
                    
            oikonomiki_katastasi=st.text_input(
                "Οικονομική Κατάσταση",
                value=existing_data.get("Οικονομική Κατάσταση","")
            )
                        
            idiaitera_problimata=st.text_area(
                "Ιδιαίτερα προβλήματα που τον απασχολούν",
                value=existing_data.get("Ιδιαίτερα Προβλήματα","")
            )

        admin_fields={}

        if is_admin:


            st.markdown("---")

            st.subheader(
                "🛡️ Στοιχεία Admin"
            )

            admin_fields["dn"]=st.selectbox(
                "ΔΝ",
                [
                    "ΝΑΙ",
                    "ΟΧΙ"
                ],
                index=0 if existing_data.get("ΔΝ","ΝΑΙ")=="ΝΑΙ" else 1
            )

            kat_i_options = [
                "Ι1",
                "Ι2",
                "Ι3 (ΕΝΟΠΛΟ)",
                "Ι3 (ΑΟΠΛΟ)",
                "Ι4"
            ]


            admin_fields["kat_i"] = st.selectbox(
                "Κατηγορία Ι",
                kat_i_options,
                index=(
                    kat_i_options.index(existing_data.get("Κατηγορία Ι"))
                    if existing_data.get("Κατηγορία Ι") in kat_i_options
                    else 0
                )
            )


            admin_fields["enoplos"]=st.selectbox(
                "Ένοπλος/Άοπλος",
                [
                    "ΕΝΟΠΛΟΣ",
                    "ΑΟΠΛΟΣ"
                ],
                index=0 if existing_data.get("Ένοπλος/Άοπλος","ΕΝΟΠΛΟΣ")=="ΕΝΟΠΛΟΣ" else 1
            )


            admin_fields["ar_oplou"]=st.text_input(
                "Αριθμός Όπλου",
                value=existing_data.get("Αριθμός Όπλου","")
            )


            admin_fields["thesi_opli"]=st.text_input(
                "Θέση Οπλοβαστού",
                value=existing_data.get("Θέση Οπλοβαστού","")
            )


            dria_options = [
                "1η",
                "2η",
                "3η",
                "4η"
            ]


            admin_fields["dria"] = st.selectbox(
                "ΔΡΙΑ",
                dria_options,
                index=(
                    dria_options.index(existing_data.get("ΔΡΙΑ"))
                    if existing_data.get("ΔΡΙΑ") in dria_options
                    else 0
                )
            )


            omada_options = [
                "1η",
                "2η",
                "3η"
            ]


            admin_fields["omada"] = st.selectbox(
                "Ομάδα",
                omada_options,
                index=(
                    omada_options.index(existing_data.get("Ομάδα"))
                    if existing_data.get("Ομάδα") in omada_options
                    else 0
                )
            )


            admin_fields["paratiriseis"]=st.selectbox(
                "Παρατηρήσεις",
                [
                    "",
                    "Β. Δρίτη",
                    "Ομαδάρχης"
                ],
                index=(
                    [
                        "",
                        "Β. Δρίτη",
                        "Ομαδάρχης"
                    ].index(existing_data.get("Παρατηρήσεις",""))
                    if existing_data.get("Παρατηρήσεις","") in [
                        "",
                        "Β. Δρίτη",
                        "Ομαδάρχης"
                    ]
                    else 0
                )
            )



        submit=st.form_submit_button(
            "💾 Αποθήκευση"
        )



        if submit:


            target_asm = asm


            if not target_asm or not onomatep:

                st.error(
                    "ΑΣΜ και Ονοματεπώνυμο υποχρεωτικά"
                )

                return



            data={

                "Βαθμός":vathmos,

                "Ονοματεπώνυμο":onomatep,

                "Πατρώνυμο":patronymo,

                "Μητρώνυμο":mitronymo,

                "Τόπος Καταγωγής":topos,

                "Τόπος Διαμονής":topos_diamonis,

                "Επάγγελμα (ως πολίτης)":epaggelma,

                "Ειδικές Γνώσεις":eidikes_gnoseis,

                "Γραμματικές Γνώσεις":grammatikes_gnoseis,

                "Ξένες Γλώσσες":xenes_glosses,

                "Ημερομηνία Εισόδου στη Μονάδα":str(imerominia_eisodou),

                "Κατάσταση Υγείας":katastasi_ygeias,

                "Οικογενειακή Κατάσταση":oikogeneiaki_katastasi,

                "Οικονομική Κατάσταση":oikonomiki_katastasi,

                "Ιδιαίτερα Προβλήματα":idiaitera_problimata,

                "Τηλέφωνο":tilefono,

                "Email":email,

                "Τηλέφωνο Συγγενή":til_syggeni,

                "Τύπος Οχήματος":typos_oxim,

                "Χρώμα Οχήματος":vehicle_color,

                "Αρ. Κυκλοφορίας":ar_kykl,

                "ΔΝ":admin_fields.get("dn",""),

                "Κατηγορία Ι":admin_fields.get("kat_i",""),

                "Ένοπλος/Άοπλος":admin_fields.get("enoplos",""),

                "Αριθμός Όπλου":admin_fields.get("ar_oplou",""),

                "Θέση Οπλοβαστού":admin_fields.get("thesi_opli",""),

                "ΔΡΙΑ":admin_fields.get("dria",""),

                "Ομάδα":admin_fields.get("omada",""),

                "Παρατηρήσεις":admin_fields.get("paratiriseis","")

            }

            if asm_to_edit and asm_to_edit != target_asm:

                # μεταφορά υπηρεσιών αν υπάρχουν
                conn=sqlite3.connect(DB_NAME)
                cur=conn.cursor()

                cur.execute(
                    """
                    UPDATE duties
                    SET asm=?
                    WHERE asm=?
                    """,
                    (
                        target_asm,
                        asm_to_edit
                    )
                )

                cur.execute(
                    """
                    DELETE FROM weapons
                    WHERE asm=?
                    """,
                    (
                        target_asm,
                    )
                )


                cur.execute(
                    """
                    UPDATE weapons
                    SET asm=?
                    WHERE asm=?
                    """,
                    (
                        target_asm,
                        asm_to_edit
                    )
                )

                cur.execute(
                    """
                    DELETE FROM personnel
                    WHERE asm=?
                    """,
                    (
                        asm_to_edit,
                    )
                )


                conn.commit()
                conn.close()


                st.session_state.personnel[target_asm] = data

                if asm_to_edit != target_asm:
                    del st.session_state.personnel[asm_to_edit]

            st.session_state.personnel[target_asm]=data


            save_personnel(
                target_asm,
                data
            )


            st.success(
                "Η καταχώρηση ολοκληρώθηκε"
            )


            st.session_state.edit_asm=None


            st.rerun()
            # =========================
# LOGIN
# =========================


st.sidebar.title(
    "🪖 Μενού"
)


role=st.sidebar.radio(
    "Σύνδεση:",
    [
        "Απλός Χρήστης",
        "Διαχειριστής (Admin)"
    ]
)


is_admin=False



if role=="Διαχειριστής (Admin)":


    username=st.sidebar.text_input(
        "Username"
    )


    password=st.sidebar.text_input(
        "Password",
        type="password"
    )


    if username=="admin" and password=="1234":

        is_admin=True

        st.sidebar.success(
            "Συνδεθήκατε"
        )


    elif username or password:

        st.sidebar.error(
            "Λάθος στοιχεία"
        )



# =========================
# ΑΠΛΟΣ ΧΡΗΣΤΗΣ
# =========================


if role=="Απλός Χρήστης":


    st.title(
        "📝 Καταχώρηση Στοιχείων"
    )


    render_registration_form(
        False
    )


    st.markdown("---")


    st.subheader(
        "📅 Υπηρεσίες"
    )


    if st.session_state.duties:


        date=st.date_input(
            "Ημερομηνία",
            datetime.now()
        )


        key=str(date)


        if key in st.session_state.duties:


            rows=[]


            for asm,duty in st.session_state.duties[key].items():


                info=st.session_state.personnel.get(
                    asm,
                    {}
                )


                rows.append({

                    "Βαθμός":info.get("Βαθμός",""),

                    "Ονοματεπώνυμο":info.get("Ονοματεπώνυμο",""),

                    "Υπηρεσία":duty

                })


            st.table(
                pd.DataFrame(rows)
            )




# =========================
# ADMIN
# =========================


elif role=="Διαχειριστής (Admin)" and is_admin:


    st.title(
        "🛡️ Πίνακας Admin"
    )


    tabs=st.tabs(
        [
            "👥 Προσωπικό",
            "📅 Αναθέσεις",
            "📊 Καταστάσεις",
            "🎯 Όπλα",
            "⚙️ Ρυθμίσεις",
            "🛠️ Ρυθμίσεις Υπηρεσιών/Αναθέσεων",
            "🔎 Επιθεωρήσεις"
        ]
    )



    with tabs[0]:


        st.subheader(
            "Προσωπικό"
        )


        render_registration_form(
            True,
            st.session_state.personnel.get(
                st.session_state.edit_asm,
                {}
            ),
            st.session_state.edit_asm
        )


        if st.session_state.personnel:


            # ΠΛΗΡΗΣ ΛΙΣΤΑ ΠΡΟΣΩΠΙΚΟΥ

            df=pd.DataFrame.from_dict(
            st.session_state.personnel,
            orient="index"
            )


            df.insert(
                0,
                "ΑΣΜ",
                df.index
            )


            st.dataframe(
                df,
                use_container_width=True
            )


            st.markdown("---")

            st.subheader("✏️ Επεξεργασία / 🗑️ Διαγραφή")


            # ΕΠΙΛΟΓΗ ΑΤΟΜΟΥ

            personnel_choices = {
                f"{info.get('Βαθμός','')} {info.get('Ονοματεπώνυμο','')}": asm
                for asm, info in st.session_state.personnel.items()
            }


            selected_name = st.selectbox(
                "Επιλέξτε Προσωπικό",
                list(personnel_choices.keys())
            )


            selected_asm = personnel_choices[selected_name]


            col1,col2 = st.columns(2)


            with col1:

                if st.button(
                    "✏️ Επεξεργασία"
                ):

                    st.session_state.edit_asm = selected_asm

                    st.rerun()



            with col2:

                if st.button(
                    "🗑️ Διαγραφή"
                ):


                    del st.session_state.personnel[selected_asm]


                    conn=sqlite3.connect(DB_NAME)

                    cur=conn.cursor()

                    cur.execute(
                        "DELETE FROM personnel WHERE asm=?",
                        (selected_asm,)
                    )


                    conn.commit()

                    conn.close()


                    st.success(
                        "Η διαγραφή ολοκληρώθηκε"
                    )


                    st.rerun()

        # ==========================
        # ΕΚΔΟΣΗ ΚΑΡΤΕΛΑΣ ΣΥΝΕΝΤΕΥΞΗΣ
        # ==========================

        st.subheader("📄 Καρτέλα Συνέντευξης")


        persons = []

        for asm, data in st.session_state.personnel.items():

            name = data.get("Ονοματεπώνυμο","")

            if name:
                persons.append(
                    (name, asm)
                )


        persons = sorted(
            persons,
            key=lambda x: x[0]
        )


        if persons:

            selected_person = st.selectbox(
                "Επιλέξτε άτομο",
                persons,
                format_func=lambda x: x[0]
            )


            if st.button(
                "📄 Δημιουργία Καρτέλας Συνέντευξης",
                key="create_interview_pdf"
            ):

                name = selected_person[0]
                asm = selected_person[1]


                person_info = st.session_state.personnel.get(
                    asm,
                    {}
                )


                filename = (
                    f"ΣΥΝΤΕΝΤΕΥΞΗ_{name}.pdf"
                )


                create_interview_pdf(
                    filename,
                    asm,
                    person_info
                )


                with open(filename,"rb") as f:

                    st.download_button(
                        "⬇️ Λήψη PDF",
                        f,
                        file_name=filename,
                        key="download_interview_pdf"
                    )


        else:

            st.info(
                "Δεν υπάρχουν καταχωρημένα άτομα"
            )

        if st.button("🚗 Δελτία Εισόδου Οχημάτων"):

            filename = "deltia_eisodou_oximaton.pdf"

            create_vehicle_passes_pdf(filename)

            with open(filename, "rb") as f:

                st.download_button(
                    "📥 Λήψη Δελτίων Εισόδου Οχημάτων",
                    f,
                    file_name=filename,
                    mime="application/pdf"
                )        
            
    with tabs[1]:

        st.subheader(
            "📅 Ανάθεση Υπηρεσιών"
        )


        selected_date=st.date_input(
            "Ημερομηνία",
            datetime.now(),
            key="service_date"
        )


        date_key=str(selected_date)



        if date_key not in st.session_state.duties:

            st.session_state.duties[date_key]={}



        available={}


        for asm,info in st.session_state.personnel.items():

            if asm not in st.session_state.duties[date_key]:

                available[asm]=(
                    f"{info.get('Βαθμός','')} "
                    f"{info.get('Ονοματεπώνυμο','')}"
                )

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("""
        SELECT
            name,
            short_name
        FROM special_status_types
        ORDER BY name
        """)

        special_statuses = cur.fetchall()

        conn.close()

        available_services = get_services()

        selected_duty = st.selectbox(
            "Υπηρεσία",
            ["-- Επιλογή --"] + available_services
        )

        selected_special = st.selectbox(
            "Ειδική Κατάσταση",
            ["-- Καμία --"] +
            [s[0] for s in special_statuses]
        )

        selected_person=st.selectbox(
            "Στέλεχος",
            ["-- Επιλογή --"]+
            list(available.keys()),
            format_func=lambda x:
            available.get(x,x)
        )



        if st.button(
            "➕ Καταχώρηση Ανάθεσης"
        ):

            if (
                selected_duty != "-- Επιλογή --"
                and
                selected_special != "-- Καμία --"
            ):

                st.error(
                    "Επιλέξτε είτε υπηρεσία είτε ειδική κατάσταση."
                )

            elif (
                selected_duty == "-- Επιλογή --"
                and
                selected_special == "-- Καμία --"
            ):

                st.error(
                    "Επιλέξτε υπηρεσία ή ειδική κατάσταση."
                )

            elif selected_person == "-- Επιλογή --":
                st.error(
                    "Επιλέξτε στέλεχος."
                )

            elif selected_person in st.session_state.duties[date_key]:

                st.error(
                    "Το στέλεχος έχει ήδη υπηρεσία για αυτή την ημέρα."
                )

            elif (
                selected_duty != "-- Επιλογή --"
                and
                selected_duty in st.session_state.duties[date_key].values()
            ):

                st.error(
                    "Η υπηρεσία έχει ήδη ανατεθεί."
                )

            else:

                assigned_value = (
                    selected_special
                    if selected_special != "-- Καμία --"
                    else selected_duty
                )

                st.session_state.duties[date_key][selected_person] = assigned_value

                save_duty(
                    date_key,
                    selected_person,
                    assigned_value
                )

                st.success(
                    "Η ανάθεση ολοκληρώθηκε."
                )

                st.rerun()

        st.divider()

        st.subheader(
            "✏️ Τροποποίηση Αναθέσεων Ημέρας"
        )


        current_duties = st.session_state.duties.get(
            date_key,
            {}
        )


        if current_duties:

            edit_person = st.selectbox(
                "Επιλέξτε στέλεχος",
                list(current_duties.keys()),
                format_func=lambda x:
                f"{st.session_state.personnel[x].get('Βαθμός','')} {st.session_state.personnel[x].get('Ονοματεπώνυμο','')}",
                key="edit_person"
            )


            old_duty = current_duties[edit_person]

            available_services = get_services()

            special_names = [
                s[0]
                for s in special_statuses
            ]

            is_special = old_duty in special_names

            new_duty = st.selectbox(
    "Νέα υπηρεσία",
    ["-- Επιλογή --"] + available_services,
    index=(
        available_services.index(old_duty) + 1
        if old_duty in available_services
        else 0
    ),
    key="new_duty"
)

            new_special = st.selectbox(
                "Νέα Ειδική Κατάσταση",
                ["-- Καμία --"] + special_names,
                index=(
                    special_names.index(old_duty) + 1
                    if is_special
                    else 0
                ),
                key="new_special"
            )


            col1, col2 = st.columns(2)


            with col1:

                if st.button(
                    "💾 Αποθήκευση Τροποποίησης"
                ):

                    if (
                        new_duty != "-- Επιλογή --"
                        and
                        new_special != "-- Καμία --"
                    ):

                        st.error(
                            "Επιλέξτε είτε υπηρεσία είτε ειδική κατάσταση."
                        )

                    elif (
                        new_duty == "-- Επιλογή --"
                        and
                        new_special == "-- Καμία --"
                    ):

                        st.error(
                            "Δεν επιλέχθηκε ανάθεση."
                        )

                    else:

                        assigned_value = (
                            new_special
                            if new_special != "-- Καμία --"
                            else new_duty
                        )

                        st.session_state.duties[date_key][edit_person] = assigned_value

                        save_duty(
                            date_key,
                            edit_person,
                            assigned_value
                        )

                        st.success(
                            "Η ανάθεση τροποποιήθηκε."
                        )

                        st.rerun()

            with col2:

                if st.button(
                    "🗑️ Διαγραφή Ανάθεσης"
                ):

                    del st.session_state.duties[date_key][edit_person]

                    delete_duty(
                        date_key,
                        edit_person
                    )

                    st.success(
                        "Η ανάθεση διαγράφηκε."
                    )

                    st.rerun()


        else:

            st.info(
                "Δεν υπάρχουν αναθέσεις για την επιλεγμένη ημέρα."
            )

    with tabs[2]:

        st.subheader(
            "📊 Καταστάσεις"
        )

        st.markdown("---")

        st.subheader(
            "📅 Μηνιαίος Έλεγχος Υπηρεσιών"
        )

        col1, col2 = st.columns(2)

        with col1:

            selected_month = st.selectbox(
                "Μήνας",
                list(range(1,13)),
                format_func=lambda x: [
                    "",
                    "Ιανουάριος",
                    "Φεβρουάριος",
                    "Μάρτιος",
                    "Απρίλιος",
                    "Μάιος",
                    "Ιούνιος",
                    "Ιούλιος",
                    "Αύγουστος",
                    "Σεπτέμβριος",
                    "Οκτώβριος",
                    "Νοέμβριος",
                    "Δεκέμβριος"
                ][x]
            )

        with col2:

            selected_year = st.number_input(
                "Έτος",
                min_value=2024,
                max_value=2100,
                value=datetime.now().year
            )


        if st.button(
            "📊 Δημιουργία Μηνιαίου Ελέγχου Υπηρεσιών"
        ):

            month_names = {
                1:"ΙΑΝΟΥΑΡΙΟΥ",
                2:"ΦΕΒΡΟΥΑΡΙΟΥ",
                3:"ΜΑΡΤΙΟΥ",
                4:"ΑΠΡΙΛΙΟΥ",
                5:"ΜΑΙΟΥ",
                6:"ΙΟΥΝΙΟΥ",
                7:"ΙΟΥΛΙΟΥ",
                8:"ΑΥΓΟΥΣΤΟΥ",
                9:"ΣΕΠΤΕΜΒΡΙΟΥ",
                10:"ΟΚΤΩΒΡΙΟΥ",
                11:"ΝΟΕΜΒΡΙΟΥ",
                12:"ΔΕΚΕΜΒΡΙΟΥ"
            }


            pdf_filename = (
                f"ΕΛΕΓΧΟΣ_ΥΠΗΡΕΣΙΩΝ_"
                f"{month_names[selected_month]}_"
                f"{selected_year}.pdf"
            )


            create_monthly_service_report_pdf(
                pdf_filename,
                selected_month,
                selected_year
            )


            with open(
                pdf_filename,
                "rb"
            ) as f:

                st.download_button(
                    "⬇️ Λήψη Μηνιαίου Ελέγχου",
                    f,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )


        st.subheader(
            "📄 Κατάσταση Υπηρεσιών"
        )

        report_date = st.date_input(
                    "Ημερομηνία Κατάστασης Υπηρεσιών",
                    datetime.now()
                )

        if st.button(
            "📄 Δημιουργία Κατάστασης Υπηρεσιών PDF"
        ):

            pdf_filename = (
                f"ΚΑΤΑΣΤΑΣΗ_ΥΠΗΡΕΣΙΩΝ_"
                f"{report_date.strftime('%d_%m_%y')}.pdf"
            )


            create_service_pdf(
                pdf_filename,
                report_date
            )


            with open(
                pdf_filename,
                "rb"
            ) as f:

                st.download_button(
                    "⬇️ Λήψη Κατάστασης Υπηρεσιών",
                    f,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )



        st.markdown("---")


        st.subheader(
            "🏠 Κατάσταση Θαλαμιζομένων"
        )


        thal_report_date = st.date_input(
            "Ημερομηνία Κατάστασης Θαλαμιζομένων",
            datetime.now(),
            key="thal_report_date"
        )



        if st.button(
            "📄 Δημιουργία Κατάστασης Θαλαμιζομένων PDF"
        ):


            pdf_filename = (
                f"ΚΑΤΑΣΤΑΣΗ_ΘΑΛΑΜΙΖΟΜΕΝΩΝ_"
                f"{thal_report_date.strftime('%d_%m_%y')}.pdf"
            )


            create_thalamizomenon_pdf(
                pdf_filename,
                thal_report_date
            )


            with open(
                pdf_filename,
                "rb"
            ) as f:


                st.download_button(
                    "⬇️ Λήψη Κατάστασης Θαλαμιζομένων",
                    f,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )

                st.markdown("---")

        st.subheader(
            "🌙 Κατάσταση Διανυκτερεύσεων"
        )


        dian_report_date = st.date_input(
            "Ημερομηνία Κατάστασης Διανυκτερεύσεων",
            datetime.now(),
            key="dian_report_date"
        )


        if st.button(
            "📄 Δημιουργία Κατάστασης Διανυκτερεύσεων PDF"
        ):


            pdf_filename = (
                f"ΚΑΤΑΣΤΑΣΗ_ΔΙΑΝΥΚΤΕΡΕΥΣΕΩΝ_"
                f"{dian_report_date.strftime('%d_%m_%y')}.pdf"
            )


            create_dianykterefseon_pdf(
                pdf_filename,
                dian_report_date
            )


            with open(
                pdf_filename,
                "rb"
            ) as f:


                st.download_button(
                    "⬇️ Λήψη Κατάστασης Διανυκτερεύσεων",
                    f,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )

        st.subheader(
            "🚶 Κατάσταση Εξοδούχων"
        )


        exod_report_date = st.date_input(
            "Ημερομηνία Κατάστασης Εξοδούχων",
            datetime.now(),
            key="exod_report_date"
        )


        if st.button(
            "📄 Δημιουργία Κατάστασης Εξοδούχων PDF"
        ):

            pdf_filename = (
                f"ΚΑΤΑΣΤΑΣΗ_ΕΞΟΔΟΥΧΩΝ_"
                f"{exod_report_date.strftime('%d_%m_%y')}.pdf"
            )


            create_exodouxon_pdf(
                pdf_filename,
                exod_report_date
            )


            with open(
                pdf_filename,
                "rb"
            ) as f:

                st.download_button(
                    "⬇️ Λήψη Κατάστασης Εξοδούχων",
                    f,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )

    with tabs[4]:


        st.subheader(
            "⚙️ Ρυθμίσεις Εκτύπωσης"
        )


        conn=sqlite3.connect(DB_NAME)

        cur=conn.cursor()



        def get_setting(k):

            cur.execute(
                "SELECT value FROM settings WHERE key=?",
                (k,)
            )

            result=cur.fetchone()

            return result[0] if result else ""



        monada=get_setting("monada")

        loxos=get_setting("loxos")

        alxias=get_setting("alxias")

        diktis=get_setting("diktis")

        alxias_rank=get_setting("alxias_rank")

        diktis_rank=get_setting("diktis_rank")

        aksos_oplismou=get_setting("aksos_oplismou")

        aksos_oplismou_rank=get_setting("aksos_oplismou_rank")

        aksos_imatismou=get_setting("aksos_imatismou")

        aksos_imatismou_rank=get_setting("aksos_imatismou_rank")

        ypxkos_kiniseos=get_setting("ypxkos_kiniseos")

        ypxkos_kiniseos_rank=get_setting("ypxkos_kiniseos_rank")

        diktis_monadas=get_setting("diktis_monadas")

        diktis_monadas_rank=get_setting("diktis_monadas_rank")

        stratopedo_tel=get_setting("stratopedo_tel")

        new_monada=st.text_input(
            "Μονάδα",
            monada
        )


        new_loxos=st.text_input(
            "Λόχος",
            loxos
        )


        new_alxias=st.text_input(
            "Αλχίας",
            alxias
        )


        new_alxias_rank=st.text_input(
            "Βαθμός Αλχία Λόχου",
            alxias_rank
        )


        new_diktis=st.text_input(
            "Διοικητής",
            diktis
        )


        new_diktis_rank=st.text_input(
            "Βαθμός Δκτή Λόχου",
            diktis_rank
        )

        new_aksos_oplismou=st.text_input(
            "ΑΞΚΟΣ ΟΠΛΙΣΜΟΥ",
            aksos_oplismou
        )


        new_aksos_oplismou_rank=st.text_input(
            "Βαθμός ΑΞΚΟΣ ΟΠΛΙΣΜΟΥ",
            aksos_oplismou_rank
        )

        new_aksos_imatismou=st.text_input(
            "ΑΞΚΟΣ ΙΜΑΤΙΣΜΟΣ",
            aksos_imatismou
        )


        new_aksos_imatismou_rank=st.text_input(
            "Βαθμός ΑΞΚΟΣ ΙΜΑΤΙΣΜΟΥ",
            aksos_imatismou_rank
        )


        new_ypxkos_kiniseos=st.text_input(
            "ΥΠΞΚΟΣ ΚΙΝΗΣΕΩΣ",
            ypxkos_kiniseos
        )


        new_ypxkos_kiniseos_rank=st.text_input(
            "Βαθμός ΥΠΞΚΟΣ ΚΙΝΗΣΕΩΣ",
            ypxkos_kiniseos_rank
        )

        new_diktis_monadas=st.text_input(
            "ΔΚΤΗΣ ΜΟΝΑΔΑΣ",
            diktis_monadas
        )


        new_diktis_monadas_rank=st.text_input(
            "Βαθμός ΔΚΤΗ ΜΟΝΑΔΑΣ",
            diktis_monadas_rank
        )

        uploaded_emblem = st.file_uploader(
            "Ανέβασμα Εμβλήματος Σχηματισμού",
            type=["png", "jpg", "jpeg"]
        )


        if uploaded_emblem:

            st.session_state["new_emblem"] = uploaded_emblem

        # Διαγραφή υπάρχοντος εμβλήματος
        emblem_current = get_setting("emblem")

        if emblem_current:

            if st.button("🗑️ Διαγραφή Εμβλήματος"):

                if os.path.exists(emblem_current):
                    os.remove(emblem_current)

                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()

                cur.execute(
                    """
                    UPDATE settings
                    SET value=''
                    WHERE key='emblem'
                    """
                )

                conn.commit()
                conn.close()

                st.session_state.pop("new_emblem", None)

                st.success("Το έμβλημα διαγράφηκε")
                st.rerun()

        new_stratopedo_tel = st.text_input(
            "Τηλέφωνο Στρατοπέδου",
            stratopedo_tel
        )

        conn.close()

        if st.button(
            "💾 Αποθήκευση Ρυθμίσεων"
        ):


            conn=sqlite3.connect(DB_NAME)

            cur=conn.cursor()



            for k,v in [

                ("monada",new_monada),

                ("loxos",new_loxos),

                ("alxias",new_alxias),

                ("alxias_rank",new_alxias_rank),

                ("diktis",new_diktis),

                ("diktis_rank",new_diktis_rank),

                ("aksos_oplismou",new_aksos_oplismou),

                ("aksos_oplismou_rank",new_aksos_oplismou_rank),

                ("aksos_imatismou",new_aksos_imatismou),

                ("aksos_imatismou_rank",new_aksos_imatismou_rank),

                ("ypxkos_kiniseos",new_ypxkos_kiniseos),

                ("ypxkos_kiniseos_rank",new_ypxkos_kiniseos_rank),

                ("diktis_monadas",new_diktis_monadas),

                ("diktis_monadas_rank",new_diktis_monadas_rank),

                ("stratopedo_tel", new_stratopedo_tel),

            ]:


                cur.execute(
                    """
                    UPDATE settings
                    SET value=?
                    WHERE key=?
                    """,
                    (v,k)
                )

            if "new_emblem" in st.session_state:

                os.makedirs(
                    "uploads",
                    exist_ok=True
                )


                emblem_path = os.path.join(
                    "uploads",
                    uploaded_emblem.name
                )


                with open(emblem_path, "wb") as f:
                    f.write(
                        st.session_state["new_emblem"].getbuffer()
                    )


                cur.execute(
                    """
                    UPDATE settings
                    SET value=?
                    WHERE key='emblem'
                    """,
                    (
                        emblem_path,
                    )
                )

            conn.commit()

            conn.close()



            st.success(
                "Οι ρυθμίσεις αποθηκεύτηκαν"
            )

    # =========================
# ΡΥΘΜΙΣΕΙΣ ΥΠΗΡΕΣΙΩΝ
# =========================

    with tabs[5]:

        st.subheader(
            "⚙️ Ρυθμίσεις Υπηρεσιών/Αναθέσεων"
        )

        conn = sqlite3.connect(DB_NAME)

        cur = conn.cursor()


        cur.execute(
            """
            SELECT id, name, short_name, service_times
            FROM services
            ORDER BY id
            """
        )


        services = cur.fetchall()

        conn.close()


        st.subheader("Υπάρχουσες Υπηρεσίες")


        service_names = [
            f"{s[1]} ({s[2]}) - {s[3] or ''}"
            for s in services
        ]


        selected = st.selectbox(
            "Επέλεξε Υπηρεσία",
            service_names
        )


        selected_index = service_names.index(selected)

        selected_service = services[selected_index]


        col1, col2 = st.columns(2)


        with col1:

            if st.button(
                "✏️ Τροποποίηση",
                key="edit_selected_service"
            ):

                st.session_state.edit_service = selected_service

                st.rerun()


        with col2:

            if st.button(
                "🗑️ Διαγραφή",
                key="delete_selected_service"
            ):

                conn = sqlite3.connect(DB_NAME)

                cur = conn.cursor()

                cur.execute(
                    "DELETE FROM services WHERE id=?",
                    (selected_service[0],)
                )

                conn.commit()

                conn.close()

                st.success(
                    "Η υπηρεσία διαγράφηκε"
                )

                st.rerun()

        if "edit_service" in st.session_state:

            service = st.session_state.edit_service

            st.subheader("✏️ Τροποποίηση Υπηρεσίας")

            edit_name = st.text_input(
                "Ονομασία Υπηρεσίας",
                value=service[1]
            )

            edit_short = st.text_input(
                "Σύντομη Ονομασία",
                value=service[2]
            )

            edit_times = st.text_input(
                "Ώρες Υπηρεσίας",
                value=service[3] or ""
            )


            if st.button(
                "💾 Αποθήκευση",
                key="save_edit_service"
            ):

                update_service(
                    service[0],
                    edit_name,
                    edit_short,
                    edit_times
                )

                st.success(
                    "Η υπηρεσία τροποποιήθηκε"
                )

                del st.session_state.edit_service

                st.rerun()

        st.markdown("---")

        st.subheader(
            "➕ Προσθήκη Νέας Υπηρεσίας"
        )

        new_name = st.text_input(
            "Ονομασία Υπηρεσίας"
        )

        new_short_name = st.text_input(
            "Σύντομη Ονομασία"
        )


        col1, col2 = st.columns(2)


        with col1:

            new_times = st.text_input(
    "Ώρες Υπηρεσίας",
    placeholder="πχ 08:00 - 10:00, 14:00 - 16:00, 22:00 - 00:00"
)


        if st.button(
        "💾 Προσθήκη Υπηρεσίας"
        ):
            
            if new_name.strip():

                conn = sqlite3.connect(DB_NAME)

                cur = conn.cursor()


                cur.execute(
                    """
                    INSERT INTO services
                    (name, short_name, service_times)
                    VALUES (?, ?, ?)
                    """,
                    (
                        new_name,
                        new_short_name,
                        new_times
                    )
                )


                conn.commit()

                conn.close()


                st.success(
                    "Η υπηρεσία προστέθηκε"
                )

                st.rerun()


            else:

                st.error(
                    "Συμπληρώστε όνομα υπηρεσίας"
                )     

        st.markdown("---")

        st.subheader(
            "🏥 Ειδικές Καταστάσεις"
        )

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                name,
                short_name,
                stay_inside
            FROM special_status_types
            ORDER BY name
        """)

        specials = cur.fetchall()

        conn.close()

        special_names = [
            f"{s[1]} ({s[2]})"
            for s in specials
        ]

        selected_special = st.selectbox(
            "Επέλεξε Ειδική Κατάσταση",
            special_names,
            key="selected_special_status"
        )

        selected_index = special_names.index(
            selected_special
        )

        selected_special_data = specials[
            selected_index
        ]

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "✏️ Τροποποίηση Ειδικής Κατάστασης"
            ):

                st.session_state.edit_special = (
                    selected_special_data
                )

                st.rerun()

        with col2:

            if st.button(
                "🗑️ Διαγραφή Ειδικής Κατάστασης"
            ):

                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()

                cur.execute(
                    """
                    DELETE FROM special_status_types
                    WHERE id=?
                    """,
                    (
                        selected_special_data[0],
                    )
                )

                conn.commit()
                conn.close()

                st.success(
                    "Η ειδική κατάσταση διαγράφηκε"
                )

                st.rerun()    

        if "edit_special" in st.session_state:

            sp = st.session_state.edit_special

            edit_name = st.text_input(
                "Ονομασία",
                value=sp[1],
                key="edit_special_name"
            )

            edit_short = st.text_input(
                "Συντομογραφία",
                value=sp[2],
                key="edit_special_short"
            )

            edit_stay_inside = st.selectbox(
                "Μένει εντός στρατοπέδου;",
                ["ΝΑΙ", "ΟΧΙ"],
                index=0 if sp[3] == 1 else 1,
                key="edit_special_stay"
            )

            if st.button(
                "💾 Αποθήκευση Ειδικής Κατάστασης"
            ):

                conn = sqlite3.connect(DB_NAME)
                cur = conn.cursor()

                cur.execute(
                    """
                    SELECT id
                    FROM special_status_types
                    WHERE name=?
                    AND id!=?
                    """,
                    (
                        edit_name,
                        sp[0]
                    )
                )

                exists = cur.fetchone()

                if exists:

                    conn.close()

                    st.error(
                        "Υπάρχει ήδη ειδική κατάσταση με αυτό το όνομα."
                    )

                else:

                    cur.execute(
                        """
                        UPDATE special_status_types
                        SET
                            name=?,
                            short_name=?,
                            stay_inside=?
                        WHERE id=?
                        """,
                        (
                            edit_name,
                            edit_short,
                            1 if edit_stay_inside == "ΝΑΙ" else 0,
                            sp[0]
                        )
                    )

                    conn.commit()
                    conn.close()

                    del st.session_state.edit_special

                    st.success(
                        "Η τροποποίηση ολοκληρώθηκε"
                    )

                    st.rerun()

        st.markdown("---")

        st.subheader(
            "➕ Νέα Ειδική Κατάσταση"
        )

        new_special_name = st.text_input(
            "Ονομασία Ειδικής Κατάστασης"
        )

        new_special_short = st.text_input(
            "Συντομογραφία Ειδικής Κατάστασης"
        )

        new_special_stay = st.selectbox(
            "Μένει εντός στρατοπέδου;",
            ["ΝΑΙ", "ΟΧΙ"],
            key="new_special_stay"
        )

        if st.button(
            "💾 Προσθήκη Ειδικής Κατάστασης"
        ):

            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()

            cur.execute(
                """
                SELECT id
                FROM special_status_types
                WHERE name=?
                """,
                (
                    new_special_name,
                )
            )

            exists = cur.fetchone()


            if exists:

                st.error(
                    "Υπάρχει ήδη αυτή η ειδική κατάσταση."
                )

            else:

                cur.execute(
                    """
                    INSERT INTO special_status_types
                    (name, short_name, stay_inside)
                    VALUES (?,?,?)
                    """,
                    (
                        new_special_name,
                        new_special_short,
                        1 if new_special_stay == "ΝΑΙ" else 0
                    )
                )

                conn.commit()

                st.success(
                    "Η ειδική κατάσταση προστέθηκε."
                )

                st.rerun()                      

    with tabs[3]:

        st.subheader("🔫 Διαχείριση Οπλισμού")

        weapon_date = st.date_input(
            "Ημερομηνία",
            datetime.now(),
            key="weapon_date"
        )

        col1, col2 = st.columns(2)

        with col1:

            if st.button(
                "📄 Χρεωμένα Όπλα PDF",
                key="weapons_pdf"
            ):

                filename = (
                    f"ΧΡΕΩΜΕΝΑ_ΟΠΛΑ_"
                    f"{weapon_date.strftime('%d_%m_%y')}.pdf"
                )


                create_weapons_pdf(
                    filename,
                    weapon_date
                )


                with open(
                    filename,
                    "rb"
                ) as f:

                    st.download_button(
                        "⬇️ Λήψη Χρεωμένων Όπλων",
                        f,
                        file_name=filename,
                        mime="application/pdf"
                    )

        with col2:

            if st.button(
                "📄 Απόντος Οπλισμού PDF",
                key="absent_weapons_pdf"
            ):

                filename = (
                    f"ΑΠΟΝΤΑ_ΟΠΛΑ_"
                    f"{weapon_date.strftime('%d_%m_%y')}.pdf"
                )


                create_absent_weapons_pdf(
                    filename,
                    weapon_date
                )


                with open(
                    filename,
                    "rb"
                ) as f:

                    st.download_button(
                        "⬇️ Λήψη Απόντων Όπλων",
                        f,
                        file_name=filename,
                        mime="application/pdf"
                    )

        st.markdown("---")

        st.subheader("Χρεωμένος Οπλισμός")

        def cell_box(text):
            st.markdown(
                f"""
                <div style="
                    border:1px solid #888;
                    padding:6px;
                    height:38px;
                    overflow:hidden;
                    display:flex;
                    align-items:center;
                    white-space:normal;">
                    {text}
                </div>
                """,
                unsafe_allow_html=True
            )

        header1, header2, header3, header4, header5 = st.columns([2,1,1,1,1])

        with header1:
            cell_box("ΟΝΟΜΑΤΕΠΩΝΥΜΟ")

        with header2:
            cell_box("ΤΥΠΟΣ ΟΠΛΟΥ")

        with header3:
            cell_box("ΑΡΙΘΜΟΣ ΟΠΛΟΥ")

        with header4:
            cell_box("ΘΕΣΗ ΟΠΛΟΒΑΣΤΟΥ")

        with header5:
            cell_box("ΠΑΡ/ΣΕΙΣ")

        for asm, info in st.session_state.personnel.items():

            weapon_number = info.get("Αριθμός Όπλου", "").strip()

            if not weapon_number:
                continue

            weapon_status = get_weapon_status(asm)

            saved_weapon_type = weapon_status["weapon_type"]
            saved_presence = weapon_status["presence"]
            saved_reason = weapon_status["absent_reason"]

            col1, col2, col3, col4, col5 = st.columns([2,1,1,1,1], gap="small")


            with col1:
                cell_box(
                    info.get("Ονοματεπώνυμο","")
                )


            with col2:

                if info.get("Βαθμός","") == "ΣΤΡΤΗΣ":

                    weapon_type = "G3A3"
                    cell_box(weapon_type)

                else:

                    weapon_type = st.selectbox(
                        " ",
                        [
                            "G3A3",
                            "G3A4"
                        ],
                        index=0 if saved_weapon_type == "G3A3" else 1,
                        key=f"weapon_type_{asm}"
                    )


                save_weapon_status(
                    asm,
                    weapon_type,
                    st.session_state.get(f"weapon_presence_{asm}", ""),
                    st.session_state.get(f"weapon_absent_reason_{asm}", "")
                )


            with col3:
                cell_box(
                    weapon_number
                )


            with col4:
                cell_box(
                    info.get("Θέση Οπλοβαστού","")
                )


            with col5:

                presence = st.selectbox(
                    " ",
                    [
                        "ΠΑΡΟΝ",
                        "ΑΠΟΝ"
                    ],
                    index=0 if saved_presence == "ΠΑΡΟΝ" else 1,
                    key=f"weapon_presence_{asm}"
                )


                reason = ""


                if presence == "ΑΠΟΝ":

                    reason = st.text_input(
                        " ",
                        value=saved_reason,
                        key=f"weapon_absent_reason_{asm}",
                        placeholder="Που βρίσκεται το όπλο;"
                    )


                save_weapon_status(
                    asm,
                    st.session_state.get(f"weapon_type_{asm}", "G3A3"),
                    presence,
                    reason
                )

    with tabs[6]:

        st.subheader(
            "📄 Επιθεωρήσεις"
        )


        st.write(
            "Επιλέξτε το PDF που θέλετε να εκτυπώσετε:"
        )

        if st.button(
            "🖨️ ΤΑΜΠΕΛΕΣ_ΦΟΡΙΑΜΩΝ"
        ):

            pdf_file = "ΤΑΜΠΕΛΕΣ_ΦΟΡΙΑΜΩΝ.pdf"


            create_tampeles_foriamon_pdf(
                pdf_file
            )


            with open(
                pdf_file,
                "rb"
            ) as f:

                st.download_button(
                    "⬇️ Λήψη ΤΑΜΠΕΛΕΣ_ΦΟΡΙΑΜΩΝ",
                    f,
                    file_name=pdf_file,
                    mime="application/pdf"
                )

        if st.button(
            "🖨️ ΔΕΛΤΙΑ_ΘΕΣΕΩΣ"
        ):

            pdf_file = "ΔΕΛΤΙΑ_ΘΕΣΕΩΣ.pdf"


            create_deltia_theseos_pdf(
                pdf_file
            )


            with open(
                pdf_file,
                "rb"
            ) as f:

                st.download_button(
                    "⬇️ Λήψη ΔΕΛΤΙΑ_ΘΕΣΕΩΣ",
                    f,
                    file_name=pdf_file,
                    mime="application/pdf"
                )


        if st.button(
            "🖨️ ΤΑΜΠΕΛΕΣ_ΣΑΚΟΥ_ΙΜΑΤΙΣΜΟΥ"
        ):

            pdf_file = "ΤΑΜΠΕΛΕΣ_ΣΑΚΟΥ_ΙΜΑΤΙΣΜΟΥ.pdf"


            create_tampeles_sakou_imatismou_pdf(
                pdf_file
            )


            with open(
                pdf_file,
                "rb"
            ) as f:

                st.download_button(
                    "⬇️ Λήψη ΤΑΜΠΕΛΕΣ_ΣΑΚΟΥ_ΙΜΑΤΙΣΜΟΥ",
                    f,
                    file_name=pdf_file,
                    mime="application/pdf"
                )

elif role=="Διαχειριστής (Admin)" and not is_admin:


    st.warning(
        "🔒 Εισάγετε σωστά στοιχεία Admin."
    )