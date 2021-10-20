import flask
from flask import request, jsonify
import sqlite3

app = flask.Flask(__name__)
app.config["DEBUG"] = True

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Client Information</h1>
<p>This API returns basic information about clients</p>'''


@app.route('/api/v1/resources/clients/all', methods=['GET'])
def api_all():
    conn = sqlite3.connect('clients.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()
    all_clients = cur.execute('SELECT * FROM clients;').fetchall()

    return jsonify(all_clients)



@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


@app.route('/api/v1/resources/clients/consult', methods=['GET'])
def api_filter():
    query_parameters = request.args
    print(request.args)
    customer = query_parameters.get('customer')
    country = query_parameters.get('country')
    region = query_parameters.get('region')
    sp = query_parameters.get('sp')
    sh = query_parameters.get('sh')
    sort = query_parameters.get('sort')

    query = "SELECT * FROM clients WHERE"
    to_filter = []

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


    print(query)
    print(to_filter)
    
    conn = sqlite3.connect('clients.db')
    conn.row_factory = dict_factory
    cur = conn.cursor()

    results = cur.execute(query, to_filter).fetchall()


    return jsonify(results)

app.run()
