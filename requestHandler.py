import sqlite3
import cgi

PATH_2_DB = '/main/latlong.db'

## Dispatches HTTP requests to the appropriate handler.
def application(env, start_line):
    if env['REQUEST_METHOD'] == 'POST':   ## add new DB record
        return handle_post(env, start_line)
    elif env['REQUEST_METHOD'] == 'GET':  ## create HTML-fragment report
        return handle_get(start_line)
    else:                                 ## no other option for now
        start_line('405 METHOD NOT ALLOWED', [('Content-Type', 'text/plain')])
        response_body = 'Only POST and GET verbs supported.'
        return [response_body.encode()]                            

def handle_post(env, start_line):    
    form = get_field_storage(env)  ## body of an HTTP POST request
   
    ## Extract fields from POST form.
    region = form.getvalue('region')
    device = form.getvalue('device')
    amount = form.getvalue('amount')
    tstamp = form.getvalue('tstamp')

    ## Missing info?
    if (region is not None and
        device is not None and
        amount is not None and
        tstamp is not None):
        add_record(region, device, amount, tstamp)
        response_body = "POST request handled.\n"
        start_line('201 OK', [('Content-Type', 'text/plain')])
    else:
        response_body = "Missing info in POST request.\n"
        start_line('400 Bad Request', [('Content-Type', 'text/plain')])
 
    return [response_body.encode()]

def handle_get(start_line):
    conn = sqlite3.connect(PATH_2_DB)        ## connect to DB
    cursor = conn.cursor()                   ## get a cursor
    cursor.execute("select * from snowfall")

    response_body = "<h3>Snowfall report</h3><ul>"
    rows = cursor.fetchall()
    for row in rows:
        response_body += "<li>" + str(row[0]) + '|'  ## primary key
        response_body += row[1] + '|'                ## region
        response_body += row[2] + '|'                ## device
        response_body += str(row[3]) + '|'           ## amount
        response_body += str(row[4]) + "</li>"       ## timestamp
    response_body += "</ul>"

    conn.commit()  ## commit
    conn.close()   ## cleanup
   
    start_line('200 OK', [('Content-Type', 'text/html')])
    return [response_body.encode()]

## Add a record from a device to the DB.
def add_record(reg, dev, amt, tstamp):
    conn = sqlite3.connect(PATH_2_DB)      ## connect to DB
    cursor = conn.cursor()                 ## get a cursor

    sql = "INSERT INTO snowfall(region,device,amount,tstamp) values (?,?,?,?)"
    cursor.execute(sql, (reg, dev, amt, tstamp)) ## execute INSERT

    conn.commit()  ## commit
    conn.close()   ## cleanup

def get_field_storage(env):
    input = env['wsgi.input']
    form = env.get('wsgi.post_form')
    if (form is not None and form[0] is input):
        return form[2]

    fs = cgi.FieldStorage(fp = input,
                          environ = env,
                          keep_blank_values = 1)
    return fs
