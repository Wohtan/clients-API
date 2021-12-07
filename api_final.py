import flask
from flask import request, render_template, redirect, url_for, flash
import sqlite3
from math import ceil

app = flask.Flask(__name__)

if __name__ == "__main__":
    app.config["DEBUG"] = True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_parameters():
    query_parameters = request.args
    customer = query_parameters.get('customer')
    country = query_parameters.get('country')
    region = query_parameters.get('region')
    sp = query_parameters.get('sp')
    sh = query_parameters.get('sh')
    sort = query_parameters.get('sort')
    parameters = [customer,country,region,sp,sh,sort]
    return parameters
   
app.secret_key = "keypass"

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Client Information</h1>
<h2>This API returns basic information about clients</h2>
<p>Here comes the Swagger main info</p>
<p>Page under construction</p>
'''


@app.route('/api/v1/resources/clients/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect('clients.db')
    conn.row_factory = dict_factory
    cur = conn.cursor() 

    ##Results per page and offset:
    per_page = 10
    offset = 0
    rows_number = cur.execute("SELECT COUNT(*) FROM clients;").fetchall()
    rows_number = rows_number[0]["COUNT(*)"]
    pages_number = ceil(rows_number / per_page)

    all_clients = cur.execute(f'SELECT * FROM clients LIMIT {per_page} OFFSET {offset};').fetchall()

    return render_template("consult.html", results = all_clients, pages_number = pages_number )


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

##Get method

@app.route('/api/v1/resources/clients/consult', methods=['GET'])
def api_filter():
    query = "SELECT * FROM clients WHERE"
    to_filter = []
    customer,country,region,sp,sh,sort = get_parameters()

    ##Results per page:
    per_page = 10
    offset = 10 

    if customer:
        query += f' customer LIKE? AND'
        customer = '%' + customer + '%'
        to_filter.append(customer)
    if country:
        query += ' country=? AND'
        to_filter.append(country)
    if region:
        query += ' region=? AND'
        to_filter.append(region)
    if sp:
        query += ' sp=? AND'
        to_filter.append(sp)
    if sh:
        query += ' sh=? AND'
        to_filter.append(sh)
    if sort:
        query = query[:-4] + f' ORDER BY {sort}'
        
    if not (customer or country or region or sp or sh):
        return page_not_found(404)
    
    if query.endswith("AND"):
        query = query[:-4]

    query = query + f" LIMIT {per_page} OFFSET {offset}" 
   
    conn = sqlite3.connect('clients.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    results = cur.execute(query, to_filter).fetchall()
    conn.close()
    if results:
        return render_template("consult.html", results = results)
    else:
        flash("No matches were found")
        return redirect(url_for("api_all"))

##Delete method:

@app.route('/api/v1/resources/clients/delete', methods=['GET','DELETE'])
def api_delete():
    query_parameters = request.args
    id = query_parameters.get("id")
    query = f"DELETE from clients where id = {id}"

    conn = sqlite3.connect('clients.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    name = cur.execute(f"SELECT customer from clients where id = {id}").fetchall()[0]
    cur.execute(query)

    
    flash(f"The customer {name['customer']} has been deleted")

    conn.commit()
    conn.close()

    return redirect(url_for('api_all'))

 #Form render

@app.route('/api/v1/resources/clients/create')
def render_form():
    return render_template("create.html")

#Post method

@app.route('/api/v1/resources/clients/create/added',methods=['POST'])  
def add():
    if request.method == "POST":
        customer = request.form["customer"]
        country = request.form["country"]
        region = request.form["region"]
        sp = request.form["sp"]
        sh = request.form["sh"]        

    conn = sqlite3.connect('clients.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    cur.execute("""INSERT or IGNORE INTO clients 
    (customer,country,region,sp,sh) VALUES (?,?,?,?,?)""",
    (customer,country,region,sp,sh))

    conn.commit()

    cur.execute("SELECT id FROM clients WHERE customer LIKE ?",(customer,))
    id = cur.fetchone()
 
    conn.close()

    flash(f"The client {customer} has been created with ID # {id['id']}")

    return redirect(url_for("api_all"))

##Edit form:

@app.route('/api/v1/resources/clients/edit', methods=['GET'])
def edit():
    query_parameters = request.args
    id = query_parameters.get("id")
    query = f"SELECT * from clients where id = {id}"

    conn = sqlite3.connect('clients.db')
    cur = conn.cursor()

    results = cur.execute(query).fetchall()[0]
 
    print(results)

    return render_template ("edit.html", results = results)

##Update:

@app.route('/api/v1/resources/clients/update', methods = ['GET','POST'])
def update():
    query_parameters = request.args
    id = query_parameters.get("id")

    if request.method == "POST":
        customer = request.form["customer"]
        country = request.form["country"]
        region = request.form["region"]
        sp = request.form["sp"]
        sh = request.form["sh"]  

    query = f"""UPDATE clients
    SET customer = ?, country = ?,
    region = ?, sp = ?, sh = ? WHERE id = {id}"""  

    conn = sqlite3.connect("clients.db")
    cur = conn.cursor()

    cur.execute(query,(customer,country,region,sp,sh))
    conn.commit()

    flash(f"The client {customer} has been sucesfully updated")

    conn.close()
    
    return redirect(url_for('api_all'))

app.run()
