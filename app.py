from flask import Flask, render_template, request, jsonify
import os
import sqlite3 as sql
from dotenv import load_dotenv

load_dotenv()

# app - The flask application where all the magical things are configured.
app = Flask(__name__)

# Constants - Stuff that we need to know that won't ever change!
DATABASE_FILE = os.environ.get('DATABASE_FILE', 'database.db')
DEFAULT_BUGGY_ID = "1"
BUGGY_RACE_SERVER_URL = "https://rhul.buggyrace.net"

#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
    return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
@app.route('/new', methods = ['POST', 'GET']) 
def create_buggy():
    if request.method == 'GET':
        with sql.connect(DATABASE_FILE) as con:
            cur = con.cursor()
            cur.execute("SELECT qty_wheels, flag_color, flag_color_secondary,qty_tyres FROM buggies WHERE id=?", (DEFAULT_BUGGY_ID,))
            result = cur.fetchone()
            if result:
                qty_wheels = result[0]
                flag_color = result[1]
                flag_color_secondary = result[2]
                qty_tyres = result[3]
                return render_template("buggy-form.html", qty_wheels=qty_wheels, flag_color=flag_color, flag_color_secondary=flag_color_secondary, qty_tyres=qty_tyres)
            else:
                return render_template("buggy-form.html")
    elif request.method == 'POST':
        msg=""
        qty_wheels = request.form['qty_wheels']
        qty_tyres = request.form['qty_tyres']
        flag_color = request.form['flag_color']
        flag_color_secondary = request.form['flag_color_secondary']
        flag_pattern = request.form['flag_pattern']
        power_type = request.form['power_type']
        tyres = request.form['tyres']
        armour = request.form['armour']
        attack = request.form['attack']
        algo = request.form['algo']
        special = request.form['special']
        flag_pattern = request.form['flag_pattern']

        if not qty_wheels.isdigit() or not int(qty_wheels)%2 == 0 or int(qty_wheels) == 0:
            qty_wheels_warning = "Quantity of wheels must be an even integer."
            return render_template("buggy-form.html", qty_wheels_warning=qty_wheels_warning, qty_wheels=qty_wheels, qty_tyres=qty_tyres, flag_color=flag_color, flag_color_secondary=flag_color_secondary)

        if not qty_tyres.isdigit() or int(qty_tyres) < int(qty_wheels):
            qty_tyres_warning = "Quantity of tyres must be an integer and more or equal to the number of wheels."
            return render_template("buggy-form.html", qty_tyres_warning=qty_tyres_warning, qty_wheels=qty_wheels, qty_tyres=qty_tyres, flag_color=flag_color, flag_color_secondary=flag_color_secondary)

        power_cost = {
            'bio': 5, 'electric': 20, 'fusion': 400, 'hamster': 3, 'none': 0,
            'petrol': 4, 'rocket': 16, 'solar': 40, 'steam': 3, 'thermo': 300, 'wind': 20
        }.get(power_type, 0)

        tyres_cost = {
            'knobbly': 15, 'maglev': 50, 'reactive': 40, 'slick': 10, 'steelband': 20
        }.get(tyres, 0)

        armour_cost = {
            'aluminium': 200, 'none': 0, 'thicksteel': 200, 'thinsteel': 100, 'titanium': 290, 'wood': 40
        }.get(armour, 0)

        attack_cost = {
            'biohazard': 30, 'charge': 28, 'flame': 20, 'none': 0, 'spike': 5
        }.get(attack, 0)

        special_cost = {
            'antibiotic': 90, 'banging': 42, 'fireproof': 70, 'hamster booster': 5, 'insulated': 100
        }.get(special, 0)

        wheel_cost_percentage = ((int(qty_wheels) - 4) * 0.1) + 1
        if wheel_cost_percentage > 1:
            total_cost = power_cost + tyres_cost + (armour_cost*wheel_cost_percentage) + attack_cost + special_cost
        elif wheel_cost_percentage <= 1:
            total_cost = power_cost + tyres_cost + armour_cost + attack_cost + special_cost

        colors = ["red", "green", "blue", "yellow", "orange", "purple", "pink", "brown", "white", "black", "gray",
                "cyan", "magenta", "lime", "teal", "indigo", "maroon", "navy", "olive", "silver", "gold", "turquoise",
                "coral", "salmon", "ivory", "violet"]

        if flag_color.lower() not in colors:
            flag_color_warning = "Invalid flag color."
            return render_template("buggy-form.html", flag_color_warning=flag_color_warning, qty_wheels=qty_wheels, qty_tyres=qty_tyres, flag_color=flag_color, flag_color_secondary=flag_color_secondary)
        
        if not flag_pattern == "plain" and flag_color.lower() == flag_color_secondary.lower():
            color_combo_warning = "Invalid flag color combination."
            return render_template("buggy-form.html", color_combo_warning=color_combo_warning)
        
        if flag_color_secondary.lower() not in colors:
            flag_color_warning = "Invalid secondary flag color."
            return render_template("buggy-form.html", flag_color_warning=flag_color_warning)
        
        if flag_pattern == "NA" or power_type == "NA" or tyres == "NA" or armour == "NA" or attack == "NA" or algo == "NA" or special == "NA":
            Invalid_data_warning = "Must pick an option!"
            return render_template("buggy-form.html", flag_pattern_warning=Invalid_data_warning if flag_pattern == "NA" else None,
                                                    power_type_warning=Invalid_data_warning if power_type == "NA" else None,
                                                    tyres_warning=Invalid_data_warning if tyres == "NA" else None,
                                                    armour_warning=Invalid_data_warning if armour == "NA" else None,
                                                    attack_warning=Invalid_data_warning if attack == "NA" else None,
                                                    algo_warning=Invalid_data_warning if algo == "NA" else None,
                                                    special_warning=Invalid_data_warning if special == "NA" else None,
                                                    qty_wheels=qty_wheels, qty_tyres=qty_tyres,
                                                    flag_color=flag_color, flag_color_secondary=flag_color_secondary)

        try:
            qty_wheels = int(qty_wheels)
            qty_tyres = int(qty_tyres)
            flag_color = flag_color.upper()
            flag_color_secondary = flag_color_secondary.upper()
            total_cost = round(total_cost, 2)
            with sql.connect(DATABASE_FILE) as con:
                cur = con.cursor()
                cur.execute(
                    "UPDATE buggies SET qty_wheels=?, qty_tyres=?, flag_color=?, flag_color_secondary=?, flag_pattern=?, power_type=?, tyres=?, armour=?, attack=?, special=?, total_cost=? WHERE id=?",
                (qty_wheels, qty_tyres, flag_color, flag_color_secondary, flag_pattern, power_type, tyres, armour, attack, special, total_cost, DEFAULT_BUGGY_ID)
                )
                con.commit()
                msg = "Record successfully saved"
        except:
            con.rollback()
            msg = "error in update operation"
        finally:
            con.close()
        return render_template("updated.html", msg = msg)

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone(); 
    return render_template("buggy.html", buggy = record)

#------------------------------------------------------------
# a placeholder page for editing the buggy: you'll need
# to change this when you tackle task 2-EDIT
#------------------------------------------------------------
@app.route('/edit')
def edit_buggy():
    return render_template("buggy-form.html")
# You probably don't need to edit this... unless you want to ;)
#
#  get JSON from current record
#  This reads the buggy record from the database, turns it
#  into JSON format (excluding any empty values), and returns
#  it. There's no .html template here because it's *only* returning
#  the data, so in effect jsonify() is rendering the data.
#------------------------------------------------------------
@app.route('/json')
def summary():
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))

    buggies = dict(zip([column[0] for column in cur.description], cur.fetchone())).items() 
    return jsonify({ key: val for key, val in buggies if (val != "" and val is not None) })

#------------------------------------------------------------
# a page for displaying the component information
#------------------------------------------------------------
@app.route('/info')
def get_info():
    return render_template("info.html")

# You shouldn't need to add anything below this!
if __name__ == '__main__':
    alloc_port = os.environ.get('CS1999_PORT') or 5000
    app.run(debug=True, host="0.0.0.0", port=alloc_port)
