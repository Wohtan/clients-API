import enum
import flask
from flask import request, render_template, redirect, url_for, flash, session
import sqlite3
from math import ceil

from flask.templating import render_template_string
from functions import *

app = flask.Flask(__name__)

if __name__ == "__main__":
    app.config["DEBUG"] = True

def dict_factory(cursor, row):
    dictionary = {}
    for idx, col in enumerate(cursor.description):
        dictionary[col[0]] = row[idx]
    return dictionary

def get_query_parameters():
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
    return redirect(url_for("api_all"))

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.route('/api/v1/resources/clients/all', methods=['GET','POST'])
def api_all():
    
    # Connection to DB
    conn = sqlite3.connect('clients.db')
    conn.row_factory = dict_factory
    cur = conn.cursor() 

    filter_parameters = []

    # Pagination:
    actual_results_per_page, offset, actual_page = pagination(request,session)

    #Checks if there is an active query on session:
    if "query" in session:
        filtered_results = cur.execute(session["query"] + f"LIMIT {actual_results_per_page} OFFSET {offset};", session["to_filter"]).fetchall()
        results = filtered_results
        rows_number = cur.execute("SELECT COUNT(*)" + session["query"][8:],session["to_filter"]).fetchall()
        rows_number = rows_number[0]["COUNT(*)"] ##Total of rows in the filtered consult

    ##If not filter request was made:
    else:
        results = cur.execute(f'SELECT * FROM clients LIMIT {actual_results_per_page} OFFSET {offset};').fetchall()
        rows_number = cur.execute("SELECT COUNT(*) FROM clients;").fetchall()
        rows_number = rows_number[0]["COUNT(*)"] ##Total of rows in db

    ## Checks if there is a filter request from the form
     
    if request.method == 'POST':
        customer = request.form["customer"]
        country = request.form["country"]
        region = request.form["region"]
        sp = request.form["sp"]
        sh = request.form["sh"] 
        filter_parameters = [customer,country,region,sp,sh]

        # SQL query creation and storage in session
        query,to_filter = create_sql_query(filter_parameters,actual_results_per_page,offset)
        session["query"] = query
        session["to_filter"] = to_filter


        ##Error handler #1:
        if not (customer or country or region or sp or sh):
            flash("No search criteria was given") 
            return redirect(url_for("clear"))  

        filtered_results = cur.execute(query + f"LIMIT {actual_results_per_page} OFFSET {offset};", to_filter).fetchall()

        if filtered_results:
            results = filtered_results
            rows_number = cur.execute("SELECT COUNT(*)" + query[8:],to_filter).fetchall()
            rows_number = rows_number[0]["COUNT(*)"] ##Total of rows in the filtered consult

        ##Error handler #2:         
        else:
            flash("No matches were found")
            return redirect(url_for("clear"))

    
    pages_number = ceil(rows_number / actual_results_per_page)   
    
    return render_template("consult.html", 
    results = results, 
    pages_number = pages_number,
    actual_page = actual_page,
    filter_parameters = filter_parameters)

    conn.close()

##Delete method:

@app.route('/api/v1/resources/clients/clear')
def clear():
    try:
        session.pop("query")
        session.pop("to_filter")
    except:
        flash("Non-active filter request")
    finally:
        return redirect(url_for("api_all"))

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

##Edit form: //This route allows to bring the Client data as a placeholder in the form

@app.route('/api/v1/resources/clients/edit', methods=['GET'])
def edit():
    query_parameters = request.args
    id = query_parameters.get("id")
    query = f"SELECT * from clients where id = {id}"

    conn = sqlite3.connect('clients.db')
    cur = conn.cursor()

    results = cur.execute(query).fetchall()[0]
 
    return render_template ("edit.html", results = results)

##Update action:

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
