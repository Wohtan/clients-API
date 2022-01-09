def create_sql_query(filter_parameters,actual_results_per_page,offset):

    query = "SELECT * FROM clients WHERE"
    to_filter = []
    customer, country, region, sp, sh = filter_parameters

    if customer in filter_parameters:
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
    # TODO: Add the sort function
    # if sort:
    #     query = query[:-4] + f' ORDER BY {sort}'
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
