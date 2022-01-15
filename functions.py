def create_sql_query(filter_parameters):

    query = "SELECT * FROM clients WHERE"
    to_filter = []
    customer, country, region, sp, sh = filter_parameters

    if customer in filter_parameters:
        query += f' customer LIKE? AND'
        customer = '%' + customer + '%'
        to_filter.append(customer)
    if country:
        query += ' country LIKE? AND'
        country = '%' + country + '%'
        to_filter.append(country)
    if region:
        query += ' region LIKE? AND'
        region = '%' + region + '%'
        to_filter.append(region)
    if sp:
        query += ' sp LIKE? AND'
        sp = '%' + sp + '%'
        to_filter.append(sp)
    if sh:
        query += ' sh LIKE? AND'
        sh = '%' + sh + '%'
        to_filter.append(sh)

    if query.endswith("AND"):
        query = query[:-4]

    return query,to_filter

def pagination(request,session):
        ##Results from the template
    query_parameters = request.args
    results_per_page_query = query_parameters.get('rpp')
    actual_page = query_parameters.get('page') 

    # Session code to read the stored value
    if 'results_per_page' in session:
        if results_per_page_query: #If exists the query from the browser, assigns it to the session dict
            session['results_per_page'] = int(results_per_page_query)
    else:
        session['results_per_page'] = 10

    actual_results_per_page = session['results_per_page'] 

    # Assign the actual page value

    if actual_page:
        actual_page = int(actual_page) - 1 ##This '-1' sets the first page offset to zero
    else:
        actual_page = 0

    offset = actual_page * actual_results_per_page

    return actual_results_per_page, offset, actual_page

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