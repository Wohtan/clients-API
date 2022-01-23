from init import *
from functions import*


app = flask.Flask(__name__)

if __name__ == "__main__":
    app.config["DEBUG"] = True
    app.run()
    
app.secret_key = "keypass"
login_manager = LoginManager(app)
login_manager.login_view = "/api/v1/login"

  
@app.route('/', methods=['GET'])
def home():
    return (redirect(url_for("api_all")))

@app.errorhandler(404)
def page_not_found(e):
    flash("The resource could not be found")
    return (redirect(url_for("api_all"))),404

@app.route('/api/v1/resources/clients/all', methods=['GET','POST'])
def api_all():

   
    # Connection to DB
    conn = sqlite3.connect('clients.db')
    conn.row_factory = dict_factory
    cur = conn.cursor() 

    if "filter_parameters" in session:
        pass
    else:
        session["filter_parameters"] = []

    ## Sort request?
    if "sort_by" in session:
        sort_by = request.args.get("sort_by")
        if sort_by:
            if sort_by == "customer":
                session["sort_by"] = f" ORDER BY CAST(customer as INTEGER)" ##This solves the enumeration 1,10,11 issue 
            else:
                session["sort_by"] = f" ORDER BY {sort_by}"  
    else:
        session["sort_by"] = ""

    # Pagination:
    actual_results_per_page, offset, actual_page = pagination(request,session)

    #Checks if there is an active query on session:
    if "query" in session:
        filtered_results = cur.execute(session["query"] + session["sort_by"] + f" LIMIT {actual_results_per_page} OFFSET {offset} ;" , session["to_filter"]).fetchall()
        
        results = filtered_results
        rows_number = cur.execute("SELECT COUNT(*)" + session["query"][8:],session["to_filter"]).fetchall()
        rows_number = rows_number[0]["COUNT(*)"] ##Total of rows in the filtered consult

    ##If not filter request was made:
    else:
        results = cur.execute(f'SELECT * FROM clients' + session["sort_by"] + f" LIMIT {actual_results_per_page} OFFSET {offset};").fetchall()
        rows_number = cur.execute("SELECT COUNT(*) FROM clients;").fetchall()
        rows_number = rows_number[0]["COUNT(*)"] ##Total of rows in db

    ## Checks if there is a filter request from the form
     
    if request.method == 'POST':
        customer = request.form["customer"]
        country = request.form["country"]
        region = request.form["region"]
        sp = request.form["sp"]
        sh = request.form["sh"] 
        session["filter_parameters"] = [customer,country,region,sp,sh]

        # SQL query creation and storage in session
        query,to_filter = create_sql_query(session["filter_parameters"])
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
    filter_parameters = session["filter_parameters"])

    conn.close()


@app.route('/api/v1/resources/clients/clear')
def clear():
    session.pop("query","")
    session.pop("to_filter","")
    session.pop("sort_by","")
    session.pop("filter_parameters")
    return redirect(url_for("api_all"))

##Delete method:
@app.route('/api/v1/resources/clients/delete', methods=['GET','DELETE'])
@login_required
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

 #Create form render

@app.route('/api/v1/resources/clients/create')
@login_required
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
@login_required
def edit():
    query_parameters = request.args
    id = query_parameters.get("id")
    query = f"SELECT * from clients where id = {id}"

    conn = sqlite3.connect('clients.db')
    cur = conn.cursor()

    results = cur.execute(query).fetchall()[0]

    conn.close() 

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

##Login manager
@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user.id == int(user_id):
            return user
    return None

##Login function:

@app.route('/api/v1/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('api_all'))
    form = LoginForm()
    if form.validate_on_submit():
        user = get_user(form.user.data)
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('api_all')
            return redirect(next_page)
    return render_template('login.html', form=form)

##Logout:
@app.route('/api/v1//logout')
def logout():
    logout_user()
    return redirect(url_for('api_all'))

